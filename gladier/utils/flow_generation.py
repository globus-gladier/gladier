import logging
import typing
from gladier.base import GladierBaseTool
from gladier.client import GladierBaseClient
from gladier.exc import FlowGenException
from gladier.utils.name_generation import (
    get_compute_flow_state_name,
    get_compute_function_name,
)
from gladier.flow_builder.registry import FlowBuilderRegistry
from gladier.utils.tool_chain import ToolChain


log = logging.getLogger(__name__)


def combine_tool_flows(client: GladierBaseClient, modifiers):
    """
    Combine flow definitions on each of a Gladier Client's **tools** and return
    a single flow definition that runs each state in order from first to last.

    Modifiers can be applied to any of the states within the flow.
    """
    tool_chain = ToolChain(flow_comment=client.__doc__).chain(client.tools)
    flow_definition = tool_chain.flow_definition

    registry = FlowBuilderRegistry()
    for tool in client.tools:
        flow_builder_cls = registry.get_flow_builder_cls_by_tool(
            tool, action_url=modifiers.get("ActionUrl")
        )
        flow_builder = flow_builder_cls(tool)
        flow_definition = flow_builder.apply_modifiers(
            modifiers, flow_definition, strict=True
        )
    return flow_definition


def _get_duplicate_functions(compute_functions: typing.List[callable]):
    tracked_set = set()
    func_names = [get_compute_flow_state_name(f) for f in compute_functions]
    return [f for f in func_names if f in tracked_set or tracked_set.add(f)]


def _fix_old_tools(tool):
    funcx_functions = getattr(tool, "funcx_functions", None)
    compute_functions = getattr(tool, "compute_functions", None)

    if funcx_functions and not compute_functions:
        log.warning(
            f'Tool {tool} defines attributue "funcx_functions" which has now been '
            'changed to "compute_functions". Automatically configuring compute_functions '
            f"for new tool. Please update the old tool {tool}"
        )
        setattr(tool, "compute_functions", funcx_functions)


def generate_tool_flow(tool: GladierBaseTool, modifiers) -> dict:
    """Generate a flow definition for a Gladier Tool based on the defined ``compute_functions``.
    Accepts modifiers for compute functions.

    Returns a complete flow definition for a given tool."""
    _fix_old_tools(tool)

    if not tool.compute_functions:
        raise FlowGenException(
            "Tool has no compute functions. Add a list of python functions "
            f'as "{tool}.compute_functions = [myfunction]" or set a custom flow '
            f"definition instead using `{tool}.flow_definition = mydef`"
        )

    duplicate_functions = _get_duplicate_functions(tool.compute_functions)
    if duplicate_functions:
        raise FlowGenException(
            f"Tool {tool} contains duplicate function names: " f"{duplicate_functions}"
        )

    registry = FlowBuilderRegistry()
    flow_builder_cls = registry.get_flow_builder_cls_by_tool(
        tool, action_url=modifiers.get("ActionUrl")
    )
    flow_builder = flow_builder_cls(tool)
    flow_definition = flow_builder.get_flow_definition()
    flow_builder.apply_modifiers(modifiers, flow_definition, strict=True)
    return flow_definition

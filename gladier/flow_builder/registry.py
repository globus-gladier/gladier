from .flow import FlowBuilder
from gladier.flow_builder.compute import ComputeFlowBuilderv2, ComputeFlowBuilderv3
from gladier.base import GladierBaseTool


class FlowBuilderRegistry:

    """
    The State registry tracks the different kind of states.

    The registry needs to do a couple different kind of lookups.

    During Flow Generation: When a flow definition is created for a tool, modifiers need to be applied to the flow
    generated for the tool itself.

    """

    registered_states = [
        ComputeFlowBuilderv2,
        ComputeFlowBuilderv3,
    ]

    def get_flow_builder_cls_by_tool(
        self, tool: GladierBaseTool = None, action_url: str = None
    ) -> FlowBuilder:
        if tool:
            if getattr(tool, "compute_functions", None) or getattr(
                tool, "funcx_functions", None
            ):
                if (
                    getattr(tool, "action_url", None)
                    == "https://compute.actions.globus.org/v3"
                ):
                    return ComputeFlowBuilderv3
                else:
                    return ComputeFlowBuilderv2

        return FlowBuilder

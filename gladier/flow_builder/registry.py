from .flow import FlowBuilder
from .compute import ComputeFlowBuilderv2, ComputeFlowBuilderv3
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

    def get_state_cls_by_tool(
        self, tool: GladierBaseTool = None, action_url: str = None
    ):
        if tool:
            if tool.compute_functions:
                return ComputeFlowBuilderv2
            else:
                return FlowBuilder

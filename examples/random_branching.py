from gladier.tools.globus import GlobusComputeStep
from gladier.tools.builtins import (
    ChoiceState,
    ChoiceOption,
    ComparisonRule,
    FailState,
    PassState,
)
from gladier import GladierBaseClient, JSONObject


def random_int(high_val: int) -> int:
    from random import randint

    return randint(0, high_val)


def main():
    class RandomComputeStep(GlobusComputeStep):
        high_val: int

        def __init__(self, *args, **kwargs):
            super().__init__(*args, function_to_call=random_int, **kwargs)

        def get_flow_definition(self) -> JSONObject:
            self.set_call_params_from_self_model(["high_val"])
            return super().get_flow_definition()

    random_step = RandomComputeStep(high_val=3)
    choice_state = (
        ChoiceState()
        .choice(
            ChoiceOption(
                rule=ComparisonRule(
                    Variable=random_step.path_to_return_val(), NumericEquals=0.0
                ),
                next=FailState(
                    cause="Random value 0 selected",
                    error="Unluck 0 selected, simulated error",
                ),
            )
        )
        .set_default(PassState())
    )
    random_step.next(choice_state)

    client = GladierBaseClient(start_at=random_step)

    flow_def = client.get_flow_definition()
    print(flow_def)

    flow_run = client.run_flow(
        {"input": {"globus_compute_endpoint": "c844aebf-9a30-4355-8178-82cc0f3d3516"}}
    )
    print(flow_run)


if __name__ == "__main__":
    main()

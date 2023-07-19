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
    random_step = GlobusComputeStep(
        function_to_call=random_int, function_parameters={"high_val": 3}
    )
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
        ))
    choice_state.set_default(PassState(state_name="SuccessfulCompletion"))
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

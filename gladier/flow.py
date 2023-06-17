from __future__ import annotations

import time
import typing as t

from globus_automate_client import FlowsClient, create_flows_client

from .flows_helpers import flow_id_for_flow_def, save_flow_to_cache
from .helpers import JSONObject, eval_jsonpath_for_input
from .state_models import GladierBaseState, GladierStateWithNextOrEnd


class GladierFlowRun:
    def __init__(
        self,
        run_id: str,
        flow_input: t.Optional[JSONObject] = None,
        run_label: t.Optional[str] = None,
        flow_manager: t.Optional[GladierFlow] = None,
        flows_client: t.Optional[FlowsClient] = None,
    ):
        self.run_id = run_id
        self.flow_input = flow_input
        self.run_label = run_label
        self._flows_client = flows_client
        self.flow_manager = flow_manager
        self.last_status: t.Optional[JSONObject] = None

    @property
    def flows_client(self) -> FlowsClient:
        if self._flows_client is not None:
            return self._flows_client
        self._flows_client = create_flows_client()
        return self._flows_client

    def __str__(self) -> str:
        rval = "Run "
        if self.run_label is not None:
            rval += f"'{self.run_label}' "
        rval += f"id {self.run_id}"
        if self.last_status is not None:
            rval += f" status {self.last_status.get('status')}"
        return rval

    def is_complete(self, refresh_status=True) -> bool:
        if refresh_status:
            self.poll_status()
        if self.last_status is not None:
            return self.last_status.get("status") in {"SUCCEEDED", "FAILED"}

    def poll_status(self) -> JSONObject:
        if not self.is_complete(refresh_status=False):
            self.last_status = self.flows_client.flow_action_status(
                self.flow_manager.flow_id, None, self.run_id
            )
        return self.last_status

    def wait_for_completion(
        self,
        max_wait_time: t.Optional[int] = None,
        poll_interval: int = 5,
        poll_callback: t.Optional[t.Callable[[JSONObject], bool]] = None,
    ) -> JSONObject:
        start_time = time.time()
        while not self.is_complete() and (
            max_wait_time is None or start_time + max_wait_time < time.time()
        ):
            if poll_callback is not None:
                if poll_callback(self.last_status):
                    break
            time.sleep(poll_interval)
        return self.last_status

    def globus_web_app_url(self):
        return f"https://app.globus.org/runs/{self.run_id}"


class GladierFlow:
    def __init__(
        self,
        flows_client: t.Optional[FlowsClient] = None,
        flow_id: t.Optional[str] = None,
        start_at: t.Optional[GladierBaseState] = None,
    ):
        self._flows_client = flows_client
        self.start_at: t.Optional[GladierBaseState] = None
        self.flow_id = flow_id
        self.start_at = start_at

    @property
    def flows_client(self) -> FlowsClient:
        if self._flows_client is not None:
            return self._flows_client
        self._flows_client = create_flows_client()
        return self._flows_client

    def set_start_at(self, start_at: GladierBaseState) -> None:
        self.start_at = start_at
        self.flow_id = None

    def set_state_list(self, states: t.List[GladierStateWithNextOrEnd]) -> None:
        """
        Set the states of the Flow based on a sequential list of states. Each state
        in the list *must* implement the next() method. This will change the states by
        setting next in order.
        """
        prev_state: t.Optional[GladierStateWithNextOrEnd] = None
        for state in states:
            if prev_state is not None:
                prev_state.next(state)
            else:
                self.set_start_at(state)
            prev_state = state

    def get_flow_definition(self) -> JSONObject:
        if self.start_at is None:
            raise ValueError(
                "A root state must be set on the flow prior to flow generation"
            )
        else:
            return self.start_at.get_flow_definition()

    def get_default_flow_title(self) -> str:
        flow_def = self.get_flow_definition()
        return f"A Flow Starting at {flow_def['StartAt']}"

    def get_default_run_label(self) -> str:
        return f"A run of flow {self.flow_id}"

    def get_id_for_flow(
        self, deploy_if_required=True, title_for_deploy: t.Optional[str] = None
    ) -> t.Optional[str]:
        if self.flow_id is not None:
            return self.flow_id
        flow_def = self.get_flow_definition()
        if title_for_deploy is None:
            title_for_deploy = self.get_default_flow_title()
        cached_id = flow_id_for_flow_def(flow_def, title_for_deploy)
        if cached_id is not None:
            self.flow_id = cached_id
        elif deploy_if_required:
            self.flow_id = self.deploy_flow(title_for_deploy)
        return self.flow_id

    def deploy_flow(self, title: str) -> t.Optional[str]:
        flow_def = self.get_flow_definition()
        cached_id = flow_id_for_flow_def(flow_def, title)
        if cached_id is not None:
            self.flow_id = cached_id
            return cached_id
        deployed_flow = self.flows_client.deploy_flow(flow_def, title, input_schema={})
        self.flow_id = deployed_flow["id"]
        save_flow_to_cache(flow_def, title, self.flow_id)
        return self.flow_id

    def traverse_flow(self, callback: t.Callable[[GladierBaseState], None]) -> None:
        to_visit = [self.start_at]
        have_visited: t.List[GladierBaseState] = []
        while len(to_visit) > 0:
            next_to_visit = to_visit.pop(0)
            if next_to_visit is not None:  # Make type checker happy, but shouldn't be
                # possible
                callback(next_to_visit)
                have_visited.append(next_to_visit)
                nexts_children = next_to_visit.get_child_states()
                to_visit += [ch for ch in nexts_children if ch not in have_visited]
        return

    def get_all_additional_scopes_for_input(self, flow_input: JSONObject) -> t.Set[str]:
        additional_scopes: t.Set[str] = set()

        def accumulate_additional_scopes(state: GladierBaseState) -> None:
            additional_scopes.update(state.get_additional_scopes_for_input(flow_input))

        self.traverse_flow(accumulate_additional_scopes)
        return additional_scopes

    def run_flow(
        self,
        flow_input: JSONObject,
        run_label: t.Optional[str] = None,
        tags: t.Optional[t.List[str]] = None,
    ) -> GladierFlowRun:
        if self.flow_id is None:
            raise ValueError("A flow id must be set prior to a run")
        if run_label is None:
            run_label = self.get_default_run_label()

        flow_scope = self.flows_client.scope_for_flow(self.flow_id)
        additional_scopes = self.get_all_additional_scopes_for_input(flow_input)
        if additional_scopes:
            dependent_scope_string = " ".join(additional_scopes)
            flow_scope = f"{flow_scope}[{dependent_scope_string}]"
        run_result = self.flows_client.run_flow(
            self.flow_id,
            flow_scope=flow_scope,
            flow_input=flow_input,
            label=run_label,
            tags=tags,
        )
        run_id = run_result["run_id"]
        return GladierFlowRun(
            run_id,
            flow_input=flow_input,
            run_label=run_label,
            flow_manager=self,
            flows_client=self.flows_client,
        )

    def update_running_flows(
        self,
        running_flows: t.List[GladierFlowRun],
        run_completion_callback: t.Optional[t.Callable[[GladierFlowRun], bool]] = None,
    ) -> bool:
        complete_runs: t.List[GladierFlowRun] = []
        for running_flow in running_flows:
            if running_flow.is_complete():
                complete_runs.append(running_flow)
                if run_completion_callback is not None:
                    end_runs = run_completion_callback(running_flow)
                    if end_runs:
                        return end_runs
        for complete_run in complete_runs:
            running_flows.remove(complete_run)
        return False

    def run_many(
        self,
        run_input_iterator: t.Iterable[JSONObject],
        max_concurrency=5,
        min_delay=100,
        run_completion_callback: t.Optional[t.Callable[[GladierFlowRun], bool]] = None,
        tags: t.Optional[t.List[str]] = None,
        label_template: t.Optional[str] = None,
        label_template_values: t.Optional[t.List[str]] = None,
        wait_for_all_completions=False,
        progress_monitor: t.Optional[t.Callable[[t.List[GladierFlowRun]], None]] = None,
    ):
        running_flows: t.List[GladierFlowRun] = []
        last_run_time = time.time()
        end_runs = False
        if label_template_values is None:
            label_template_values = []

        for run_input in run_input_iterator:
            at_concurrency_limit = True
            while at_concurrency_limit:
                end_runs = self.update_running_flows(
                    running_flows, run_completion_callback=run_completion_callback
                )
                at_concurrency_limit = len(running_flows) >= max_concurrency
                if at_concurrency_limit and not end_runs:
                    time.sleep(2)
                if progress_monitor is not None:
                    progress_monitor(running_flows)

            if end_runs:
                break

            if label_template is not None:
                evaluated_template_vals: t.List[t.Any] = []
                for label_template_value in label_template_values:
                    evaluated_template_vals.append(
                        eval_jsonpath_for_input(label_template_value, run_input)
                    )
                run_label = label_template.format(*evaluated_template_vals)
            else:
                run_label = f"Run of {self.flow_id}"

            now = time.time()
            sleep_time = (last_run_time + min_delay) - now
            if sleep_time > 0:
                time.sleep(float(sleep_time) / 1000.0)
            flow_run = self.run_flow(run_input, run_label, tags)
            last_run_time = time.time()
            running_flows.append(flow_run)
            if progress_monitor is not None:
                progress_monitor(running_flows)

        while wait_for_all_completions and len(running_flows) > 0:
            wait_for_all_completions = not self.update_running_flows(
                running_flows, run_completion_callback=run_completion_callback
            )
            if wait_for_all_completions and len(running_flows) > 0:
                time.sleep(2)
            if progress_monitor is not None:
                progress_monitor(running_flows)

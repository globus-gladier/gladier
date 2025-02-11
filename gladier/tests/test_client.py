from unittest.mock import Mock
from gladier.tests.test_data.gladier_mocks import MockGladierClient, mock_func


def test_get_input(logged_in):
    assert MockGladierClient().get_input() == {
        "input": {
            "compute_endpoint": "my_compute_endpoint",
            "mock_func_function_id": "mock_compute_function",
        }
    }


def test_get_flow_id(logged_in):
    assert MockGladierClient().get_flow_id() is None


def test_get_input_from_aliased_tool(logged_in):
    class MockGladierClientAlias(MockGladierClient):
        gladier_tools = [
            "gladier.tests.test_data.gladier_mocks.MockToolWithRequirements:MyAlias"
        ]

    assert MockGladierClientAlias().get_input() == {
        "input": {
            "compute_endpoint": "my_compute_endpoint",
            "mock_func_function_id": "mock_compute_function",
            "my_alias_default_var": "is a thing!",
        }
    }


def test_get_input_from_priv_config(logged_in, mock_secrets_config):
    cli = MockGladierClient()
    cli.storage.set_value("compute_endpoint", "new_ep_uuid")
    assert cli.get_input() == {
        "input": {
            "compute_endpoint": "new_ep_uuid",
            "mock_func_function_id": "mock_compute_function",
        }
    }


def test_pub_config_overrides_priv(logged_in, storage, mock_secrets_config):
    cli = MockGladierClient()
    cli.storage.set_value("compute_endpoint", "my_ep_uuid")
    assert cli.get_input() == {
        "input": {
            "compute_endpoint": "my_ep_uuid",
            "mock_func_function_id": "mock_compute_function",
        }
    }


def test_run_flow(logged_in):
    cli = MockGladierClient(login_manager=logged_in)
    cli.run_flow()


def test_propagated_group_uuid(monkeypatch, logged_in):
    class MockGladierClientShared(MockGladierClient):
        globus_group = "my-globus-group"

        gladier_tools = ["gladier.tests.test_data.gladier_mocks.GeneratedTool"]

    cli = MockGladierClientShared(login_manager=logged_in)
    monkeypatch.setattr(cli.compute_manager.compute_client, "register_function", Mock())
    cli.run_flow()
    cli.compute_manager.compute_client.register_function.assert_called_with(
        mock_func, group="my-globus-group"
    )

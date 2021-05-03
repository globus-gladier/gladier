import pytest
from gladier.tests.test_data.gladier_mocks import MockGladierClient, mock_func


def test_register_funcx_function(logged_in, mock_funcx_client):
    cli = MockGladierClient()
    cli.funcx_client.register_function(mock_func)
    assert mock_funcx_client.register_function.called


@pytest.mark.skip
def test_register_flow():
    pass

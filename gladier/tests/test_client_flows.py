import pytest
from gladier.tests.test_data.gladier_mocks import MockGladierClient


def test_get_input(logged_in):
    assert MockGladierClient().get_input() == {'input': {
        'funcx_endpoint_non_compute': 'my_non_compute_endpoint_uuid',
        'mock_func_funcx_id': 'mock_funcx_id',
    }}


def test_get_input_from_priv_config(logged_in, mock_secrets_config):
    cli = MockGladierClient()
    cli.get_cfg(private=True)[cli.section]['funcx_endpoint_non_compute'] = 'new_ep_uuid'
    assert cli.get_input() == {'input': {
        'funcx_endpoint_non_compute': 'new_ep_uuid',
        'mock_func_funcx_id': 'mock_funcx_id',
        }
    }


def test_get_input_from_pub_config(logged_in, mock_config):
    cli = MockGladierClient()
    cli.get_cfg(private=False)[cli.section]['funcx_endpoint_non_compute'] = 'new_ep_uuid'
    assert cli.get_input() == {'input': {
        'funcx_endpoint_non_compute': 'new_ep_uuid',
        'mock_func_funcx_id': 'mock_funcx_id',
        }
    }


def test_pub_config_overrides_priv(logged_in, mock_config, mock_secrets_config):
    cli = MockGladierClient()
    cli.get_cfg(private=True)[cli.section]['funcx_endpoint_non_compute'] = 'priv_ep_uuid'
    cli.get_cfg(private=False)[cli.section]['funcx_endpoint_non_compute'] = 'pub_ep_uuid'
    assert cli.get_input() == {'input': {
        'funcx_endpoint_non_compute': 'pub_ep_uuid',
        'mock_func_funcx_id': 'mock_funcx_id',
        }
    }


def test_run_flow(logged_in):
    cli = MockGladierClient()
    cli.run_flow()


@pytest.mark.skip
def test_progress():
    pass


@pytest.mark.skip
def test_get_status():
    pass


@pytest.mark.skip
def test_get_details():
    pass

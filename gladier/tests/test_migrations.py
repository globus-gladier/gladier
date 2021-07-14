from gladier.tests.test_data.gladier_mocks import MockGladierClient
from gladier.version import __version__


def test_config_add_version(mock_config, logged_in):
    mc = MockGladierClient()
    assert mc.get_cfg()['general']['version'] == __version__


def test_migrate_to_v04x(mock_config, logged_in, mock_version_040):
    mock_config['general'] = {}
    mock_config['general']['version'] = '0.3.0'
    mock_config['mock_gladier_client'] = {}
    mock_config['mock_gladier_client']['myfuncx_funcx_id'] = 'uuid'
    mc = MockGladierClient()
    assert mc.get_cfg()['general']['version'] == mock_version_040
    assert not mock_config['mock_gladier_client'].get('myfuncx_funcx_id')


def test_migrate_to_v03x(mock_config, logged_in, mock_version_030):
    mock_config['general'] = {}
    mock_config['general']['version'] = '0.4.0'
    mock_config['mock_gladier_client'] = {}
    mock_config['mock_gladier_client']['myfuncx_funcx_id'] = 'uuid'
    mc = MockGladierClient()
    assert mc.get_cfg()['general']['version'] == mock_version_030

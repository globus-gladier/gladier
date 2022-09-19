from gladier.managers import CallbackLoginManager
from gladier.tests.test_data.gladier_mocks import MockGladierClient
from gladier.version import __version__


def test_config_add_version(mock_config, logged_in):
    mc = MockGladierClient()
    assert mc.storage.get('general', 'version') == __version__


def test_no_migration_needed(mock_config, logged_in):
    """Ensure the config isn't written when no migrations are needed.
    This can corrupt the tokens file if the client is written rapidly."""
    mock_config['general'] = {}
    mock_config['general']['version'] = __version__
    mock_config['tokens_client_id'] = {}

    # Callback login manager is used since it's token management is in memory, and
    # it will not write to the db.
    MockGladierClient(login_manager=CallbackLoginManager({}))
    assert not mock_config.save.called

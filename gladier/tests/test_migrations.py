from gladier.tests.test_data.gladier_mocks import MockGladierClient
from gladier.storage.tokens import GladierSecretsConfig
from gladier.storage.migrations import needs_migration

from gladier.version import __version__


def test_config_add_version(storage, logged_in):
    mc = MockGladierClient()
    assert mc.storage.get('general', 'version') == __version__


def test_no_migration_needed(storage, logged_in):
    """Ensure the config isn't written when no migrations are needed.
    This can corrupt the tokens file if the client is written rapidly."""
    storage['general'] = {}
    storage['general']['version'] = __version__
    storage['tokens_client_id'] = {}
    storage.save()

    cfg = GladierSecretsConfig('mockfile')
    assert not needs_migration(cfg)


def test_funcx_migration(storage, logged_in):
    storage['my_client_section'] = {}
    storage['my_client_section']['foo_funcx_id'] = 'foo_funcx_id'
    storage['my_client_section']['foo_funcx_id_checksum'] = 'foo fx cksum'

    storage.write()
    cfg = GladierSecretsConfig('filename')
    cfg.update()

    assert not cfg['my_client_section'].get('foo_funcx_id')

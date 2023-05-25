from abc import ABC, abstractmethod
from packaging import version
import logging
import gladier.version
import traceback

log = logging.getLogger(__name__)


class ConfigMigration(ABC):

    def __init__(self, config):
        self.config = config

        if 'general' not in self.config.sections():
            log.debug('No version in config, adding...')
            self.config.add_section('general')
        cfg_version = self.config['general'].get('version')

        self.config_version = version.parse(cfg_version) if cfg_version else None
        self.version = version.parse(gladier.version.__version__)

    @abstractmethod
    def is_applicable(self):
        pass

    @abstractmethod
    def migrate(self):
        pass


class AddVersionToConfig(ConfigMigration):
    """
    Add a version if one does not exist in the config.
    """
    def is_applicable(self):
        return self.config_version is None

    def migrate(self):
        # Set the version
        self.config['general']['version'] = str(self.version)
        log.info(f'Setting Version {self.version}')


class UpdateConfigVersion(ConfigMigration):
    """Sets the config version to the current version of Gladier.
    Should be run LAST, after all other migrations have taken place"""
    def is_applicable(self):
        return self.config_version != self.version

    def migrate(self):
        self.config['general']['version'] = str(self.version)


class UpdateFuncXFunctions(ConfigMigration):
    """Updates from old functions which were named: my_thing_funcx_id to
    the newer compute function names named my_thing_function_id"""
    def is_applicable(self):
        for section in self.config.sections():
            for key in self.config[section].keys():
                if key.endswith('funcx_id') and not key.count('funcx_id') > 1:
                    return True

    def migrate(self):
        for section in self.config.sections():
            try:
                todelete = []
                for key, value in self.config[section].items():
                    if key.endswith('funcx_id') and not key.count('funcx_id') > 1:
                        oldkey_checksum = f'{key}_checksum'
                        newkey = key.replace('funcx_id', 'function_id')
                        newkey_checksum = f'{newkey}_checksum'
                        if not self.config[section].get(newkey):
                            log.info(f'Migrating new function name {section}.{key} to '
                                     f'{section}.{newkey}')
                            self.config[section][newkey] = value
                            log.info('Migrating new function checksum name '
                                     f'{section}.{oldkey_checksum} to {section}.{newkey_checksum}')
                            self.config[section][newkey_checksum] = \
                                self.config[section][oldkey_checksum]
                        todelete.append(key)

                # Delete old keys
                for oldkey in todelete:
                    log.info(f'Deleting {section}.{oldkey}')
                    self.config.remove_option(section, oldkey)
                    if self.config[section].get(oldkey_checksum):
                        log.info(f'Deleting {section}.{oldkey_checksum}')
                        self.config.remove_option(section, oldkey_checksum)

            except Exception:
                traceback.print_exc()
                print('Failed to migrate Gladier config. Please send us the error above!')
                print('If you see this error again, you can try deleting ~/.gladier-secrets.cfg')


MIGRATIONS = [
    AddVersionToConfig,
    UpdateConfigVersion,
    UpdateFuncXFunctions,
]


def needs_migration(config):
    return any(m(config).is_applicable() for m in MIGRATIONS)


def migrate_gladier(config):
    for migration in MIGRATIONS:
        m_instance = migration(config)
        if m_instance.is_applicable():
            log.info(f'Applying migration: {m_instance.__class__.__name__}')
            m_instance.migrate()
    return config


def panic_print(message):
    """Print a message to console for the user to see. The message must be URGENT."""
    print(message)

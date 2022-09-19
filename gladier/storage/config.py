import logging
import configparser
from gladier.storage.migrations import needs_migration, migrate_gladier

log = logging.getLogger(__name__)


class GladierConfig(configparser.ConfigParser):

    def __init__(self, filename, section='default'):
        super().__init__()
        self.section = section
        self.filename = filename
        self.read(self.filename)
        if section not in self.sections():
            log.debug(f'Section {section} missing, adding to config.')
            self[section] = {}
            self.save()

    def save(self):
        with open(self.filename, 'w') as configfile:
            self.write(configfile)
            log.debug(f'Saved local gladier config to {configfile}')

    def update(self):
        if needs_migration(self):
            self = migrate_gladier(self)
            self.save()

    def get_value(self, name: str) -> str:
        try:
            return self.get(self.section, name)
        except configparser.NoOptionError:
            return None

    def set_value(self, name: str, value: str):
        self.set(self.section, name, value)
        self.save()

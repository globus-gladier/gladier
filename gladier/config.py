import logging
import configparser

log = logging.getLogger(__name__)


class GladierConfig(configparser.ConfigParser):

    def __init__(self, filename, section='default'):
        super().__init__()
        self.section = section
        self.filename = filename
        self.read(self.filename)

    def read(self):
        with open(self.filename, 'w') as configfile:
            return self.read(configfile)

    def save(self):
        with open(self.filename, 'w') as configfile:
            self.write(configfile)
            log.debug(f'Saved local gladier config to {configfile}')

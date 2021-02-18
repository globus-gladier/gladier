import logging
import configparser

log = logging.getLogger(__name__)


class GladierConfig(configparser.ConfigParser):

    def __init__(self, filename, section=None):
        super().__init__()
        self.section = section or self.DEFAULT_SECTION
        self.filename = filename
        self.read(self.filename)

    def save(self):
        with open(self.filename, 'w') as configfile:
            self.write(configfile)
            log.debug(f'Saved local gladier config to {configfile}')

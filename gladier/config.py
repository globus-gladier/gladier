import logging
import os
import stat
import configparser
from fair_research_login.token_storage import flat_pack, flat_unpack

log = logging.getLogger(__name__)


class GladierConfig(configparser.ConfigParser):

    def __init__(self, filename, section='default'):
        super().__init__()
        self.section = section
        self.filename = filename
        self.read(self.filename)

    def save(self):
        with open(self.filename, 'w') as configfile:
            self.write(configfile)
            log.debug(f'Saved local gladier config to {configfile}')


class GladierSecretsConfig(GladierConfig):

    DEFAULT_PERMISSION = stat.S_IRUSR | stat.S_IWUSR
    TOKENS_SECTION_DEFAULT = 'tokens_{client_id}'

    def __init__(self, filename, section, client_id):
        super().__init__(filename, section)
        self.tokens_section = self.TOKENS_SECTION_DEFAULT.format(client_id=client_id)
        if self.tokens_section not in self.sections():
            log.debug(f'Adding new section {section} to {self.filename}')
            self[self.tokens_section] = {}
            self.save()

    def save(self):
        super().save()
        os.chmod(self.filename, self.DEFAULT_PERMISSION)

    def write_tokens(self, tokens):
        for name, value in flat_pack(tokens).items():
            self.set(self.tokens_section, name, value)
        self.save()

    def read_tokens(self):
        return flat_unpack(dict(self.items(self.tokens_section)))

    def clear_tokens(self):
        self.remove_section(self.tokens_section)
        self.add_section(self.tokens_section)
        self.save()

import os
import stat
import logging
from fair_research_login.token_storage import flat_pack, flat_unpack
from gladier.storage.config import GladierConfig


log = logging.getLogger(__name__)


class GladierSecretsConfig(GladierConfig):
    DEFAULT_PERMISSION = stat.S_IRUSR | stat.S_IWUSR

    def __init__(self, *args, tokens_section="tokens", **kwargs):
        self.tokens_section = tokens_section
        super().__init__(*args, **kwargs)

    def save(self):
        super().save()
        os.chmod(self.filename, self.DEFAULT_PERMISSION)

    def load(self):
        super().load()
        if self.tokens_section not in self.sections():
            self[self.tokens_section] = {}
            self.save()

    def write_tokens(self, tokens):
        self.load()
        for name, value in flat_pack(tokens).items():
            self.set(self.tokens_section, name, value)
        log.debug(f"Wrote tokens to {self.filename}")
        self.save()

    def read_tokens(self):
        self.load()
        return flat_unpack(dict(self.items(self.tokens_section)))

    def clear_tokens(self):
        self.load()
        self.remove_section(self.tokens_section)
        self.add_section(self.tokens_section)
        log.debug(f"Tokens cleared from {self.filename}")
        self.save()

import os
import stat
from fair_research_login.token_storage import flat_pack, flat_unpack
from gladier.storage.config import GladierConfig


class GladierSecretsConfig(GladierConfig):

    DEFAULT_PERMISSION = stat.S_IRUSR | stat.S_IWUSR

    def save(self):
        super().save()
        os.chmod(self.filename, self.DEFAULT_PERMISSION)

    def write_tokens(self, tokens):
        self.load()
        for name, value in flat_pack(tokens).items():
            self.set(self.section, name, value)
        self.save()

    def read_tokens(self):
        self.load()
        return flat_unpack(dict(self.items(self.section)))

    def clear_tokens(self):
        self.load()
        self.remove_section(self.section)
        self.add_section(self.section)
        self.save()

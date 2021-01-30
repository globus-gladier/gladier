import configparser


class GladierConfig(configparser.ConfigParser):
    DEFAULT_SECTION = 'general'

    def __init__(self, filename, section=None):
        super().__init__()
        self.section = section or self.DEFAULT_SECTION
        self.filename = filename
        try:
            self.read(self.filename)
            if self.section not in self.sections():
                self.add_section(self.section)
        except Exception as e:
            raise

    # def load(self):
    #     self.read(self.filename)
    #     if self.section not in self.sections():
    #         config.add_section(self.section)
    #     return self

    def save(self):
        with open(self.filename, 'w') as configfile:
            self.write(configfile)

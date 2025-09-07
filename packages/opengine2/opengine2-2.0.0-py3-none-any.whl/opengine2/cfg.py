from xdg import BaseDirectory
import tomllib

class Cfg:
    def __init__(self, filename):
        with open(filename, 'rb') as f:
            dat = tomllib.load(f)
        self.default_kbd = dat['default_kbd']
        self.keyboards = dat['keyboards']

    @classmethod
    def load(cls):
        return cls(BaseDirectory.load_first_config('opengine2', 'conf.toml'))

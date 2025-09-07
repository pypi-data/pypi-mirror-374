import tomllib
import unicodedata
from importlib import resources
import logging
from pathlib import Path
from xdg import BaseDirectory
import itertools
import pyhocon

_logger = logging.getLogger(__name__)

def parse_char_descr_pairs(thing):
    match thing:
        case [str() as char, str() as descr]:
            return (char, descr)
        case [str() as single_char]:
            return (single_char, unicodedata.name(single_char))

class Kbd:
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"

    def __init__(self, name, sortkey, keydat):
        self.name = name
        self.sortkey = sortkey
        self.chars = dict()
        for inchar, *outcharspec in keydat:
            self.chars.setdefault(inchar, list())
            self.chars[inchar].append(parse_char_descr_pairs(outcharspec))

    @classmethod
    def from_toml(cls, filename):
        with open(filename, 'rb') as f:
            dat = tomllib.load(f)
        if 'opengine2_version' in dat:
            return cls(dat['name'], filename.name.split(".")[0], dat['keys'])
        else:
            raise ValueError(f"""File given ({filename}) is not a keyboard file\
            (must contain key `opengine2_version')""")

    @classmethod
    def from_hocon(cls, filename):
        dat = pyhocon.ConfigFactory.parse_file(filename)
        if 'opengine2_version' in dat:
            return cls(dat['name'], filename.name.split(".")[0], dat['keys'])
        else:
            raise ValueError(f"""File given ({filename}) is not a keyboard file\
            (must contain key `opengine2_version')""")

    def getchar(self, key, index):
        thing = self.chars.get(key)
        if thing:
            return thing[index % len(thing)][0]
        else:
            return None

    def getlabel(self, key, index):
        thing = self.chars.get(key)
        if thing:
            return thing[index % len(thing)][1]
        else:
            return None

    def getcharlist(self, key):
        return ''.join(x[0] for x in self.chars.get(key, []))

class Kbdlist:
    def __init__(self, files):
        self.kbds = list()
        for i in files:
            if i.suffix == ".toml":
                self.kbds.append(Kbd.from_toml(i))
            elif i.suffix == ".hocon":
                self.kbds.append(Kbd.from_hocon(i))
        self.kbds.sort(key=lambda x: x.sortkey)

    @classmethod
    def find_keyboards(cls, cfg):
        files_from_config = list() # to be filled in later
        files_from_xdg = BaseDirectory.load_data_paths("opengine")
        files_from_cwd = Path.cwd().glob("*.opengine2.*")
        if __package__ is not None:
            files_from_package = resources.files(__package__).glob("*.opengine2.*")
        else:
            files_from_package = list()
        return cls(itertools.chain(
            files_from_package,
            files_from_config,
            files_from_xdg,
            files_from_cwd))

from abc import ABC, abstractmethod
from argparse import ArgumentParser

from afqlite.afqlite import AFQLite

COMMAND_PREFIX = '.'


class Command(ABC):
    def __init__(self, name: str, description: str):
        self.parser: ArgumentParser = ArgumentParser(prog=name, description=description)

    @property
    def name(self) -> str:
        return self.parser.prog

    @property
    def description(self) -> str:
        return self.parser.description

    @abstractmethod
    def run(self, afql: AFQLite, argv: list[str] = None):
        pass


class Help(Command):
    def __init__(self):
        super().__init__("help", "show the help message")

    def run(self, afql: AFQLite, argv: list[str] = None):
        indent = max(len(name) for name in commands) + 1
        for name in commands:
            print(("{:<%i}: {}" % indent).format(name, commands[name].description))


class Exit(Command):
    def __init__(self):
        super().__init__("exit", "exit the AFQLite cli")

    def run(self, afql: AFQLite, args: list[str] = None):
        raise EOFError  # simulate EOF, which shuts down the prompt


class Open(Command):
    def __init__(self):
        super().__init__("open", "open a video")
        self.parser.add_argument("alias")
        self.parser.add_argument("file")

    def run(self, afql: AFQLite, args: list[str] = None):
        parsed_args = self.parser.parse_args(args)
        print("Opening '%s' for alias '%s'" % (parsed_args.file, parsed_args.alias))
        # TODO


class Import(Command):
    def __init__(self):
        super().__init__("import", "import an afqlite cache")
        self.parser.add_argument("file", help="path to the cache file to be imported")

    def run(self, afql: AFQLite, args: list[str] = None):
        parsed_args = self.parser.parse_args(args)
        print("Importing '%s'" % (parsed_args.file,))
        # TODO


_commands = [
    Help(),
    Exit(),
    Open(),
    Import()
]

commands = {c.name: c for c in _commands}

from abc import ABC, abstractmethod
from argparse import ArgumentParser

from afqlite.afqlite import AFQLite
from afqlite.test_integration import TestIntegration
from afqlite.test_arman import TestArman


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
        self.parser.add_argument("dataset")
        self.parser.add_argument("file")
        self.parser.add_argument("--cache", default=None)

    def run(self, afql: AFQLite, args: list[str] = None):
        parsed_args = self.parser.parse_args(args)
        msg = "Opening '%s' for alias '%s'" % (parsed_args.file, parsed_args.dataset)
        if parsed_args.cache is not None:
            msg += ", loading from cache in '%s'" % (parsed_args.cache,)

        print(msg)
        afql.load_video(parsed_args.dataset, parsed_args.file, parsed_args.cache)

class Import(Command):
    def __init__(self):
        super().__init__("import", "import an afqlite cache")
        self.parser.add_argument("dataset", help="name of the dataset we're importing for")
        self.parser.add_argument("detector", help="name of the detector we're importing for")
        self.parser.add_argument("file", help="path to the cache file to be imported")

    def run(self, afql: AFQLite, args: list[str] = None):
        parsed_args = self.parser.parse_args(args)
        print("Importing '%s' for dataset '%s' and detector '%s'" % (
            parsed_args.file, parsed_args.dataset, parsed_args.detector))
        afql.import_cache_from_file(parsed_args.dataset, parsed_args.detector, parsed_args.file)


class Export(Command):
    def __init__(self):
        super().__init__("export", "export an afqlite cache")
        self.parser.add_argument("dataset", help="name of the dataset we're exporting for")
        self.parser.add_argument("detector", help="name of the detector we're exporting for")
        self.parser.add_argument("file", help="path to the file the cache is exported to")

    def run(self, afql: AFQLite, args: list[str] = None):
        parsed_args = self.parser.parse_args(args)
        print("Exporting cache for dataset '%s' and detector '%s' to '%s'" % (
            parsed_args.dataset, parsed_args.detector, parsed_args.file))
        afql.write_cache_to_file(parsed_args.dataset, parsed_args.detector, parsed_args.file)
        
class Load(Command):
    def __init__(self):
        super().__init__("load", "load a detector")
        self.parser.add_argument("detector", help="name of the detector to load")
        self.parser.add_argument("file", help="path to the file for the detector")
        self.parser.add_argument("--hash", help="hash to verify the detector gets loaded properly")

    def run(self, afql: AFQLite, args: list[str] = None):
        parsed_args = self.parser.parse_args(args)
        print("Loading detector '%s' from '%s'" % (parsed_args.detector, parsed_args.file))
        afql.add_detector(parsed_args.detector, parsed_args.file, parsed_args.hash)
        
class DemoQuery1(Command):
    def __init__(self):
        super().__init__("rtq1", 
                         "run demo query 1")
        self.parser.add_argument("display", help="display annotated video or not")

    def run(self, afql: AFQLite, args: list[str] = None):
        parsed_args = self.parser.parse_args(args)
        # msg = "Opening '%s' for alias '%s'" % (parsed_args.file, parsed_args.dataset)
        # if parsed_args.cache is not None:
        #     msg += ", loading from cache in '%s'" % (parsed_args.cache,)

        # print(msg)
        #afql.load_video(parsed_args.dataset, parsed_args.file, parsed_args.cache)
        print("recognized my command")
        ti = TestIntegration()
        ti.test_query2()
        
class DemoQuery2(Command):
    def __init__(self):
        super().__init__("rtq2", 
                         "run demo query 2")
        self.parser.add_argument("display", help="display annotated video or not")

    def run(self, afql: AFQLite, args: list[str] = None):
        parsed_args = self.parser.parse_args(args)
        # msg = "Opening '%s' for alias '%s'" % (parsed_args.file, parsed_args.dataset)
        # if parsed_args.cache is not None:
        #     msg += ", loading from cache in '%s'" % (parsed_args.cache,)

        # print(msg)
        #afql.load_video(parsed_args.dataset, parsed_args.file, parsed_args.cache)
        print("recognized my command")
        ti = TestArman()
        ti.test_query1()


_commands = [
    Help(),
    Exit(),
    Open(),
    Import(),
    Export(),
    Load(),
    DemoQuery1(),
    DemoQuery2()
]

commands = {c.name: c for c in _commands}

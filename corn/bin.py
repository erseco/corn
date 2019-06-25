import argparse
import sys
import os

from celery.utils import imports

from .worker import CornWorker


def main():
    command = CornCommand()
    command.execute_from_commandline()


class CornCommand:
    Parser = argparse.ArgumentParser
    args_name = 'args'
    commands = {
        'worker': CornWorker
    }

    def execute_from_commandline(self):
        argv = list(sys.argv)
        self.prog_name = os.path.basename(argv[0])
        args, options = self.handle_argv(self.prog_name, argv[1:])
        if options.get('worker'):
            cls = self.commands.get('worker')
            return cls(self.app)()

    def handle_argv(self, prog_name, argv, command=None):
        options, args = self.prepare_args(
            *self.parse_options(prog_name, argv, command))
        self.set_app(options)
        return args, options

    def prepare_args(self, options, args):
        return options, args

    def find_app(self, app):
        from .utils.app import find_app
        return find_app(app, symbol_by_name=self.symbol_by_name)

    def symbol_by_name(self, name, imp=imports.import_from_cwd):
        return imports.symbol_by_name(name, imp=imp)

    def set_app(self, options):
        self.app = self.find_app(options.get('app'))

    def get_app(self):
        return self.app

    def parse_options(self, prog_name, arguments, command=None):
        """Parse the available options."""
        # Don't want to load configuration to just print the version,
        # so we handle --version manually here.
        self.parser = self.create_parser(prog_name, command)
        options = vars(self.parser.parse_args(arguments))
        return options, options.pop(self.args_name, None) or []

    def usage(self, command):
        return '%(prog)s {0} [options] {1}'.format(command, sys.argv)

    def create_parser(self, prog_name, command=None):
        # for compatibility with optparse usage.
        usage = self.usage(command).replace('%prog', '%(prog)s')
        parser = self.Parser(
            prog=prog_name,
            usage=usage,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self.add_preload_arguments(parser)
        return parser

    def add_preload_arguments(self, parser):
        group = parser.add_argument_group('Global Options')
        group.add_argument('-A', '--app', default=None)
        group.add_argument('worker', help='Worker')

    def __call__(self, *args, **kwargs):
        import ipdb; ipdb.set_trace()

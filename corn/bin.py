import argparse
import sys

from .worker import CornWorker


def main():
    import ipdb; ipdb.set_trace()
    command = CornCommand()
    command.execute_from_commandline()
    app = command.get_app()
    if command.is_worker:
        worker = CornWorker(app)
        worker.start()


class CornCommand:
    Parser = argparse.ArgumentParser

    def execute_from_commandline(self):
        argv = list(sys.argv)
        self.prog_name = os.path.basename(argv[0])
        return self.handle_argv(self.prog_name, argv[1:])

    def handle_argv(self, prog_name, argv, command=None):
        options, args = self.prepare_args(
            *self.parse_options(prog_name, argv, command))
        return self(*args, **options)

    def parse_options(self, prog_name, arguments, command=None):
        """Parse the available options."""
        # Don't want to load configuration to just print the version,
        # so we handle --version manually here.
        self.parser = self.create_parser(prog_name, command)
        options = vars(self.parser.parse_args(arguments))
        return options, options.pop(self.args_name, None) or []

    def create_parser(self, prog_name, command=None):
        # for compatibility with optparse usage.
        usage = self.usage(command).replace('%prog', '%(prog)s')
        parser = self.Parser(
            prog=prog_name,
            usage=usage,
            epilog=self._format_epilog(self.epilog),
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=self._format_description(self.description),
        )
        self._add_version_argument(parser)
        self.add_preload_arguments(parser)
        self.add_arguments(parser)
        self.add_compat_options(parser, self.get_options())
        self.add_compat_options(parser, self.app.user_options['preload'])

        if self.supports_args:
            # for backward compatibility with optparse, we automatically
            # add arbitrary positional args.
            parser.add_argument(self.args_name, nargs='*')
        return self.prepare_parser(parser)

    def add_preload_arguments(self, parser):
        group = parser.add_argument_group('Global Options')
        group.add_argument('-A', '--app', default=None)

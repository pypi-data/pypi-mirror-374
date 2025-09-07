# Imports

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from commonkit.logging import LoggingHelper
from commonkit.shell import EXIT
from ..lib.contexts import Context
from ..lib.loaders import load_variables
from ..variables import LOGGER_NAME
from ..version import DATE as VERSION_DATE, VERSION
from . import initialize
from . import subcommands

DEBUG = 10

logging = LoggingHelper(colorize=True, name=LOGGER_NAME)
log = logging.setup()

# Commands


def main_command():
    """Process script configurations."""

    __author__ = "Shawn Davis <shawn@develmaycare.com>"
    __date__ = VERSION_DATE
    __help__ = """NOTES

    This command is used to parse configuration files and output the commands.

        """
    __version__ = VERSION

    # Main argument parser from which sub-commands are created.
    parser = ArgumentParser(description=__doc__, epilog=__help__, formatter_class=RawDescriptionHelpFormatter)

    # Initialize sub-commands.
    subparsers = parser.add_subparsers(
        dest="subcommand",
        help="Commands",
        metavar="docs, inventory, script"
    )

    initialize.subcommands(subparsers)

    # Access to the version number requires special consideration, especially
    # when using sub parsers. The Python 3.3 behavior is different. See this
    # answer: http://stackoverflow.com/questions/8521612/argparse-optional-subparser-for-version
    parser.add_argument(
        "-v",
        action="version",
        help="Show version number and exit.",
        version=__version__
    )

    parser.add_argument(
        "--version",
        action="version",
        help="Show verbose version information and exit.",
        version="%(prog)s" + " %s %s by %s" % (__version__, __date__, __author__)
    )

    # Parse arguments.
    args = parser.parse_args()

    if args.debug_enabled:
        log.setLevel(DEBUG)

    log.debug("Namespace: %s" % args)

    # Load resources for docs and script output.
    if args.subcommand in ["docs", "script"]:
        # Create the global context.
        context = Context()

        if args.variables_file:
            variables = load_variables(args.variables_file)
            for v in variables:
                context.variables[v.name] = v

        if args.variables:
            initialize.variables_from_cli(context, args.variables)

        # Handle global command options.
        options = dict()
        if args.options:
            options = initialize.options_from_cli(args.options)

        loader = initialize.loader(
            args.command_file,
            context=context,
            options=options,
            template_locations=args.template_locations
        )
        if loader is None:
            exit(EXIT.ERROR)

    # Handle sub-commands.
    if args.subcommand == "docs":
        # noinspection PyUnboundLocalVariable
        exit_code = subcommands.generate_docs(
            loader,
            output_file=args.output_file,
            output_format=args.output_format
        )
    elif args.subcommand in ["inv", "inventory"]:
        exit_code = subcommands.copy_inventory(args.name, to_path=args.to_path)
    elif args.subcommand == "script":
        # noinspection PyUnboundLocalVariable
        exit_code = subcommands.generate_script(
            loader,
            color_enabled=args.color_enabled,
            include_shebang=args.include_shebang,
            output_file=args.output_file
        )
    else:
        print("Unrecognized command: %s" % args.subcommand)
        exit_code = EXIT.USAGE

    exit(exit_code)

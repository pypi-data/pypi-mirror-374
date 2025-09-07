import logging

from commonkit import smart_cast
from commonkit.shell import EXIT
import logging
import os
from ..lib.loaders import load_variables, INILoader, YMLLoader
from ..variables import LOGGER_NAME, PATH_TO_SCRIPT_TEASE

log = logging.getLogger(LOGGER_NAME)


def options_from_cli(options):
    _options = dict()
    for token in options:
        try:
            key, value = token.split(":")
            _options[key] = smart_cast(value)
        except ValueError:
            _options[token] = True

    return _options


def loader(path, context=None, options=None, template_locations=None):
    # The path may have been given as a file name (steps.ini), path, or an inventory name.
    input_locations = [
        path,
        os.path.join(PATH_TO_SCRIPT_TEASE, "data", "inventory", path, "steps.ini"),
        os.path.join(PATH_TO_SCRIPT_TEASE, "data", "inventory", path, "steps.yml"),
    ]
    path = None
    for location in input_locations:
        if os.path.exists(location):
            path = location
            break

    if path is None:
        log.warning("Path does not exist: %s" % path)
        return None

    # Initialize the loader.
    if path.endswith(".ini"):
        _loader = INILoader(
            path,
            context=context,
            locations=template_locations,
            **options
        )
    elif path.endswith(".yml"):
        _loader = YMLLoader(
            path,
            context=context,
            locations=template_locations,
            **options
        )
    else:
        log.error("Unsupported file format: %s" % path)
        return None

    # Load the commands.
    if not _loader.load():
        log.error("Failed to load the input file: %s" % path)
        return None

    return _loader


def subcommands(subparsers):
    """Initialize sub-commands.

    :param subparsers: The subparsers instance from argparse.

    """
    sub = SubCommands(subparsers)
    sub.docs()
    sub.inventory()
    sub.script()


def variables_from_cli(context, variables):
    for token in variables:
        try:
            key, value = token.split(":")
            context.add(key, smart_cast(value))
        except ValueError:
            context.add(token, True)


class SubCommands(object):

    def __init__(self, subparsers):
        self.subparsers = subparsers

    def docs(self):
        sub = self.subparsers.add_parser(
            "docs",
            help="Output documentation instead of code."
        )

        sub.add_argument(
            "-o=",
            "--output-format=",
            choices=["html", "md", "plain", "rst"],
            default="md",
            dest="output_format",
            help="The output format; HTML, Markdown, plain text, or ReStructuredText."
        )

        self._add_script_options(sub)
        self._add_common_options(sub)

    def inventory(self):
        sub = self.subparsers.add_parser(
            "inventory",
            aliases=["inv"],
            help="Copy an inventory item to a local directory."
        )

        sub.add_argument(
            "name",
            help="The name of the inventory item. Use ? to list available items."
        )

        sub.add_argument(
            "-P=",
            "--path=",
            dest="to_path",
            help="The path to where the item should be copied. Defaults to the current working directory."
        )

        self._add_common_options(sub)

    def script(self):
        sub = self.subparsers.add_parser(
            "script",
            help="Output the commands."
        )

        sub.add_argument(
            "-c",
            "--color",
            action="store_true",
            dest="color_enabled",
            help="Enable code highlighting for terminal output."
        )

        sub.add_argument(
            "-s",
            "--shebang",
            action="store_true",
            dest="include_shebang",
            help="Add the shebang to the beginning of the output."
        )

        self._add_script_options(sub)
        self._add_common_options(sub)

    def _add_common_options(self, sub):
        sub.add_argument(
            "-D",
            "--debug",
            action="store_true",
            dest="debug_enabled",
            help="Enable debug mode. Produces extra output."
        )

        sub.add_argument(
            "-p",
            action="store_true",
            dest="preview_enabled",
            help="Preview mode."
        )

    def _add_script_options(self, sub):
        sub.add_argument(
            "-C=",
            "--context=",
            action="append",
            dest="variables",
            help="Context variables for use in pre-parsing the config and templates. In the form of: name:value"
        )

        sub.add_argument(
            "-i=",
            "--input-file=",
            default="steps.ini",
            dest="steps_file",
            help="The path to the configuration file."
        )

        # sub.add_argument(
        #     "-f=",
        #     "--filter=",
        #     action="append",
        #     dest="filters",
        #     help="Filter the commands in the form of: attribute:value"
        # )

        # Capture filters.
        # if args.filters:
        #     filters = dict()
        #     for token in args.filters:
        #         key, value = token.split(":")
        #         if key not in filters:
        #             filters[key] = list()
        #
        #         filters[key].append(value)

        sub.add_argument(
            "-O=",
            "--option=",
            action="append",
            dest="options",
            help="Common command options in the form of: name:value"
        )

        sub.add_argument(
            "-P=",
            "--profile=",
            choices=["centos", "ubuntu"],
            default="ubuntu",
            dest="profile",
            help="The OS profile to use."
        )

        sub.add_argument(
            "-T=",
            "--template-path=",
            action="append",
            dest="template_locations",
            help="The location of template files that may be used with the template command."
        )

        sub.add_argument(
            "-w=",
            "--write=",
            dest="output_file",
            help="Write the output to disk."
        )

        sub.add_argument(
            "-V=",
            "--variables-file=",
            dest="variables_file",
            help="Load variables from a file."
        )

# # Imports
#
# from commonkit import smart_cast
# from configparser import ConfigParser
# import logging
# import os
# from ..constants import LOGGER_NAME
#
# log = logging.getLogger(LOGGER_NAME)
#
# # Exports
#
# __all__ = (
#     "context_from_cli",
#     "filters_from_cli",
#     "options_from_cli",
#     "variables_from_file",
# )
#
# # Functions
#
#
# def context_from_cli(variables):
#     """Takes a list of variables given in the form of ``name:value`` and converts them to a dictionary.
#
#     :param variables: A list of strings of ``name:value`` pairs.
#     :type variables: list[str]
#
#     :rtype: dict
#
#     The ``value`` of the pair passes through "smart casting" to convert it to the appropriate Python data type.
#
#     """
#     context = dict()
#     for i in variables:
#         key, value = i.split(":")
#         context[key] = smart_cast(value)
#
#     return context
#
#
# def filters_from_cli(filters):
#     """Takes a list of filters given in the form of ``name:value`` and converts them to a dictionary.
#
#     :param filters: A list of strings of ``attribute:value`` pairs.
#     :type filters: list[str]
#
#     :rtype: dict
#
#     """
#     _filters = dict()
#     for i in filters:
#         key, value = i.split(":")
#         if key not in filters:
#             _filters[key] = list()
#
#         _filters[key].append(value)
#
#     return _filters
#
#
# def options_from_cli(options):
#     """Takes a list of variables given in the form of ``name:value`` and converts them to a dictionary.
#
#     :param options: A list of strings of ``name:value`` pairs.
#     :type options: list[str]
#
#     :rtype: dict
#
#     The ``value`` of the pair passes through "smart casting" to convert it to the appropriate Python data type.
#
#     """
#     _options = dict()
#     for i in options:
#         key, value = i.split(":")
#         _options[key] = smart_cast(value)
#
#     return _options
#
#
# def variables_from_file(path):
#     """Loads variables from a given INI file.
#
#     :param path: The path to the INI file.
#     :type path: str
#
#     :rtype: dict | None
#
#     The resulting dictionary flattens the sections and values. For example:
#
#     .. code-block:: ini
#
#         [copyright]
#         name = ACME, Inc.
#         year = 2020
#
#         [domain]
#         name = example.com
#         tld = example_com
#
#     The dictionary would contain:
#
#     .. code-block:: python
#
#         {
#             'copyright_name': "ACME, Inc.",
#             'copyright_year': 2020,
#             'domain_name': "example.com",
#             'domain_tld': "example_com",
#         }
#
#     """
#     if not os.path.exists(path):
#         log.warning("Variables file does not exist: %s" % path)
#         return None
#
#     ini = ConfigParser()
#     ini.read(path)
#
#     variables = dict()
#     for section in ini.sections():
#         for key, value in ini.items(section):
#             key = "%s_%s" % (section, key)
#             variables[key] = smart_cast(value)
#
#     return variables

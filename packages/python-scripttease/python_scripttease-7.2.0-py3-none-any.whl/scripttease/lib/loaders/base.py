# Imports

from commonkit import any_list_item, parse_jinja_string, parse_jinja_template, pick, read_file, smart_cast, split_csv, \
    File
from configparser import ParsingError, ConfigParser
from jinja2.exceptions import TemplateError, TemplateNotFound
import logging
import os
from ...constants import EXCLUDED_KWARGS
from ..contexts import Variable

log = logging.getLogger(__name__)

# Exports


__all__ = (
    # "filter_snippets",
    "load_variables",
    "BaseLoader",
)
# Functions


# def filter_commands(commands, key, value):
#     """Filter commands based on the given criteria.
#
#     :param commands: The commands to be filtered.
#     :type commands: list[scripttease.lib.commands.base.Command]
#
#     :param key: The attribute name to be matched.
#     :type key: str
#
#     :param value: The value of the attribute.
#
#     """
#     filtered = list()
#     for command in commands:
#         try:
#             values = getattr(command, key)
#         except AttributeError:
#             continue
#
#         if not any_list_item(values, key):
#             continue
#
#         if not any_list_item()
#         if environments is not None and len(snippet.environments) > 0:
#             if not any_list_item(environments, snippet.environments):
#                 continue
#
#         if tags is not None:
#             if not any_list_item(tags, snippet.tags):
#                 continue
#
#         filtered.append(snippet)
#
#     return filtered


def load_variables(path, env=None):
    """Load variables from an INI file.

    :param path: The path to the INI file.
    :type path: str

    :param env: The environment name of variables to return.
    :type env: str

    :rtype: list[scripttease.lib.contexts.Variable]

    """
    if not os.path.exists(path):
        log.warning("Variables file does not exist: %s" % path)
        return list()

    ini = ConfigParser()
    try:
        ini.read(path)
    except ParsingError as e:
        log.warning("Failed to parse %s variables file: %s" % (path, str(e)))
        return list()

    variables = list()
    for section in ini.sections():
        if ":" in section:
            variable_name, _environment = section.split(":")
        else:
            _environment = None
            variable_name = section

        kwargs = {
            'environment': _environment,
        }
        _value = None
        for key, value in ini.items(section):
            if key == "value":
                _value = smart_cast(value)
                continue

            kwargs[key] = smart_cast(value)

        variables.append(Variable(variable_name, _value, **kwargs))

    if env is not None:
        filtered_variables = list()
        for var in variables:
            if var.environment and var.environment == env or var.environment is None:
                filtered_variables.append(var)

        return filtered_variables

    return variables


# Classes


class BaseLoader(File):
    """Base class for loading a command file."""

    def __init__(self, path,  context=None, locations=None, **kwargs):
        """Initialize the loader.

        :param path: The path to the command file.
        :type path: str

        :param context: Global context that may be used to parse the command file and templates.
        :type context: scripttease.lib.contexts.Context

        :param locations: A list of paths where templates and other external files may be found. The ``templates/``
                          directory in which the command file exists is added automatically.
        :type locations: list[str]

        :param mappings: A mapping of canonical command names and their snippets, organized by ``profile``. The profile
                         is typically an operating system such as ``centos`` or ``ubuntu``.
        :type mappings: dict

        :param profile: The profile (operating system or platform) to be used.
        :type profile: str

        kwargs are stored as ``options`` and may include any of the common options for command configuration. These may
        be supplied as defaults for snippet processing.

        """
        self.commands = list()
        self.context = context
        self.is_loaded = False
        self.locations = locations or list()
        self.profile = kwargs.pop("profile", "ubuntu")

        self.options = kwargs

        super().__init__(path)

        # Always include the path to the current file in locations.
        self.locations.insert(0, os.path.join(self.directory, "templates"))

    def get_context(self):
        """Get the context for parsing command files.

        :rtype: dict

        """
        d = self.options.copy()
        if self.context is not None:
            d.update(self.context.mapping().copy())

        return d

    def load(self):
        """Load the command file.

        :rtype: bool

        """
        raise NotImplementedError()

    def read_file(self):
        """Get the content of the command file.

        :rtype: str | None

        """
        if self.context is not None:
            try:
                return parse_jinja_template(self.path, self.get_context())
            except Exception as e:
                log.error("Failed to process %s file as template: %s" % (self.path, e))
                return None

        return read_file(self.path)

    # noinspection PyMethodMayBeStatic
    def _get_key_value(self, key, value):
        """Process a key/value pair.

        :param key: The key to be processed.
        :type key: str

        :param value: The value to be processed.

        :rtype: tuple
        :returns: The key and value, both of which may be modified from the originals.

        This handles special names in the following manner:

        - ``environments``, ``environs``, ``envs``, and ``env`` are treated as a CSV list of environment names
          if provided as a string. These are normalized to the keyword ``environments``.
        - ``func`` and ``function`` are normalized to the keyword ``function``. The value is the name of the function to
          be defined.
        - ``groups`` is assumed to be a CSV list of groups if provided as a string.
        - ``items`` is assumed to be a CSV list if provided as a string. These are used to create an "itemized" command.
        - ``tags`` is assumed to be a CSV list if provided as a string.

        All other keys are used as is. Values provided as a CSV list are smart cast to a Python value.

        """
        if key in ("environments", "environs", "envs", "env"):
            _key = "environments"
            if type(value) in (list, tuple):
                _value = value
            else:
                _value = split_csv(value) if "," in value else split_csv(value, separator=" ")
        elif key in ("func", "function"):
            _key = "function"
            _value = value
        elif key == "groups":
            _key = "groups"
            if type(value) in (list, tuple):
                _value = value
            else:
                _value = split_csv(value) if "," in value else split_csv(value, separator=" ")
        elif key == "items":
            _key = "items"
            if type(value) in (list, tuple):
                _value = value
            else:
                _value = split_csv(value) if "," in value else split_csv(value, separator=" ")
        elif key == "tags":
            _key = "tags"
            if type(value) in (list, tuple):
                _value = value
            else:
                _value = split_csv(value) if "," in value else split_csv(value, separator=" ")
        else:
            _key = key
            _value = smart_cast(value)

        return _key, _value

# Imports

from commonkit import parse_jinja_template, read_file
from configparser import ConfigParser, ParsingError
import logging
from .base import BaseLoader

log = logging.getLogger(__name__)

# Exports

__all__ = (
    "INILoader",
)

# Classes


class INILoader(BaseLoader):
    """Load commands from an INI file."""

    def load(self):
        """Load the INI file.

        :rtype: bool

        """
        if not self.exists:
            log.warning("Input file does not exist: %s" % self.path)
            return False

        content = self.read_file()
        if content is None:
            return False

        ini = ConfigParser()
        try:
            ini.read_string(content)
        except ParsingError as e:
            log.error("Failed to parse %s as an INI file: %s" % (self.path, e))
            return False

        for comment in ini.sections():
            args = list()
            command_name = None
            count = 0
            kwargs = self.options.copy()
            kwargs['comment'] = comment

            for key, value in ini.items(comment):
                # Is there a reason for this?
                # if key.startswith("_"):
                #     continue

                # The first key/value pair is the command name and arguments.
                if count == 0:
                    command_name = key
                    # kwargs['name'] = command_name

                    # Explanations and screenshots aren't processed like commands, so the text need not be surrounded
                    # by double quotes.
                    if command_name in ("explain", "screenshot"):
                        args.append(value)
                        count += 1
                        continue

                    # Arguments surrounded by quotes are considered to be one argument. All others are split into a
                    # list to be passed to the command factory. It is also possible that this is a call where no
                    # arguments are present, so the whole thing is wrapped to protect against an index error. A TypeError is raised in
                    # cases where a command is provided with no positional arguments; we interpret this as True.
                    try:
                        if value[0] == '"':
                            args.append(value.replace('"', ""))
                        else:
                            args = value.split(" ")
                    except IndexError:
                        pass
                    # except TypeError:
                    #     noinspection PyTypeChecker
                        # args.append(True)
                else:
                    _key, _value = self._get_key_value(key, value)
                    kwargs[_key] = _value

                count += 1

            self.commands.append((command_name, args, kwargs))

        self.is_loaded = True
        return True

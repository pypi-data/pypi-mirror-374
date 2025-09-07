# Imports

from commonkit import parse_jinja_template, read_file
import logging
import yaml
from .base import BaseLoader

log = logging.getLogger(__name__)

# Exports

__all__ = (
    "YMLLoader",
)

# Classes


class YMLLoader(BaseLoader):
    """Load commands from an YAML file."""

    def load(self):
        """Load the YAML file.

        :rtype: bool

        """
        if not self.exists:
            return False

        content = self.read_file()
        if content is None:
            return False

        try:
            commands = yaml.load(content, yaml.Loader)
        except yaml.YAMLError as e:
            log.error("Failed to parse %s as a YAML file: %s" % (self.path, e))
            return False

        for command in commands:
            comment = list(command.keys())[0]
            tokens = list(command.values())[0]

            args = list()
            command_name = None
            count = 0
            kwargs = self.options.copy()
            kwargs['comment'] = comment
            kwargs['name'] = command

            for key, value in tokens.items():
                if key.startswith("_"):
                    continue

                if count == 0:
                    command_name = key

                    # Explanations and screenshots aren't processed like commands, so the text need not be surrounded
                    # by double quotes.
                    if command_name in ("explain", "screenshot"):
                        args.append(value)
                        continue

                    try:
                        if value[0] == '"':
                            args.append(value.replace('"', ""))
                        else:
                            args = value.split(" ")
                    except IndexError:
                        pass
                    except TypeError:
                        args.append(True)
                else:
                    _key, _value = self._get_key_value(key, value)
                    kwargs[_key] = _value

                count += 1

            self.commands.append((command_name, args, kwargs))

        self.is_loaded = True

        return True

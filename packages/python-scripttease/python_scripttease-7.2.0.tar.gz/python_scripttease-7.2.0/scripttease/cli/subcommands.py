# Imports

from commonkit import copy_tree, highlight_code, indent, write_file
from commonkit.shell import EXIT
from markdown import markdown
import os
from ..lib.factories import command_factory
from ..constants import PROFILE
from ..variables import PATH_TO_SCRIPT_TEASE

# Exports

__all__ = (
    "copy_inventory",
    "generate_docs",
    "generate_script",
)

# Functions


def copy_inventory(name, to_path=None):
    """Copy an inventory item to a path.

    :param name: The name of the inventory item. ``?`` will list available items.
    :type name: str

    :param to_path: The path to where the item should be copied. Defaults to the current working directory.
    :type to_path: str

    :rtype: int
    :returns: An exit code.

    """
    path = os.path.join(PATH_TO_SCRIPT_TEASE, "data", "inventory")
    if name == "?":
        for d in os.listdir(path):
            print(d)

        return EXIT.OK

    from_path = os.path.join(path, name)

    if to_path is None:
        to_path = os.path.join(os.getcwd(), name)
        os.makedirs(to_path)

    if copy_tree(from_path, to_path):
        return EXIT.OK

    return EXIT.ERROR


def generate_docs(loader, output_file=None, output_format="md", profile=PROFILE.UBUNTU):
    """Generate documentation from a commands file.

    :param loader: The loader instance.
    :type loader: BaseType[scripttease.lib.loaders.BaseLoader]

    :param output_file: The path to the output file.
    :type output_file: str

    :param output_format: The output format; ``html``, ``md`` (Markdown, the default), ``plain`` (text), ``rst``
                          (ReStructuredText).
    :type output_format: str

    :param profile: The operating system profile to use.
    :type profile: str

    :rtype: int
    :returns: An exit code.

    """
    commands = command_factory(loader, profile=profile)
    if commands is None:
        return EXIT.ERROR

    output = list()
    for command in commands:

        if command.name in ("explain", "screenshot"):
            output.append(command.get_output(output_format))
        elif command.name == "template":
            if output_format == "plain":
                output.append("+++")
                output.append(command.get_content())
                output.append("+++")
                output.append("")
            elif output_format == "rst":
                output.append(".. code-block:: %s" % command.get_target_language())
                output.append("")
                output.append(indent(command.get_content()))
                output.append("")
            else:
                output.append("```%s" % command.get_target_language())
                output.append(command.get_content())
                output.append("```")
                output.append("")
        else:
            statement = command.get_statement(include_comment=False, include_register=False, include_stop=False)
            if statement is not None:
                line = command.comment.replace("#", "")
                output.append("%s:" % line.capitalize())
                output.append("")
                if output_format == "plain":
                    output.append("---")
                    output.append(statement)
                    output.append("---")
                    output.append("")
                elif output_format == "rst":
                    output.append(".. code-block:: bash")
                    output.append("")
                    output.append(indent(statement))
                    output.append("")
                else:
                    output.append("```bash")
                    output.append(statement)
                    output.append("```")
                    output.append("")

    if output_format == "html":
        _output = markdown("\n".join(output), extensions=['fenced_code'])
    else:
        _output = "\n".join(output)

    print(_output)

    if output_file:
        write_file(output_file, _output)

    return EXIT.OK


def generate_script(loader, color_enabled=False, include_shebang=False, output_file=None, profile=PROFILE.UBUNTU):
    """Generate statements from a commands file.

    :param loader: The loader instance.
    :type loader: BaseType[scripttease.lib.loaders.BaseLoader]

    :param color_enabled: Colorize the output.
    :type color_enabled: bool

    :param include_shebang: Add the shebang to the beginning of the output.
    :type include_shebang: bool

    :param output_file: The path to the output file.
    :type output_file: str

    :param profile: The operating system profile to use.
    :type profile: str

    :rtype: int
    :returns: An exit code.

    """
    commands = command_factory(loader, profile=profile)
    if commands is None:
        return EXIT.ERROR

    output = list()
    if include_shebang:
        output.append("#! /usr/bin/env bash")

    for command in commands:
        if command.name in ("explain", "screenshot"):
            continue

        statement = command.get_statement(include_comment=True)
        if statement is not None:
            output.append(statement)
            output.append("")

    if color_enabled:
        print(highlight_code("\n".join(output), language="bash"))
    else:
        print("\n".join(output))

    if output_file:
        write_file(output_file, "\n".join(output))

    return EXIT.OK

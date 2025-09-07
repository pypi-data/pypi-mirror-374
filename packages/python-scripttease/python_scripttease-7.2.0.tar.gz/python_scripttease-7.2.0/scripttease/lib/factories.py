import logging
from ..constants import EXCLUDED_KWARGS, PROFILE
from ..exceptions import InvalidInput
from ..variables import LOGGER_NAME
from .commands.base import Command, ItemizedCommand, Template
from .commands.centos import CENTOS_MAPPINGS
from .commands.ubuntu import UBUNTU_MAPPINGS

log = logging.getLogger(LOGGER_NAME)


def command_factory(loader, excluded_kwargs=None, mappings=None, profile=PROFILE.UBUNTU):
    """Get command instances.

    :param loader: The loader instance used to generate commands.
    :type loader: BaseType[scripttease.lib.loaders.BaseLoader]

    :param excluded_kwargs: For commands that support ad hoc sub-commands (like Django), this is a list of keyword
                            argument names that must be removed. Defaults to the names of common command attributes.
                            If your implementation requires custom but otherwise standard command attributes, you'll
                            need to import the ``EXCLUDED_KWARGS`` constant and add your attribute names before
                            calling the command factory.
    :type excluded_kwargs: list[str]

    :param mappings: Additional command mappings which may be used to override or extend those provided by the selected
                     profile. This is a dictionary of the command name and the callback.
    :type mappings: dict

    :param profile: The operating system profile to use for finding commands.
    :type profile: str

    :returns: A list of instances that may be Command, ItemizedCommand, or Template.

    """
    # Identify the command mappings to be used.
    if profile in (PROFILE.CENTOS, PROFILE.FEDORA, PROFILE.REDHAT):
        _mappings = CENTOS_MAPPINGS
    elif profile in (PROFILE.DEBIAN, PROFILE.POP_OS, PROFILE.UBUNTU):
        _mappings = UBUNTU_MAPPINGS
    else:
        log.error("Unsupported or unrecognized profile: %s" % profile)
        return None

    # Update mappings if custom mappings have been supplied.
    if mappings is not None:
        _mappings.update(mappings)

    # Support custom exclusion of kwargs when instantiating a command instance. This is specific to the implementation
    # and is not used by scripttease CLI. Most callbacks will ignore this; however, those that support subcommands may
    # use this to identify keyword arguments that are standard to scripttease versus those that are custom.
    _excluded_kwargs = excluded_kwargs or EXCLUDED_KWARGS

    # Generate the command instances.
    commands = list()
    number = 1
    for command_name, args, kwargs in loader.commands:
        kwargs['excluded_kwargs'] = _excluded_kwargs

        try:
            command = get_command(_mappings, command_name, *args, locations=loader.locations, **kwargs)
        except TypeError as e:
            raise InvalidInput("The %s command in %s is not configured correctly: %s" % (command_name, loader.path, e))

        if command is not None:
            command.name = command_name
            command.number = number

            if command.name == "template":
                command.context.update(loader.get_context())

            commands.append(command)

            number += 1

    return commands


def get_command(mappings, name, *args, locations=None, **kwargs):
    """Get a command instance.

    :param mappings: The command mappings.
    :type mappings: dict

    :param name: The name of the command.
    :type name: str

    :param locations: A list of paths where templates may be found.
    :type locations: list[str]

    args and kwargs are passed to the callback.

    :rtype: scripttease.lib.commands.base.Command | scripttease.lib.commands.base.ItemizedCommand |
            scripttease.lib.commands.base.Template | scripttease.lib.commands.base.MultipleCommands

    """
    # Args need to be mutable.
    _args = list(args)

    # Handle templates special.
    if name == "template":
        source = _args.pop(0)
        target = _args.pop(0)
        return Template(source, target, locations=locations, **kwargs)

    # Command is not recognized, is spelled wrong, etc.
    if name not in mappings:
        log.warning("Command does not exist: %s" % name)
        return None

    callback = mappings[name]

    # Itemization wraps the callback.
    if "items" in kwargs:
        items = kwargs.pop("items")
        return ItemizedCommand(callback, items, *args, **kwargs)

    # The callback generates the Command instance.
    return callback(*args, **kwargs)

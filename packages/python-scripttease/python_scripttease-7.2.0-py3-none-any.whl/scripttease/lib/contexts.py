# Imports

import logging

log = logging.getLogger(__name__)

# Exports

__all__ = (
    "Context",
    "Variable",
)


# Classes


class Context(object):
    """A collection of context variables."""

    def __init__(self):
        """Initialize the context."""
        self.is_loaded = False
        self.variables = dict()

    def __getattr__(self, item):
        return self.variables.get(item)

    def add(self, name, value, **kwargs):
        """Add a variable to the context.

        :param name: The name of the variable.
        :type name: str

        :param value: The value of the variable.

        :rtype: scripttease.lib.contexts.Variable

        kwargs are passed to instantiate the Variable.

        """
        v = Variable(name, value, **kwargs)
        self.variables[name] = v

        return v

    def append(self, variable):
        """Append a variable to the context.

        :param variable: The variable to be added to the context.
        :type variable: scripttease.lib.contexts.Variable

        """
        self.variables[variable.name] = variable

    def mapping(self):
        """Get the context as a dictionary.

        :rtype: dict

        """
        d = dict()
        for name, variable in self.variables.items():
            d[name] = variable.value

        return d


class Variable(object):
    """An individual variable."""

    def __init__(self, name, value, environment=None, **kwargs):
        """Initialize a variable.

        :param name: The name of the variable.
        :type name: str

        :param value: The value of the variable.

        :param environment: The environment in which the variable is used.
        :type environment: str

        kwargs are available as dynamic attributes.

        """
        self.environment = environment
        self.name = name
        self.value = value

        self.attributes = kwargs

    def __getattr__(self, item):
        return self.attributes.get(item)

    def __str__(self):
        return str(self.value)

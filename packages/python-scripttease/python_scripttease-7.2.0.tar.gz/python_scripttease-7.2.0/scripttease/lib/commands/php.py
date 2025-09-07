from .base import Command


def php_module(name, **kwargs):
    """Enable a PHP module.

    :param name: The module name.
    :type name: str

    """
    statement = "phpenmod %s" % name

    return Command(statement, **kwargs)


PHP_MAPPINGS = {
    'php.module': php_module,
}

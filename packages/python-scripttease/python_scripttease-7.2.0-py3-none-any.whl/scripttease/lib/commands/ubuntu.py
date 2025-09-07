# Imports

from commonkit import split_csv
from .base import Command
from .django import DJANGO_MAPPINGS
from .messages import MESSAGE_MAPPINGS
from .mysql import MYSQL_MAPPINGS
from .pgsql import PGSQL_MAPPINGS
from .php import PHP_MAPPINGS
from .posix import POSIX_MAPPINGS
from .python import PYTHON_MAPPINGS

# Exports

__all__ = (
    "UBUNTU_MAPPINGS",
    "apache",
    "apache_disable_module",
    "apache_disable_site",
    "apache_enable_module",
    "apache_enable_site",
    "apache_reload",
    "apache_restart",
    "apache_start",
    "apache_stop",
    "apache_test",
    "service_reload",
    "service_restart",
    "service_start",
    "service_stop",
    "system",
    "system_install",
    "system_reboot",
    "system_update",
    "system_upgrade",
    "system_uninstall",
    # "template",
    "user",
)

# Functions


def apache(op, **kwargs):
    """Execute an Apache-related command.

    :param op: The operation to perform; ``reload``, ``restart``, ``start``, ``stop``, ``test``.
    :type op: str

    """
    if op == "reload":
        return apache_reload(**kwargs)
    elif op == "restart":
        return apache_restart(**kwargs)
    elif op == "start":
        return apache_start(**kwargs)
    elif op == "stop":
        return apache_stop(**kwargs)
    elif op == "test":
        return apache_test(**kwargs)
    else:
        raise NameError("Unrecognized or unsupported apache operation: %s" % op)


def apache_disable_module(module, **kwargs):
    """Disable an Apache module.

    :param module: The name of the module.
    :type module: str

    """
    kwargs.setdefault("comment", "disable %s apache module" % module)

    return Command("a2dismod %s" % module, **kwargs)


def apache_disable_site(site, **kwargs):
    """Disable an Apache site.

    :param site: The site/domain name.
    :type site: str

    """
    kwargs.setdefault("comment", "disable %s apache site" % site)

    return Command("a2dissite %s" % site, **kwargs)


def apache_enable_module(module, **kwargs):
    """Enable an Apache module.

    :param module: The name of the module.
    :type module: str

    """
    kwargs.setdefault("comment", "enable %s apache module" % module)

    return Command("a2enmod %s" % module, **kwargs)


def apache_enable_site(site, **kwargs):
    """Enable an Apache site.

    :param site: The site/domain name.
    :type site: str

    """
    kwargs.setdefault("comment", "enable %s apache module" % site)

    return Command("a2ensite %s" % site, **kwargs)


def apache_reload(**kwargs):
    """Reload the apache service."""
    kwargs.setdefault("comment", "reload apache")
    kwargs.setdefault("register", "apache_reloaded")

    return Command("service apache2 reload", **kwargs)


def apache_restart(**kwargs):
    """Restart the apache service."""
    kwargs.setdefault("comment", "restart apache")
    kwargs.setdefault("register", "apache_restarted")

    return Command("service apache2 restart", **kwargs)


def apache_start(**kwargs):
    """Start the apache service."""
    kwargs.setdefault("comment", "start apache")
    kwargs.setdefault("register", "apache_started")

    return Command("service apache2 start", **kwargs)


def apache_stop(**kwargs):
    """Stop the apache service."""
    kwargs.setdefault("comment", "stop apache")

    return Command("service apache2 stop", **kwargs)


def apache_test(**kwargs):
    """Run a configuration test on apache."""
    kwargs.setdefault("comment", "check apache configuration")
    kwargs.setdefault("register", "apache_checks_out")

    return Command("apachectl configtest", **kwargs)


def service_reload(service, **kwargs):
    """Reload a service.

    :param service: The service name.
    :type service: str

    """
    kwargs.setdefault("comment", "reload %s service" % service)
    kwargs.setdefault("register", "%s_reloaded" % service)

    return Command("service %s reload" % service, **kwargs)


def service_restart(service, **kwargs):
    """Restart a service.

    :param service: The service name.
    :type service: str

    """
    kwargs.setdefault("comment", "restart %s service" % service)
    kwargs.setdefault("register", "%s_restarted" % service)

    return Command("service %s restart" % service, **kwargs)


def service_start(service, **kwargs):
    """Start a service.

    :param service: The service name.
    :type service: str

    """
    kwargs.setdefault("comment", "start %s service" % service)
    kwargs.setdefault("register", "%s_started" % service)

    return Command("service %s start" % service, **kwargs)


def service_stop(service, **kwargs):
    """Stop a service.

    :param service: The service name.
    :type service: str

    """
    kwargs.setdefault("comment", "stop %s service" % service)
    kwargs.setdefault("register", "%s_stopped" % service)

    return Command("service %s stop" % service, **kwargs)


def system(op, **kwargs):
    """Perform a system operation.

    :param op: The operation to perform; ``reboot``, ``update``, ``upgrade``.
    :type op: str

    """
    if op == "reboot":
        return system_reboot(**kwargs)
    elif op == "update":
        return system_update(**kwargs)
    elif op == "upgrade":
        return system_upgrade(**kwargs)
    else:
        raise NameError("Unrecognized or unsupported system operation: %s" % op)


def system_install(package, **kwargs):
    """Install a system-level package.

    :param package: The name of the package to install.
    :type package: str

    """
    kwargs.setdefault("comment", "install system package %s" % package)

    return Command("apt install -y %s" % package, **kwargs)


def system_reboot(**kwargs):
    """Reboot the system."""
    kwargs.setdefault("comment", "reboot the system")

    return Command("reboot", **kwargs)


def system_uninstall(package, **kwargs):
    """Uninstall a system-level package.

    :param package: The name of the package to remove.
    :type package: str

    """
    kwargs.setdefault("comment", "remove system package %s" % package)

    return Command("apt uninstall -y %s" % package, **kwargs)


def system_update(**kwargs):
    """Update the system's package info."""
    kwargs.setdefault("comment", "update system package info")

    return Command("apt update -y", **kwargs)


def system_upgrade(**kwargs):
    """updated the system."""
    kwargs.setdefault("comment", "upgrade the system")

    return Command("apt upgrade -y", **kwargs)


def user(name, groups=None, home=None, op="add", password=None, **kwargs):
    """Create or remove a user.

    :param name: The username.
    :type name: str

    :param groups: A list of groups to which the user should belong.
    :type groups: list | str

    :param home: The path to the user's home directory.
    :type home: str

    :param op: The operation to perform; ``add`` or ``remove``.
    :type op:

    :param password: The user's password. (NOT IMPLEMENTED)
    :type password: str

    """
    if op == "add":
        kwargs.setdefault("comment", "create a user named %s" % name)

        commands = list()

        # The gecos switch eliminates the prompts.
        a = list()
        a.append('adduser %s --disabled-password --gecos ""' % name)
        if home is not None:
            a.append("--home %s" % home)

        commands.append(Command(" ".join(a), **kwargs))

        if type(groups) is str:
            groups = split_csv(groups, smart=False)

        if type(groups) in [list, tuple]:
            for group in groups:
                commands.append(Command("adduser %s %s" % (name, group), **kwargs))

        a = list()
        for c in commands:
            a.append(c.get_statement(include_comment=True))

        return Command("\n".join(a), name="user_add", **kwargs)
    elif op == "remove":
        kwargs.setdefault("comment", "remove a user named %s" % name)
        return Command("deluser %s" % name, name="user_remove", **kwargs)
    else:
        raise NameError("Unsupported or unrecognized operation: %s" % op)


UBUNTU_MAPPINGS = {
    'apache': apache,
    'apache.disable_module': apache_disable_module,
    'apache.disable_site': apache_disable_site,
    'apache.enable_module': apache_enable_module,
    'apache.enable_site': apache_enable_site,
    'apache.reload': apache_reload,
    'apache.restart': apache_restart,
    'apache.start': apache_start,
    'apache.stop': apache_stop,
    'apache.test': apache_test,
    'install': system_install,
    'reboot': system_reboot,
    'reload': service_reload,
    'restart': service_restart,
    'start': service_start,
    'stop': service_stop,
    'system': system,
    'update': system_update,
    'uninstall': system_uninstall,
    'upgrade': system_upgrade,
    'user': user,
}

UBUNTU_MAPPINGS.update(DJANGO_MAPPINGS)
UBUNTU_MAPPINGS.update(MESSAGE_MAPPINGS)
UBUNTU_MAPPINGS.update(MYSQL_MAPPINGS)
UBUNTU_MAPPINGS.update(PGSQL_MAPPINGS)
UBUNTU_MAPPINGS.update(PHP_MAPPINGS)
UBUNTU_MAPPINGS.update(POSIX_MAPPINGS)
UBUNTU_MAPPINGS.update(PYTHON_MAPPINGS)

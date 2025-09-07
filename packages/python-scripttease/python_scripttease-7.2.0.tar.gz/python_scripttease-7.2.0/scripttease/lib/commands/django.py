from ...constants import EXCLUDED_KWARGS
from .base import Command


def django(management_command, *args, excluded_kwargs=None, **kwargs):
    """Common function for assembling Django management commands.

    :param management_command: The name of the management command.
    :type management_command: str

    :param excluded_kwargs: A dictionary of kwargs that should be excluded from the management command parameters.
    :param excluded_kwargs: dict

    :rtype: scripttease.lib.commands.base.Command

    If provided, args are passed directly to the command as positional parameters.

    Any provided kwargs are converted to long form parameters. For example, database="alternative_db" becomes
    ``--database="alternative_db"``.

    A kwarg with a ``True`` value becomes a long form parameter with no value. For example, natural_foreign=True becomes
    ``--natural-foreign``.

    Finally, any kwarg that is not a string is passed without quotes. For example, testing=1 becomes ``--testing=1``.

    """
    # The excluded parameters (filtered below) may vary based on implementation. We do, however, need a default.
    excluded_kwargs = excluded_kwargs or EXCLUDED_KWARGS

    venv = kwargs.pop("venv", None)
    if venv is not None:
        kwargs['prefix'] = "source %s/bin/activate" % venv

    # Django's management commands can have a number of options. We need to filter out internal parameters so that these
    # are not used as options for the management command.
    _kwargs = dict()
    for key in excluded_kwargs:
        if key in kwargs:
            _kwargs[key] = kwargs.pop(key)

    if 'comment' not in _kwargs:
        _kwargs['comment'] = "run %s django management command" % management_command

    a = list()
    a.append("./manage.py %s" % management_command)
    for key, value in kwargs.items():
        key = key.replace("_", "-")
        if type(value) is bool and value is True:
            a.append("--%s" % key)
        elif type(value) is str:
            a.append('--%s="%s"' % (key, value))
        else:
            a.append('--%s=%s' % (key, value))

    _args = list(args)
    if len(_args) > 0:
        a.append(" ".join(_args))

    statement = " ".join(a)

    return Command(statement, **_kwargs)


def django_check(**kwargs):
    """Run Django checks."""
    kwargs.setdefault("comment", "run django checks")
    kwargs.setdefault("register", "django_checks_out")
    return django("check", **kwargs)


def django_createsuperuser(username, email=None, **kwargs):
    """Create a superuser account.

    :param username: The name for the user account.
    :type username: str

    :param email: The user's email address. Optional, but recommended because the account must be created without a
                  password.
    :type email: str

    """
    kwargs.setdefault("comment", "create the %s superuser" % username)
    kwargs['username'] = username
    kwargs['noinput'] = True

    if email is not None:
        kwargs['email'] = email

    return django("createsuperuser", **kwargs)


def django_dump(target, path=None, **kwargs):
    """Dump data fixtures.

    :param target: The app name or ``app.ModelName``.
    :type target: str

    :param path: The path to the fixture file.
    :type path: str

    """
    kwargs.setdefault("comment", "dump app/model data for %s" % target)
    kwargs.setdefault("format", "json")
    kwargs.setdefault("indent", 4)

    app = target
    file_name = "%s/initial.%s" % (app, kwargs['format'])
    if "." in target:
        app, model = target.split(".")
        file_name = "%s/%s.%s" % (app, model.lower(), kwargs['format'])

    if path is None:
        path = "../fixtures/%s" % file_name

    return django("dumpdata", target, "> %s" % path, **kwargs)


def django_load(target, path=None, **kwargs):
    """Load data fixtures.

    :param target: The app name or ``app.ModelName``.
    :type target: str

    :param path: The path to the fixture file.
    :type path: str

    """
    kwargs.setdefault("comment", "load app/model data from %s" % target)
    input_format = kwargs.pop("format", "json")

    app = target
    file_name = "%s/initial.%s" % (app, input_format)
    if "." in target:
        app, model = target.split(".")
        file_name = "%s/%s.%s" % (app, model.lower(), input_format)

    if path is None:
        path = "../fixtures/%s" % file_name

    return django("loaddata", path, **kwargs)


def django_migrate(**kwargs):
    """Apply database migrations."""
    kwargs.setdefault("comment", "apply database migrations")
    return django("migrate", **kwargs)


def django_static(**kwargs):
    """Collect static files."""
    kwargs.setdefault("comment", "collect static files")
    kwargs.setdefault("noinput", True)
    return django("collectstatic", **kwargs)


DJANGO_MAPPINGS = {
    'django': django,
    'django.check': django_check,
    'django.collectstatic': django_static,
    'django.createsuperuser': django_createsuperuser,
    'django.dump': django_dump,
    'django.dumpdata': django_dump,
    'django.load': django_load,
    'django.loaddata': django_load,
    'django.migrate': django_migrate,
    'django.static': django_static,
}

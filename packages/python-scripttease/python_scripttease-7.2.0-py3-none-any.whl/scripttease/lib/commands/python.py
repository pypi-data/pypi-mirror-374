from .base import Command


def python_pip(name, op="install", tmp_dir=None, upgrade=False, venv=None, version=3, **kwargs):
    """Use pip to install or uninstall a Python package.

    :param name: The name of the package.
    :type name: str

    :param op: The operation to perform; ``install``, ``remove``
    :type op: str

    :param tmp_dir: The temporary directory to use when downloading packages. This may be required when packages are too
                    large for the system's temporary space.
    :type tmp_dir: str

    :param upgrade: Upgrade an installed package.
    :type upgrade: bool

    :param venv: The name of the virtual environment to load.
    :type venv: str

    :param version: The Python version to use, e.g. ``2`` or ``3``.
    :type version: int

    """
    manager = "pip"
    if version == 3:
        manager = "pip3"

    if upgrade:
        statement = "%s install --upgrade %s" % (manager, name)
    else:
        statement = "%s %s %s" % (manager, op, name)

    prefix = None
    if tmp_dir is not None or venv is not None:
        prefix = list()

    if tmp_dir is not None:
        prefix.append('export TMPDIR="%s"' % tmp_dir)

    if venv is not None:
        prefix.append("source %s/bin/activate" % venv)

    if prefix is not None:
        kwargs['prefix'] = "&& ".join(prefix)

    kwargs.setdefault("comment", "%s %s" % (op, name))

    return Command(statement, **kwargs)


def python_pip_file(path, tmp_dir=None, venv=None, version=3, **kwargs):
    """Install Python packages from a pip file.

    :param path: The path to the file.
    :type path: str

    :param tmp_dir: The temporary directory to use when downloading packages. This may be required when packages are too
                    large for the system's temporary space.
    :type tmp_dir: str

    :param venv: The name (and/or path) of the virtual environment.
    :type venv: str

    :param version: The pip version to use.

    """
    manager = "pip"
    if version == 3:
        manager = "pip3"

    prefix = None
    if tmp_dir is not None or venv is not None:
        prefix = list()

    if tmp_dir is not None:
        prefix.append('export TMPDIR="%s"' % tmp_dir)

    if venv is not None:
        prefix.append("source %s/bin/activate" % venv)

    if prefix is not None:
        kwargs['prefix'] = "&& ".join(prefix)

    kwargs.setdefault("comment", "install packages from pip file %s" % path)

    statement = "%s install -r %s" % (manager, path)

    return Command(statement, **kwargs)


def python_virtualenv(name, **kwargs):
    """Create a Python virtual environment.

    :param name: The name of the environment to create.
    :type name: str

    """
    kwargs.setdefault("comment", "create %s virtual environment" % name)

    return Command("virtualenv %s" % name, **kwargs)


PYTHON_MAPPINGS = {
    'pip': python_pip,
    'pipf': python_pip_file,
    'pip_file': python_pip_file,
    'virtualenv': python_virtualenv,
}

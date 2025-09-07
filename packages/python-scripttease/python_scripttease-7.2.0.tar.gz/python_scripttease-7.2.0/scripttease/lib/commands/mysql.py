# Imports

from ...constants import EXCLUDED_KWARGS
from ...exceptions import InvalidInput
from .base import Command

# Exports

__all__ = (
    "MYSQL_MAPPINGS",
    "mysql_create",
    "mysql_drop",
    "mysql_dump",
    "mysql_exists",
    "mysql_grant",
    "mysql_load",
    "mysql_user",
)


def mysql(command, *args, excluded_kwargs=None, host="localhost", password=None, port=3306, user="root", **kwargs):
    """Get a mysql-related command using commonly required parameters.

    :param command: The name of the command.
    :type command: str

    :param excluded_kwargs: Keyword arguments to exclude from automatic switch creation.
    :type excluded_kwargs: list[str]

    :param host: The host name.
    :type host: str

    :param password: The password to use.
    :type password: str

    :param port: The TCP port number.
    :type port: int

    :param user: The username that will be used to execute the command.

    """
    # The excluded parameters (filtered below) may vary based on implementation. We do, however, need a default.
    excluded_kwargs = excluded_kwargs or EXCLUDED_KWARGS

    # if 'comment' not in kwargs:
    #     kwargs['comment'] = "run %s mysql command" % command

    # Allow additional command line switches to pass through?
    # Django's management commands can have a number of options. We need to filter out internal parameters so that these
    # are not used as options for the management command.
    _kwargs = dict()
    for key in excluded_kwargs:
        if key in kwargs:
            _kwargs[key] = kwargs.pop(key)

    # MySQL commands always run without sudo because the --user may be provided.
    _kwargs['sudo'] = False

    a = list()

    a.append(command)
    a.append("--user %s --host=%s --port=%s" % (user, host, port))
    
    if password:
        a.append('--password="%s"' % password)
    
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


def mysql_create(database, owner=None, **kwargs):
    """Create a MySQL database.

    :param database: The database name.
    :type database: str

    :param owner: The owner (user/role name) of the new database.
    :type owner: str

    """
    kwargs.setdefault("comment", "create mysql database")

    command = mysql("mysqladmin create", database, **kwargs)
    
    if owner is not None:
        grant = mysql_grant(owner, database=database, **kwargs)
        command.statement += " && " + grant.statement
        
    return command


def mysql_drop(database, **kwargs):
    """Remove a MySQL database.

    :param database: The database name.
    :type database: str

    """
    kwargs.setdefault("comment", "drop %s mysql database" % database)

    return mysql("mysqladmin drop", database, **kwargs)


def mysql_dump(database, path=None, **kwargs):
    """Export a MySQL database.

    :param database: The database name.
    :type database: str

    :param path: The name/path of the export file. Defaults the database name plus ``.sql``.
    :type path: str

    """
    kwargs.setdefault("comment", "dump mysql database")

    if path is None:
        path = "%s.sql" % database

    return mysql("mysqldump", database, "> %s" % path, **kwargs)


def mysql_exists(database, **kwargs):
    """Determine if a MySQL database exists.

    :param database: The database name.
    :type database: str

    """
    kwargs.setdefault("comment", "determine if %s mysql database exists" % database)
    kwargs.setdefault("register", "%s_exists" % database)

    command = mysql("mysql", **kwargs)
    
    sql = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '%s'" % database
    
    command.statement += '--execute="%s"' % sql
    
    return command


def mysql_grant(to, database=None, privileges="ALL", **kwargs):
    """Grant privileges to a user.

    :param to: The username to which privileges are granted.
    :type to: str

    :param database: The database name.
    :type database: str

    :param privileges: The privileges to be granted.
    :type privileges: str

    """
    kwargs.setdefault("comment", "grant mysql privileges to %s" % to)

    host = kwargs.get("host", "localhost")

    command = mysql("mysql", **kwargs)

    # See https://dev.mysql.com/doc/refman/5.7/en/grant.html
    _database = database or "*"
    sql = "GRANT %(privileges)s ON %(database)s.* TO '%(user)s'@'%(host)s'" % {
        'database': _database,
        'host': host,
        'privileges': privileges,
        'user': to,
    }
    command.statement += ' --execute="%s"' % sql

    return command


def mysql_load(database, path, **kwargs):
    """Load data into a MySQL database.

    :param database: The database name.
    :type database: str

    :param path: The path to the file to be loaded.
    :type path: str

    """
    kwargs.setdefault("comment", "load data into a mysql database")

    return mysql("mysql", database, "< %s" % path, **kwargs)


def mysql_user(name, admin_pass=None, admin_user="root", op="create", password=None, **kwargs):
    """Work with a MySQL user.

    :param name: The username.
    :type name: str

    :param admin_pass: The password for the user with admin privileges.
    :type admin_pass: str

    :param admin_user: The username of the user with admin privileges.
    :type admin_user: str

    :param op: The operation to perform: ``create``, ``drop``, ``exists``.
    :type op: str

    :param password: The password for a new user.
    :type password: str

    """
    host = kwargs.get("host", "localhost")

    if op == "create":
        kwargs.setdefault("comment", "create %s mysql user" % name)

        command = mysql("mysql", password=admin_pass, user=admin_user, **kwargs)

        sql = "CREATE USER IF NOT EXISTS '%s'@'%s'" % (name, host)
        if password is not None:
            sql += " IDENTIFIED BY PASSWORD('%s')" % password

        command.statement += ' --execute="%s"' % sql

        return command
    elif op == "drop":
        kwargs.setdefault("comment", "remove %s mysql user" % name)

        command = mysql("mysql", password=admin_pass, user=admin_user, **kwargs)

        sql = "DROP USER IF EXISTS '%s'@'%s'" % (name, host)

        command.statement += ' --execute="%s"' % sql

        return command
    elif op == "exists":
        kwargs.setdefault("comment", "determine if %s mysql user exists" % name)
        kwargs.setdefault("register", "mysql_user_exists")

        command = mysql("mysql", password=admin_pass, user=admin_user, **kwargs)

        sql = "SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '%s')" % name

        command.statement += ' --execute "%s"' % sql

        return command
    else:
        raise InvalidInput("Unrecognized or unsupported MySQL user operation: %s" % op)


MYSQL_MAPPINGS = {
    'mysql.create': mysql_create,
    'mysql.drop': mysql_drop,
    'mysql.dump': mysql_dump,
    'mysql.exists': mysql_exists,
    'mysql.grant': mysql_grant,
    # 'mysql.sql': mysql_exec,
    'mysql.user': mysql_user,
}

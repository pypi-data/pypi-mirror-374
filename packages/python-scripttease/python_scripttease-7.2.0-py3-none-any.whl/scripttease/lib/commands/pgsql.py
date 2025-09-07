"""

"""
from ...constants import EXCLUDED_KWARGS
from ...exceptions import InvalidInput
from .base import Command


__all__ = (
    "PGSQL_MAPPINGS",
    "pgsql_create",
    "pgsql_drop",
    "pgsql_dump",
    "pgsql_exists",
    "pgsql_grant",
    "pgsql_load",
    "pgsql_sql",
    "pgsql_user",
)


def pgsql(command, *args, excluded_kwargs=None, host="localhost", password=None, port=5432, user="postgres", **kwargs):
    """Get a postgres-related command using commonly required parameters.

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
    #     kwargs['comment'] = "run %s postgres command" % command

    # Allow additional command line switches to pass through?
    _kwargs = dict()
    for key in excluded_kwargs:
        if key in kwargs:
            _kwargs[key] = kwargs.pop(key)

    # Postgres commands always run without sudo because the -U may be provided.
    _kwargs['sudo'] = False

    a = list()

    # Password may be None or an empty string.
    if password:
        a.append('export PGPASSWORD="%s" &&' % password)

    a.append(command)
    a.append("-U %s --host=%s --port=%s" % (user, host, port))
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


def pgsql_create(database, owner=None, template=None, **kwargs):
    """Create a PostgreSQL database.

    :param database: The database name.
    :type database: str

    :param owner: The owner (user/role name) of the new database.
    :type owner: str

    :param template: The database template name to use, if any.
    :type template: str

    """
    kwargs.setdefault("comment", "create %s postgres database" % database)

    if owner is not None:
        kwargs['owner'] = owner

    if template is not None:
        kwargs['template'] = template

    # SELECT 'CREATE DATABASE <db_name>'
    # WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '<db_name>')\gexec

    # psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '<your db name>'" | grep -q 1 | psql -U postgres -c "CREATE DATABASE <your db name>"
    # first = pgsql("psql", **kwargs)
    #
    # first_query = "SELECT 1 FROM pg_database WHERE datname = '%s'" % database
    # first_statement = '%s -tc "%s" | grep -q 1' % (first.statement, first_query)
    #
    # kwargs_without_password = kwargs.copy()
    # if 'password' in kwargs_without_password:
    #     kwargs_without_password.pop("password")
    #
    # second = pgsql("psql", **kwargs_without_password)
    # second_statement = '%s -c "CREATE DATABASE %s"' % (second.statement, database)
    #
    # final_statement = "%s | %s" % (first_statement, second_statement)
    # return Command(final_statement, **kwargs)

    return pgsql("createdb", database, **kwargs)


def pgsql_drop(database, **kwargs):
    """Remove a PostgreSQL database.

    :param database: The database name.
    :type database: str

    """
    kwargs.setdefault("comment", "drop %s postgres database" % database)

    return pgsql("dropdb", database, **kwargs)


def pgsql_dump(database, path=None, **kwargs):
    """Export a PostgreSQL database.

    :param database: The database name.
    :type database: str

    :param path: The name/path of the export file. Defaults the database name plus ``.sql``.
    :type path: str

    """
    kwargs.setdefault("comment", "dump postgres database")
    kwargs.setdefault("column_inserts", True)

    if path is None:
        path = "%s.sql" % database

    kwargs['dbname'] = database
    kwargs['file'] = path

    return pgsql("pg_dump", **kwargs)


def pgsql_exists(database, **kwargs):
    """Determine if a PostgreSQL database exists.

    :param database: The database name.
    :type database: str

    """
    kwargs.setdefault("comment", "determine if %s postgres database exists" % database)
    kwargs.setdefault("register", "%s_exists" % database)

    command = pgsql("psql", **kwargs)
    command.statement += r" -lqt | cut -d \| -f 1 | grep -qw %s" % database

    return command


def pgsql_grant(to, database=None, privileges="ALL", schema=None, table=None, **kwargs):
    """Grant privileges to a user.

    :param to: The username to which privileges are granted.
    :type to: str

    :param database: The database name. Required.
    :type database: str

    :param privileges: The privileges to be granted. See https://www.postgresql.org/docs/current/sql-grant.html
    :type privileges: str

    :param schema: The schema to which the privileges apply.
    :type schema: str

    :param table: The table name to which privileges apply.
    :type table: str

    .. note::
        A schema or table is required and the privileges must be compatible with the target object.

    """
    if database is None:
        raise InvalidInput("Database is required.")

    kwargs.setdefault("comment", "grant postgres privileges to %s" % to)
    kwargs['dbname'] = database

    if schema is not None:
        target = "SCHEMA %s" % schema
    elif table is not None:
        target = "TABLE %s" % table
    else:
        raise InvalidInput("Either schema or table is required.")

    _privileges = privileges
    if privileges.lower() == "all":
        _privileges = "ALL PRIVILEGES"

    # See https://www.postgresql.org/docs/current/sql-grant.html
    sql = "GRANT %(privileges)s ON %(target)s TO %(user)s" % {
        'privileges': _privileges,
        'target': target,
        'user': to,
    }

    command = pgsql("psql", **kwargs)
    command.statement += ' -c "%s"' % sql

    return command


def pgsql_load(database, path, **kwargs):
    """Load data into a PostgreSQL database.

    :param database: The database name.
    :type database: str

    :param path: The path to the file to be loaded.
    :type path: str

    """
    kwargs.setdefault("comment", "load data into a postgres database")

    kwargs['dbname'] = database
    kwargs['file'] = path

    return pgsql("psql", **kwargs)


def pgsql_sql(statement, database="template1", **kwargs):
    kwargs.setdefault("comment", "run SQL statement")

    kwargs['dbname'] = database

    command = pgsql("psql", **kwargs)
    command.statement += ' -c "%s"' % statement

    return command


def pgsql_user(name, admin_pass=None, admin_user="postgres", op="create", password=None, **kwargs):
    """Work with a PostgreSQL user.

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
    if op == "create":
        kwargs.setdefault("comment", "create %s postgres user" % name)

        command = pgsql("createuser", "-DRS %s" % name, password=admin_pass, user=admin_user, **kwargs)

        if password is not None:
            extra = pgsql("psql", password=admin_pass, user=admin_user, **kwargs)
            command.statement += " && " + extra.statement
            command.statement += " -c \"ALTER USER %s WITH ENCRYPTED PASSWORD '%s';\"" % (name, password)

        return command
    elif op in ("drop", "remove"):
        kwargs.setdefault("comment", "remove %s postgres user" % name)

        return pgsql("dropuser", name, password=admin_pass, user=admin_user, **kwargs)
    elif op == "exists":
        kwargs.setdefault("comment", "determine if %s postgres user exists" % name)
        kwargs.setdefault("register", "pgsql_user_exists")

        command = pgsql("psql", password=admin_pass, user=admin_user, **kwargs)

        sql = "SELECT 1 FROM pgsql_roles WHERE rolname='%s'" % name

        command.statement += ' -c "%s"' % sql

        return command
    else:
        raise InvalidInput("Unrecognized or unsupported Postgres user operation: %s" % op)


PGSQL_MAPPINGS = {
    'pgsql.create': pgsql_create,
    'pgsql.drop': pgsql_drop,
    'pgsql.dump': pgsql_dump,
    'pgsql.exists': pgsql_exists,
    'pgsql.grant': pgsql_grant,
    'pgsql.sql': pgsql_sql,
    'pgsql.user': pgsql_user,
}

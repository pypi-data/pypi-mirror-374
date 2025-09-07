# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2023 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Fabric Library for MySQL
"""

import re

from rattail_fabric2 import apt, make_deploy, sed


deploy = make_deploy(__file__)


def install(c):
    """
    Install the MySQL database service
    """
    # TODO: must install 'mysql-server' instead for Ubuntu 16.04
    apt.install(c, 'default-mysql-server')


def get_version_string(c):
    """
    Fetch the version of MySQL running on the target system
    """
    result = c.sudo('mysql --version', warn=True)
    if not result.failed:
        # match = re.match(r'^mysql .*?(\d+\.\d+\.\d+)-MariaDB', result.stdout)
        match = re.match(r'^mysql +Ver +(\d+\.\d+\.\d+)-.*', result.stdout)
        if match:
            return match.group(1)


def set_bind_address(c, address):
    """
    Configure the 'bind-address' setting with the given value.
    """
    sed(c, '/etc/mysql/my.cnf',
        '^bind-address.*',
        'bind-address = {}'.format(address),
        use_sudo=True)


def restart(c):
    """
    Restart the MySQL database service
    """
    c.sudo('systemctl restart mysql.service')


def user_exists(c, name, host='localhost'):
    """
    Determine if a given MySQL user exists.
    """
    user = sql(c, "SELECT User FROM user WHERE User = '{0}' and Host = '{1}'".format(name, host), database='mysql').stdout.strip()
    return user == name


def create_user(c, name, host='localhost', password=None, checkfirst=True):
    """
    Create a MySQL user account.
    """
    if not checkfirst or not user_exists(c, name, host):
        sql(c, "CREATE USER '{}'@'{}';".format(name, host))
    if password:
        # supposedly this is the new way to do it
        result = sql(c, "ALTER USER '{}'@'{}' IDENTIFIED BY '{}';".format(
            name, host, password),
            echo=False, hide=True, warn=True)
        if result.failed: # but this may fail for older systems
            # in which case we try it the old way
            sql(c, "SET PASSWORD FOR '{}'@'{}' = PASSWORD('{}');".format(
                name, host, password),
                echo=False, hide=True)


def db_exists(c, name):
    """
    Determine if a given MySQL database exists.
    """
    db = sql(c, "SELECT SCHEMA_NAME FROM SCHEMATA WHERE SCHEMA_NAME = '{0}'".format(name), database='information_schema').stdout.strip()
    return db == name


def create_db(c, name, checkfirst=True, user=None):
    """
    Create a MySQL database.
    """
    if not checkfirst or not db_exists(c, name):
        # note, we force sudo "as root" to ensure -H flag is used
        # (which allows us to leverage /root/.my.cnf config file)
        c.sudo('mysqladmin create {}'.format(name), user='root')
        if user:
            grant_access(c, name, user)


def drop_db(c, name, checkfirst=True):
    """
    Drop a MySQL database.
    """
    if not checkfirst or db_exists(c, name):
        # note, we force sudo "as root" to ensure -H flag is used
        # (which allows us to leverage /root/.my.cnf config file)
        c.sudo('mysqladmin drop --force {}'.format(name), user='root')


def grant_access(c, dbname, username):
    """
    Grant full access to the given database for the given user.  Note that the
    username should be given in MySQL's native format, e.g. 'myuser@localhost'.
    """
    sql(c, 'grant all on `{}`.* to {}'.format(dbname, username))


def table_exists(c, tblname, dbname):
    """
    Determine if given table exists in given DB.
    """
    # TODO: should avoid sql injection here...
    query = "SELECT TABLE_NAME FROM TABLES WHERE TABLE_SCHEMA = '{}' AND TABLE_NAME = '{}'".format(dbname, tblname)
    name = sql(c, query, database='information_schema').stdout.strip()
    return name == tblname


def sql(c, sql, database='', **kwargs):
    """
    Execute some SQL.
    """
    # some crazy quoting required here, see also
    # http://stackoverflow.com/a/1250279
    sql = sql.replace("'", "'\"'\"'")
    # note, we force sudo "as root" to ensure -H flag is used
    # (which allows us to leverage /root/.my.cnf config file)
    kwargs['user'] = 'root'
    return c.sudo("mysql --execute='{}' --batch --skip-column-names {}".format(sql, database), **kwargs)


def script(c, path, database=''):
    """
    Execute a SQL script against the given database.
    """
    c.sudo("bash -c 'mysql {} < {}'".format(database, path))


def dump_db(c, name, skip_triggers=False):
    """
    Dump a database to file, on the server represented by ``c`` param.

    This function returns the name of the DB dump file.  The name will
    not have a path component as it's assumed to be in the home folder
    of the connection user.
    """
    skip_triggers = '--skip-triggers' if skip_triggers else ''
    # note, we force sudo "as root" to ensure -H flag is used
    # (which allows us to leverage /root/.my.cnf config file)
    c.sudo(f'mysqldump {skip_triggers} --result-file={name}.sql {name}',
           user='root')
    c.sudo(f'gzip --force {name}.sql')
    return f'{name}.sql.gz'


def download_db(c, name, destination=None, **kwargs):
    """
    Download a database from the "current" server.
    """
    filename = dump_db(c, name,
                       skip_triggers=kwargs.get('skip_triggers', False))
    c.get(filename, destination or f'./{filename}')
    c.sudo(f'rm {filename}')


def clone_db(c, name, download, user=None, force=False):
    """
    Clone a MySQL database from a (presumably live) server

    :param name: Name of the database.

    :param force: Whether the target database should be forcibly dropped, if it
       exists already.
    """
    if db_exists(c, name):
       if force:
           drop_db(c, name, checkfirst=False)
       else:
           raise RuntimeError("Database '{}' already exists! (pass force=True to override)".format(name))

    create_db(c, name, checkfirst=False)

    # obtain database dump from live server
    download(c, '{}.sql.gz'.format(name), user=user or c.user)

    # upload database dump to target server
    c.put('{}.sql.gz'.format(name))
    c.local('rm {}.sql.gz'.format(name))

    # restore database on target server
    c.run('gunzip --force {}.sql.gz'.format(name))
    c.sudo("bash -c 'mysql {0} < {0}.sql'".format(name))
    c.run('rm {}.sql'.format(name))


def restore_db(c, name, path):
    """
    Restore a database from a dump file.

    :param name: Name of the database to restore.

    :param path: Path to the DB dump file, which should end in ``.sql.gz``
    """
    if not path.endswith('.sql.gz'):
        raise ValueError("Path to dump file must end in `.sql.gz`")

    c.sudo(f'gunzip --force {path}')
    sql_path = path[:-3]
    c.sudo(f"bash -c 'mysql {name} < {sql_path}'")
    c.sudo(f'rm {sql_path}')

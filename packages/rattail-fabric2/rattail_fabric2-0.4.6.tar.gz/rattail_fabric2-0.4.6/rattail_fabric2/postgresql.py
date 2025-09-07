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
Fabric Library for PostgreSQL
"""

import os
import re

from rattail_fabric2 import apt, append, contains, sed, uncomment


def install(c):
    """
    Install the PostgreSQL database service
    """
    apt.install(c, 'postgresql', 'libpq-dev')


def get_version(c):
    """
    Fetch the version of PostgreSQL running on the target system
    """
    result = c.run('psql --version', warn=True)
    if not result.failed:
        match = re.match(r'^psql \(PostgreSQL\) (\d+\.\d+)(?:\.\d+)?', result.stdout.strip())
        if match:
            return float(match.group(1))


def set_listen_addresses(c, *addresses):
    """
    Overwrite the `listen_addresses` config setting in `postgresql.conf`.
    """
    version = get_version(c)
    if version > 12:
        version = int(version)

    addresses = ','.join(addresses)

    if not contains(c, '/etc/postgresql/{}/main/postgresql.conf'.format(version),
                    "listen_addresses = '{}'".format(addresses),
                    exact=True):

        uncomment(c, '/etc/postgresql/{}/main/postgresql.conf'.format(version),
                  r'^# *listen_addresses\s*=.*',
                  use_sudo=True)

        sed(c, '/etc/postgresql/{}/main/postgresql.conf'.format(version),
            r'listen_addresses\s*=.*',
            "listen_addresses = '{}'".format(addresses),
            use_sudo=True)

        restart(c)


def add_hba_entry(c, entry):
    """
    Add an entry to the `pg_hba.conf` file.
    """
    version = get_version(c)
    if version > 12:
        version = int(version)

    if not contains(c, '/etc/postgresql/{}/main/pg_hba.conf'.format(version),
                    entry, use_sudo=True):
        append(c, '/etc/postgresql/{}/main/pg_hba.conf'.format(version),
               entry, use_sudo=True)
        reload_(c)


def restart(c):
    """
    Restart the PostgreSQL database service
    """
    c.sudo('systemctl restart postgresql.service')


def reload_(c):
    """
    Reload config for the PostgreSQL database service
    """
    c.sudo('systemctl reload postgresql.service')

# TODO: deprecate / remove this
reload = reload_


def sql(c, sql, database='', port=None, **kwargs):
    """
    Execute some SQL as the 'postgres' user.
    """
    cmd = 'psql {port} --tuples-only --no-align --command="{sql}" {database}'.format(
        port='--port={}'.format(port) if port else '',
        sql=sql, database=database)
    return c.sudo(cmd, user='postgres', **kwargs)


def script(c, path, database='', port=None, user=None, password=None):
    """
    Execute a SQL script.  By default this will run as 'postgres' user, but can
    use PGPASSWORD authentication if necessary.
    """
    port = '--port={}'.format(port) if port else ''
    if user and password:
        kw = dict(pw=password, user=user, port=port, path=path, db=database)
        return c.sudo(" PGPASSWORD='{pw}' psql --host=localhost {port} --username='{user}' --file='{path}' {db}".format(**kw),
                      echo=False)

    else: # run as postgres
        kw = dict(port=port, path=path, db=database)
        return c.sudo("psql {port} --file='{path}' {db}".format(**kw),
                      user='postgres')


def user_exists(c, name, port=None):
    """
    Determine if a given PostgreSQL user exists.
    """
    user = sql(c, "SELECT rolname FROM pg_roles WHERE rolname = '{0}'".format(name), port=port).stdout.strip()
    return bool(user)


def create_user(c, name, password=None, port=None, checkfirst=True, createdb=False):
    """
    Create a PostgreSQL user account.
    """
    if not checkfirst or not user_exists(c, name, port=port):
        cmd = 'createuser {port} {createdb} --no-createrole --no-superuser {name}'.format(
            port='--port={}'.format(port) if port else '',
            createdb='--{}createdb'.format('' if createdb else 'no-'),
            name=name)
        c.sudo(cmd, user='postgres')
        if password:
            set_user_password(c, name, password, port=port)


def set_user_password(c, name, password, port=None):
    """
    Set the password for a PostgreSQL user account
    """
    sql(c, "ALTER USER \\\"{}\\\" PASSWORD '{}';".format(name, password), port=port,
        hide=True, echo=False)


def db_exists(c, name, port=None):
    """
    Determine if a given PostgreSQL database exists.
    """
    db = sql(c, "SELECT datname FROM pg_database WHERE datname = '{0}'".format(name), port=port).stdout.strip()
    return db == name


def create_db(c, name, owner=None, port=None, checkfirst=True):
    """
    Create a PostgreSQL database.
    """
    if not checkfirst or not db_exists(c, name, port=port):
        cmd = 'createdb {port} {owner} {name}'.format(
            port='--port={}'.format(port) if port else '',
            owner='--owner={}'.format(owner) if owner else '',
            name=name)
        c.sudo(cmd, user='postgres')


def create_schema(c, name, dbname, owner='rattail', port=None):
    """
    Create a schema within a PostgreSQL database.
    """
    sql_ = "create schema if not exists {} authorization {}".format(name, owner)
    sql(c, sql_, database=dbname, port=port)


def drop_db(c, name, checkfirst=True):
    """
    Drop a PostgreSQL database.
    """
    if not checkfirst or db_exists(c, name):
        c.sudo('dropdb {}'.format(name), user='postgres')


def dump_db(c, name, port=None, exclude_tables=None,
            skip_raw_file=False):
    """
    Dump a database to file, on the server represented by ``c`` param.

    This function returns the name of the DB dump file.  The name will not have
    a path component as it's assumed to be in the home folder of the connection
    user.
    """
    c.run('touch {}.sql'.format(name))
    c.run('chmod 0666 {}.sql'.format(name))

    sql_name = f'{name}.sql'
    gz_name = f'{sql_name}.gz'
    filename = gz_name if skip_raw_file else sql_name

    port = f'--port={port}' if port else ''
    exclude_tables = f'--exclude-table-data={exclude_tables}' if exclude_tables else ''
    filename = '' if skip_raw_file else f'--file={filename}'
    cmd = f'pg_dump {port} {exclude_tables} {filename} {name}'

    if skip_raw_file:
        tmp_name = f'/tmp/{gz_name}'
        cmd = f'{cmd} | gzip -c > {tmp_name}'
        c.sudo(cmd, user='postgres')
        # TODO: should remove this file
        c.run(f"cp {tmp_name} {gz_name}")

    else:
        c.sudo(cmd, user='postgres')
        c.run(f'gzip --force {sql_name}')

    return gz_name


def download_db(c, name, destination=None, port=None, exclude_tables=None,
                skip_raw_file=False):
    """
    Download a database from the server represented by ``c`` param.
    """
    if destination is None:
        destination = './{}.sql.gz'.format(name)
    dumpfile = dump_db(c, name, port=port, exclude_tables=exclude_tables,
                       skip_raw_file=skip_raw_file)
    c.get(dumpfile, destination)
    c.run('rm {}'.format(dumpfile))


def clone_db(c, name, owner, download, user='rattail', force=False, workdir=None):
    """
    Clone a database from a (presumably live) server

    :param name: Name of the database.

    :param owner: Username of the user who is to own the database.

    :param force: Whether the target database should be forcibly dropped, if it
       exists already.
    """
    if db_exists(c, name):
       if force:
           drop_db(c, name, checkfirst=False)
       else:
           raise RuntimeError("Database '{}' already exists!".format(name))

    create_db(c, name, owner=owner, checkfirst=False)

    # upload database dump to target server
    if workdir:
        curdir = os.getcwd()
        os.chdir(workdir)
    download(c, '{}.sql.gz'.format(name), user=user)
    c.put('{}.sql.gz'.format(name))
    c.local('rm {}.sql.gz'.format(name))
    if workdir:
        os.chdir(curdir)

    # restore database on target server
    # TODO: first tried c.sudo('mv ...') but that did not work for the "typical"
    # scenario of connecting as rattail@server to obtain db dump, since the dump
    # cmd is normally carved out via sudoers config, but 'sudo mv ..' is not
    filename = f'{name}.sql.gz'
    c.run(f'mv {filename} /tmp/')
    restore_db(c, name, f'/tmp/{filename}')


def restore_db(c, name, path):
    """
    Restore a database from a dump file.

    :param name: Name of the database to restore.

    :param path: Path to the DB dump file, which should end in ``.sql.gz``
    """
    if not path.endswith('.sql.gz'):
        raise ValueError("Path to dump file must end in `.sql.gz`")

    c.run('gunzip --force {}'.format(path))
    sql_path = path[:-3]
    c.sudo('psql --echo-errors --file={} {}'.format(sql_path, name),
           user='postgres')
    c.run('rm {}'.format(sql_path))

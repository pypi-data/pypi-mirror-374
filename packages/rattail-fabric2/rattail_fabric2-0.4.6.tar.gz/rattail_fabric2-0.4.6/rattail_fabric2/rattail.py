# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
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
Fabric library for Rattail itself
"""

from __future__ import unicode_literals, absolute_import

import os

from rattail_fabric2 import apache, apt, postfix, postgresql, python, make_deploy, make_system_user, mkdir


deploy_common = make_deploy(__file__)


def bootstrap_rattail_base(c, deploy=None, timezone='America/Chicago',
                           **context):
    """
    Bootstrap the base system requirements, common to all machines
    running Rattail apps.  Note that this includes basic installation
    of Python, PostgreSQL and Aapche.
    """
    env = context.get('env')
    context['timezone'] = timezone

    # make system user, install init scripts etc.
    bootstrap_rattail(c, alias='root')

    # machine-wide config
    if deploy and deploy.local_exists('rattail/rattail.conf.mako'):
        deploy(c, 'rattail/rattail.conf.mako', '/etc/rattail/rattail.conf',
               use_sudo=True, context=context)
    else:
        deploy_machine_conf(c, timezone=timezone, context=context)

    # python
    python.bootstrap_python(c, deploy,
                            python3=True,
                            virtualenvwrapper_from_apt=True)

    # postgres
    postgresql.install(c)
    if env and hasattr(env, 'password_postgresql_rattail'):
        postgresql.create_user(c, 'rattail', password=env.password_postgresql_rattail)

    # apache
    apache.install(c)
    apache.enable_mod(c, 'proxy_http')

    # supervisor
    apt.install(c, 'supervisor')


def bootstrap_rattail(c, home='/var/lib/rattail', uid=None, shell='/bin/bash',
                      alias=None):
    """
    Bootstrap a basic Rattail software environment.
    """
    make_system_user(c, 'rattail', home=home, uid=uid, shell=shell)
    mkdir(c, os.path.join(home, '.ssh'), owner='rattail:', mode='0700', use_sudo=True)
    if alias:
        postfix.alias(c, 'rattail', alias)

    mkdir(c, '/etc/rattail', use_sudo=True)
    mkdir(c, '/srv/rattail', use_sudo=True)
    mkdir(c, '/var/log/rattail', owner='rattail:rattail', mode='0775', use_sudo=True)

    mkdir(c, '/srv/rattail/init', use_sudo=True)
    deploy_common(c, 'check-rattail-daemon', '/usr/local/bin/check-rattail-daemon', use_sudo=True)
    deploy_common(c, 'check-supervisor-process', '/usr/local/bin/check-supervisor-process', use_sudo=True)
    deploy_common(c, 'check-systemd-service', '/usr/local/bin/check-systemd-service', use_sudo=True)
    deploy_common(c, 'soffice', '/srv/rattail/init/soffice', use_sudo=True)


def deploy_machine_conf(c, env=None, timezone=None, context={}):
    """
    Deploy the standard machine-wide ``rattail.conf`` file.
    """
    mkdir(c, '/etc/rattail', use_sudo=True)
    context['env'] = env
    context['timezone'] = timezone or getattr(env, 'timezone', 'America/Chicago')
    deploy_common(c, 'rattail/rattail.conf.mako', '/etc/rattail/rattail.conf', use_sudo=True,
                  context=context)


def delete_email_recipients(c, dbname):
    """
    Purge all email recipient settings for the given database.
    """
    # purge new-style for wuttjamaican
    postgresql.sql(c, "delete from setting where name like 'rattail.email.%.sender';", database=dbname)
    postgresql.sql(c, "delete from setting where name like 'rattail.email.%.to';", database=dbname)
    postgresql.sql(c, "delete from setting where name like 'rattail.email.%.cc';", database=dbname)
    postgresql.sql(c, "delete from setting where name like 'rattail.email.%.bcc';", database=dbname)

    # purge old-style for rattail
    postgresql.sql(c, "delete from setting where name like 'rattail.mail.%.from';", database=dbname)
    postgresql.sql(c, "delete from setting where name like 'rattail.mail.%.to';", database=dbname)
    postgresql.sql(c, "delete from setting where name like 'rattail.mail.%.cc';", database=dbname)
    postgresql.sql(c, "delete from setting where name like 'rattail.mail.%.bcc';", database=dbname)


def disable_emails(c, dbname):
    """
    Disable all emails for the given database.
    """
    postgresql.sql(c, "update setting set value = 'false' where name like 'rattail.mail.%.enabled';", database=dbname)


def deploy_datasync_checks(c, envroot, **kwargs):
    """
    Deploy the standard datasync (queue, watcher) check scripts.
    """
    envroot = envroot.rstrip('/')
    context = kwargs.pop('context', {})
    context['envroot'] = envroot
    context.setdefault('config', kwargs.pop('config', 'quiet'))
    deploy_common(c, 'rattail/check-datasync-queue.mako', '{}/app/check-datasync-queue'.format(envroot),
                  context=context, **kwargs)
    deploy_common(c, 'rattail/check-datasync-watchers.mako', '{}/app/check-datasync-watchers'.format(envroot),
                  context=context, **kwargs)

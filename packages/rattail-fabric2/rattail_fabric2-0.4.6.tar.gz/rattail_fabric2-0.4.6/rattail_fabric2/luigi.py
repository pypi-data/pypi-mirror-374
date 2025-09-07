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
Fabric library for Luigi apps
"""

import os
import re
from pkg_resources import parse_version

from rattail_fabric2 import postgresql, make_deploy, mkdir


deploy_common = make_deploy(__file__)


def install_luigi(c, envroot, luigi='luigi', user='rattail',
                  db=False, dbuser='rattail', dbpass='TODO_PASSWORD',
                  db_connection=None,
                  supervisor=False, autostart=False,
                  crontab=False, crontab_mailto=None):
    """
    Install and configure Luigi to the given virtualenv.
    """
    envroot = envroot.rstrip('/')
    envname = os.path.basename(envroot)
    appdir = '{}/app'.format(envroot)

    # package
    c.sudo("""bash -lc "workon {} && pip install '{}'" """.format(envname, luigi),
           user=user)

    # detect luigi version
    LUIGI2 = False
    output = c.sudo("bash -lc 'workon {} && pip show luigi | grep Version'".format(envname), user=user).stdout.strip()
    match = re.match(r'^Version: (\d+\S+)$', output)
    if match:
        if parse_version(match.group(1)) < parse_version('3'):
            LUIGI2 = True

    # dirs
    mkdir(c, ['{}/luigi'.format(appdir),
              '{}/luigi/log'.format(appdir),
              '{}/luigitasks'.format(appdir),
    ], use_sudo=True, owner=user)

    # tasks
    c.sudo('touch {}/luigitasks/__init__.py'.format(appdir),
           user=user)

    # database
    if db:
        postgresql.create_db(c, 'luigi', owner=dbuser)
        if not db_connection:
            db_connection = 'postgresql://{}:{}@localhost/luigi'.format(
                dbuser, dbpass)

    # config
    deploy_common(c, 'luigi/luigi.cfg.mako', '{}/luigi/luigi.cfg'.format(appdir),
                  use_sudo=True, owner=user, mode='0640',
                  context={'appdir': appdir,
                           'LUIGI2': LUIGI2,
                           'db_connection': db_connection})
    deploy_common(c, 'luigi/logging.conf.mako', '{}/luigi/logging.conf'.format(appdir),
                  use_sudo=True, owner=user,
                  context={'appdir': appdir})

    # supervisor
    if supervisor:
        c.sudo('supervisorctl stop luigi:', warn=True)
        deploy_common(c, 'luigi/supervisor.conf.mako',
                      '/etc/supervisor/conf.d/luigi.conf',
                      use_sudo=True,
                      context={'envroot': envroot,
                               'appdir': appdir,
                               'user': user,
                               'autostart': autostart})
        c.sudo('supervisorctl update')
        if autostart:
            c.sudo('supervisorctl start luigi:')

    # logrotate
    deploy_common(c, 'luigi/luigi-logrotate.conf.mako', '{}/luigi/logrotate.conf'.format(appdir),
                  use_sudo=True, owner='root:', # must be owned by root (TODO: why is that again?)
                  context={'appdir': appdir})
    deploy_common(c, 'luigi/rotate-logs.sh.mako', '{}/rotate-luigi-logs.sh'.format(appdir),
                  use_sudo=True, owner=user,
                  context={'appdir': appdir})
    if crontab:
        deploy_common(c, 'luigi/crontab.mako', '/etc/cron.d/luigi',
                      use_sudo=True, context={'appdir': appdir,
                                              'mailto': crontab_mailto})


def install_overnight_script(c, envroot, user='rattail', automation='All',
                             email_key=None,
                             luigi=False,
                             cron=True, cron_conf='app/cron.conf',
                             restart=True, restart_conf='app/silent.conf'):
    """
    Install an overnight automation script
    """
    envroot = envroot.rstrip('/')
    appdir = '{}/app'.format(envroot)

    # overnight-*.sh
    if luigi:
        filename = 'overnight-{}.sh'.format(automation.lower())
        deploy_common(c, 'luigi/overnight.sh.mako',
                      '{}/{}'.format(appdir, filename),
                      use_sudo=True, owner=user, mode='0755',
                      context={'envroot': envroot, 'appdir': appdir,
                               'automation': automation})

    # cron-overnight-*.sh
    if cron:
        filename = 'cron-overnight-{}.sh'.format(automation.lower())
        deploy_common(c, 'luigi/cron-overnight.sh.mako',
                      '{}/{}'.format(appdir, filename),
                      use_sudo=True, owner=user, mode='0755',
                      context={'envroot': envroot,
                               'overnight_conf': cron_conf,
                               'automation': automation,
                               'email_key': email_key})

    # restart-overnight-*.sh
    if restart:
        filename = 'restart-overnight-{}.sh'.format(automation.lower())
        deploy_common(c, 'luigi/restart-overnight.sh.mako',
                      '{}/{}'.format(appdir, filename),
                      use_sudo=True, owner=user, mode='0755',
                      context={'envroot': envroot,
                               'appdir': appdir,
                               'overnight_conf': restart_conf,
                               'automation': automation,
                               'email_key': email_key})


def register_with_supervisor(c, envroot, user='rattail', autostart=False):
    """
    Register the Luigi scheduler daemon with supervisor
    """
    envroot = envroot.rstrip('/')
    appdir = '{}/app'.format(envroot)

    deploy_common(c, 'luigi/supervisor.conf.mako',
                  '/etc/supervisor/conf.d/luigi.conf',
                  use_sudo=True,
                  context={'envroot': envroot,
                           'appdir': appdir,
                           'user': user,
                           'autostart': autostart})
    c.sudo('supervisorctl update')
    if autostart:
        c.sudo('supervisorctl start luigi:')

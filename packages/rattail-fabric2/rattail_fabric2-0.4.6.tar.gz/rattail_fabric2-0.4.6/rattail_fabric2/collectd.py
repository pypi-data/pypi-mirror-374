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
Fabric library for collectd
"""

from rattail_fabric2 import apt, make_deploy, sed


deploy = make_deploy(__file__)


def install_collectd(c, interval=None, rrdtool=None, restart_=False):
    """
    Install the ``collectd`` service.

    :param interval: Optional override for the collectd ``Interval``
       setting.
    """
    apt.install(c, 'collectd')

    if interval:
        sed(c, '/etc/collectd/collectd.conf',
            r'^#? ?Interval\s+[0-9]+.*$',
            'Interval {}'.format(interval),
            use_sudo=True)

    if rrdtool is not None:
        sed(c, '/etc/collectd/collectd.conf',
            r'^#? ?LoadPlugin rrdtool\s*$',
            '{}LoadPlugin rrdtool'.format('' if rrdtool else '#'),
            use_sudo=True)

    if restart_:
        restart(c)


def restart(c):
    """
    Restart the collectd service.
    """
    c.sudo('systemctl restart collectd')


def deploy_mountpoint_check_script(c, dest, **kwargs):
    """
    Deploy generic mountpoint check script to specified destination.
    """
    deploy(c, 'collectd/check-mountpoints.py', dest, **kwargs)

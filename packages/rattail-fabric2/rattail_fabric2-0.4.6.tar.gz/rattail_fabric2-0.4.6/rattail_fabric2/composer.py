# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
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
Fabric lib for Composer (PHP dependency manager)
"""

from rattail_fabric2 import apt, make_deploy, exists


deploy = make_deploy(__file__)


def install(c, with_apt=True):
    if with_apt:
        apt.install(c, 'composer')
    else:
        install_globally(c)


def install_globally(c):
    """
    Install `composer.phar` in global location
    """
    if not exists(c, '/usr/local/bin/composer.phar'):
        deploy(c, 'composer/install-composer.sh', '/tmp/install-composer.sh', mode='0700', use_sudo=True)
        c.sudo("bash -c 'cd /usr/local/bin; /tmp/install-composer.sh'")
        c.sudo('rm /tmp/install-composer.sh')

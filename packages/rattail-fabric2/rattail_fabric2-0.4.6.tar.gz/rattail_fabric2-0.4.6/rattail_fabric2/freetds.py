# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
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
Fabric Library for FreeTDS
"""

from rattail_fabric2 import apt, exists, mkdir


def install_from_source(c, user='rattail', branch=None):
    """
    Install the FreeTDS library from source.

    Per instructions found here:
    https://github.com/FreeTDS/freetds/blob/master/INSTALL.md
    """
    apt.install(
        c,
        'automake',
        'autoconf',
        'gettext',
        'gperf',
        'pkg-config',
    )

    if c.run('which git', warn=True).failed:
        apt.install(c, 'git')

    if not exists(c, '/usr/local/src/freetds'):
        mkdir(c, '/usr/local/src/freetds', owner=user, use_sudo=True)
        c.sudo('git clone https://github.com/FreeTDS/freetds.git /usr/local/src/freetds',
               user=user)
        if branch:
            c.sudo("bash -c 'cd /usr/local/src/freetds; git checkout {}'".format(branch),
                   user=user)

    if not exists(c, '/usr/local/lib/libtdsodbc.so'):
        c.sudo("bash -c 'cd /usr/local/src/freetds; ./autogen.sh'", user=user)
        c.sudo("bash -c 'cd /usr/local/src/freetds; make'", user=user)
        c.sudo("bash -c 'cd /usr/local/src/freetds; make install'") # as root

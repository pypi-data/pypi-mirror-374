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
Fabric library for Byjove
"""

from rattail_fabric2 import exists, mkdir


def install_from_source(c, user='rattail'):
    """
    Install the 'byjove' source code package, for staging systems
    """
    if not exists(c, '/usr/local/src/byjove'):
        mkdir(c, '/usr/local/src/byjove', use_sudo=True, owner=user)
        c.sudo('git clone https://forgejo.wuttaproject.org/rattail/byjove.git /usr/local/src/byjove',
               user=user)
        c.sudo("bash -l -c 'cd /usr/local/src/byjove; npm link'", 
               user=user)
        c.sudo("bash -l -c 'cd /usr/local/src/byjove; npm run build'", 
               user=user)

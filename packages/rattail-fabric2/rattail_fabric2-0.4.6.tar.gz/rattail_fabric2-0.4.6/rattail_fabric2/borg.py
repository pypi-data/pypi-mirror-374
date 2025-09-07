# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2024 Lance Edgar
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
Fabric library for Borg backups

https://www.borgbackup.org/
"""

from rattail_fabric2 import apt


def install_dependencies(c):
    """
    Install the dependencies for Borg
    """
    apt.install(
        c,
        'libacl1-dev',
        'libfuse-dev',
        'liblz4-dev',
        'libssl-dev',
        'libxxhash-dev',
        'libzstd-dev',
        'pkg-config',
    )

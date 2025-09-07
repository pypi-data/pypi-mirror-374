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
Rattail-Fabric2 Library

This package contains various tasks and associated functions for use with
Fabric deployment and maintenance.
"""

from ._version import __version__

from .core import (
    is_debian,
    get_debian_version,
    get_ubuntu_version,
    Deployer,
    make_deploy,
    make_normal_user,
    make_system_user,
    mkdir,
    rsync,
    set_timezone,
    UNSPECIFIED,
)
from .util import exists, contains, append, sed, uncomment

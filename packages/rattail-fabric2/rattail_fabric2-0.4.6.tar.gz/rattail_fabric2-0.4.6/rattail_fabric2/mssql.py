# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2020 Lance Edgar
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
Fabric Library for MS SQL Server
"""

from rattail_fabric2 import apt


def install_mssql_odbc(c, accept_eula=None):
    """
    Install the MS SQL Server ODBC driver

    https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-2017
    """
    apt.install(c, 'apt-transport-https', 'curl')
    c.sudo("bash -c 'curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -'")
    c.sudo("bash -c 'curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list'")
    apt.update(c)
    cmd = 'apt-get --assume-yes install msodbcsql17'
    if accept_eula:
        cmd = 'ACCEPT_EULA=Y {}'.format(cmd)
    c.sudo(cmd)

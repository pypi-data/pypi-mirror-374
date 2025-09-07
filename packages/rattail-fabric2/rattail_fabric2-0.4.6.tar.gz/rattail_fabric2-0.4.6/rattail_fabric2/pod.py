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
Fabric Library for Product Open Data (POD)
"""

import os

from rattail_fabric2 import apt, exists, mkdir


def install_pod(c, path='/srv/pod', download_url=None):
    """
    Install the Product Open Data (POD) files to the given path.
    """
    apt.install(c, 'unzip')
    mkdir(c, path, use_sudo=True)
    if not exists(c, os.path.join(path, 'pod_pictures_gtin.zip')):
        if not download_url:
            download_url = 'http://www.product-open-data.com/docs/pod_pictures_gtin_2013.08.29_01.zip'
        c.sudo("bash -c 'cd {}; wget --output-document=pod_pictures_gtin.zip {}'".format(path, download_url))
    if not exists(c, os.path.join(path, 'pictures/gtin')):
        c.sudo("bash -c 'cd {}; unzip pod_pictures_gtin.zip -d pictures'".format(path))

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
Fabric library for Docker
"""

from rattail_fabric2 import apt, exists, mkdir


def setup_repository(c, flavor='debian'):
    """
    Setup the APT repository for Docker

    https://docs.docker.com/engine/install/debian/#install-using-the-repository
    https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
    """
    apt.install(c, 'ca-certificates',
                'curl',
                'gnupg',
                'lsb-release')

    mkdir(c, '/etc/apt/keyrings', use_sudo=True)

    if not exists(c, '/etc/apt/keyrings/docker.gpg'):
        c.sudo("bash -c 'curl -fsSL https://download.docker.com/linux/{}/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg'".format(flavor))

    c.sudo("""bash -c 'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/{} $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null'""".format(flavor))

    apt.update(c)


def install_engine(c):
    """
    Install the Docker engine

    https://docs.docker.com/engine/install/debian/#install-docker-engine
    """
    apt.install(c, 'docker-ce',
                'docker-ce-cli',
                'containerd.io',
                'docker-compose-plugin')

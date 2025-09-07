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
Fabric library for Let's Encrypt certbot
"""

from rattail_fabric2 import apt, exists, get_debian_version


def install(c, source=False, service='apache'):
    """
    Install the Let's Encrypt certbot utility
    """
    if source:
        if not exists(c, '/usr/local/src/certbot'):
            c.sudo('git clone https://github.com/certbot/certbot /usr/local/src/certbot')
        c.sudo('ln --symbolic --force /usr/local/src/certbot/certbot-auto /usr/local/bin/certbot')

    else:
        version = get_debian_version(c)

        # debian 7 wheezy
        if 7 <= version < 8:
            if not exists(c, '/usr/local/src/certbot'):
                c.sudo('git clone https://github.com/certbot/certbot /usr/local/src/certbot')
            c.sudo('ln --symbolic --force /usr/local/src/certbot/certbot-auto /usr/local/bin/certbot')

        # debian 8 jessie
        elif 8 <= version < 9:
            apt.add_source(c, 'deb http://ftp.debian.org/debian jessie-backports main')
            apt.install(c, 'python-certbot-apache', target_release='jessie-backports')

        # debian 9 stretch
        elif 9 <= version < 10:
            if service == 'apache':
                apt.install(c, 'python-certbot-apache')
            elif service == 'nginx':
                apt.install(c, 'python-certbot-nginx')
            else:
                raise NotImplementedError("unknown web service: {}".format(service))

        # debian 10 buster, or later
        elif version >= 10:
            if service == 'apache':
                apt.install(c, 'python3-certbot-apache')
            elif service == 'nginx':
                apt.install(c, 'python3-certbot-nginx')
            else:
                raise NotImplementedError("unknown web service: {}".format(service))

        # other..? will have to investigate when this comes up
        else:
            raise NotImplementedError("don't know how to install certbot on debian version {}".format(version))

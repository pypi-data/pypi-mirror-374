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
Fabric library for Apache web server
"""

from __future__ import unicode_literals, absolute_import

import re

from rattail_fabric2 import apt


def install(c):
    """
    Install the Apache web service
    """
    apt.install(c, 'apache2')


def install_wsgi(c, python_home=None, python3=True):
    """
    Install the mod_wsgi Apache module, with optional ``WSGIPythonHome`` value.

    NOTE: you probably should not use this!  reverse proxy seems more robust
    """
    if python3:
        apt.install(c, 'libapache2-mod-wsgi-py3')
    else:
        apt.install(c, 'libapache2-mod-wsgi')
    if python_home:
        if get_version(c) == 2.2:
            c.sudo("bash -c 'echo WSGIPythonHome {} > /etc/apache2/conf.d/wsgi'".format(python_home))
        else: # assuming 2.4
            c.sudo("bash -c 'echo WSGIPythonHome {} > /etc/apache2/conf-available/wsgi.conf'".format(python_home))
            enable_conf(c, 'wsgi')


def get_version(c):
    """
    Fetch the version of Apache running on the target system
    """
    result = c.sudo('apache2 -v')
    if not result.failed:
        match = re.match(r'^Server version: Apache/(\d+\.\d+)\.\d+ \(.*\)', result.stdout)
        if match:
            return float(match.group(1))


def get_php_version(c):
    """
    Fetch the version of PHP running on the target system
    """
    result = c.sudo('php --version')
    if not result.failed:
        match = re.match(r'^PHP (\d+\.\d+)\.\d+', result.stdout)
        if match:
            return float(match.group(1))


def enable_mod(c, *names):
    """
    Enable the given Apache modules
    """
    for name in names:
        c.sudo('a2enmod {}'.format(name))


def enable_port(c, port):
    """
    Tell Apache to listen on the given port.
    """
    if not isinstance(port, int) and not port.isdigit():
        raise ValueError("port must be an integer")
    if c.run("grep '^Listen {}' /etc/apache2/ports.conf".format(port), warn=True).failed:
        c.sudo("""bash -c 'echo "Listen {}" >> /etc/apache2/ports.conf'""".format(port))


def enable_site(c, *names):
    """
    Enable the given Apache site(s)
    """
    for name in names:
        c.sudo('a2ensite {}'.format(name))


def deploy_site(c, deployer, local_path, name, enable=False, **kwargs):
    """
    Deploy a file to Apache sites-available
    """
    apache_version = get_version(c)
    if apache_version == 2.2:
        path = '/etc/apache2/sites-available/{}'.format(name)
    else:
        path = '/etc/apache2/sites-available/{}.conf'.format(
            '000-default' if name == 'default' else name)
    context = kwargs.pop('context', {})
    context['apache_version'] = apache_version
    deployer(c, local_path, path, context=context, **kwargs)
    if enable and name != 'default':
        enable_site(c, name)


def deploy_conf(c, deployer, local_path, name, enable=False, **kwargs):
    """
    Deploy a config snippet file to Apache
    """
    apache_version = get_version(c)
    if apache_version == 2.2:
        deployer(c, local_path, '/etc/apache2/conf.d/{}.conf'.format(name), **kwargs)
    else:
        deployer(c, local_path, '/etc/apache2/conf-available/{}.conf'.format(name), **kwargs)
        if enable:
            enable_conf(c, name)


def enable_conf(c, *names):
    """
    Enable the given Apache configurations
    """
    for name in names:
        c.sudo('a2enconf {}'.format(name))


def restart(c):
    """
    Restart the Apache web service
    """
    c.sudo('systemctl restart apache2.service')


def stop(c):
    """
    Stop the Apache web service
    """
    c.sudo('systemctl stop apache2.service')


def start(c):
    """
    Start the Apache web service
    """
    c.sudo('systemctl start apache2.service')

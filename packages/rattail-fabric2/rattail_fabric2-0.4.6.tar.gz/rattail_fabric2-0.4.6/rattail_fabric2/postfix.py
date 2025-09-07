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
Fabric library for Postfix
"""

from rattail_fabric2 import apt
from rattail.util import shlex_join


def install(c):
    """
    Install the Postfix mail service
    """
    apt.install(c, 'postfix')
    apt.purge(c, 'exim4', 'exim4-base', 'exim4-config', 'exim4-daemon-light')


def alias(c, name, alias_to, path='/etc/aliases'):
    """
    Set a mail alias for Postfix
    """
    # does alias entry already exist?
    if c.run("grep '^{}:' /etc/aliases".format(name), warn=True).failed:
        # append new entry
        entry = '{}: {}'.format(name, alias_to)
        echo = shlex_join(['echo', entry])
        cmd = '{} >> /etc/aliases'.format(echo)
        cmd = shlex_join(['bash', '-c', cmd])
        c.sudo(cmd)
    else:
        # update existing entry
        alias_to = alias_to.replace('|', '\\|')
        sub = "s|^{}: .*|{}: {}|".format(name, name, alias_to)
        cmd = shlex_join(['sed', '-i.bak', '-E', sub, '/etc/aliases'])
        c.sudo(cmd)

    c.sudo('newaliases')


def restart(c):
    """
    Restart the Postfix mail service
    """
    c.sudo('systemctl restart postfix.service')


def set_config(c, setting, value):
    """
    Configure the given setting with the given value.
    """
    c.sudo("postconf -e '{}={}'".format(setting, value))


def set_myhostname(c, hostname):
    """
    Configure the 'myhostname' setting with the given string.
    """
    set_config(c, 'myhostname', hostname)


def set_myorigin(c, origin):
    """
    Configure the 'myorigin' setting with the given string.
    """
    set_config(c, 'myorigin', origin)


def set_mydestination(c, *destinations):
    """
    Configure the 'mydestinations' setting with the given strings.
    """
    set_config(c, 'mydestination', ', '.join(destinations))


def set_mynetworks(c, *networks):
    """
    Configure the 'mynetworks' setting with the given strings.
    """
    set_config(c, 'mynetworks', ' '.join(networks))


def set_relayhost(c, relayhost):
    """
    Configure the 'relayhost' setting with the given string
    """
    set_config(c, 'relayhost', relayhost)

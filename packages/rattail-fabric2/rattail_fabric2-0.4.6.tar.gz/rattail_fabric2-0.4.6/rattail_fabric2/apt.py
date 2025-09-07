# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2025 Lance Edgar
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
Fabric library for the APT package system
"""

from __future__ import unicode_literals, absolute_import

from rattail_fabric2 import make_deploy, get_debian_version, get_ubuntu_version


deploy = make_deploy(__file__)


def install(c, *packages, **kwargs):
    """
    Install one or more packages via ``apt-get install``.
    """
    frontend = kwargs.pop('frontend', 'noninteractive')
    target = kwargs.pop('target_release', None)
    target = '--target-release={}'.format(target) if target else ''
    force_yes = ' --force-yes' if kwargs.pop('force_yes', False) else ''
    return c.sudo('DEBIAN_FRONTEND={} apt-get --assume-yes {}{} install {}'.format(
        frontend, target, force_yes, ' '.join(packages)), **kwargs)


def is_installed(c, package):
    """
    Check if the given APT package is installed.

    :param c: Fabric connection.

    :param package: Name of package to be checked.

    :returns: ``True`` if package is installed, else ``False``.
    """
    return c.run(f"dpkg-query -s {package}", warn=True).ok


def purge(c, *packages):
    """
    Uninstall and purge config for given packages
    """
    c.sudo('apt-get --assume-yes purge {}'.format(' '.join(packages)))


def update(c):
    """
    Perform an ``apt-get update`` operation.
    """
    c.sudo('apt-get update')


def add_source(c, entry):
    """
    Add a new entry to the apt/sources.list file
    """
    if c.run("grep '^{}' /etc/apt/sources.list".format(entry), warn=True).failed:
        c.sudo("""bash -c 'echo "{}" >> /etc/apt/sources.list'""".format(entry))
        update(c)


def upgrade(c, frontend='noninteractive'):
    """
    Perform an ``apt-get upgrade`` operation.
    """
    options = ''
    if frontend == 'noninteractive':
        options = '--option Dpkg::Options::="--force-confdef" --option Dpkg::Options::="--force-confold"'
    c.sudo('DEBIAN_FRONTEND={} apt-get --assume-yes {} upgrade'.format(frontend, options))


def dist_upgrade(c, frontend='noninteractive'):
    """
    Perform a full ``apt-get dist-upgrade`` operation.
    """
    update(c)
    options = ''
    if frontend == 'noninteractive':
        options = '--option Dpkg::Options::="--force-confdef" --option Dpkg::Options::="--force-confold"'
    c.sudo('DEBIAN_FRONTEND={} apt-get --assume-yes {} dist-upgrade'.format(frontend, options))


def configure_listchanges(c):
    """
    Configure apt listchanges to never use a frontend.
    """
    deploy(c, 'apt/listchanges.conf', '/etc/apt/listchanges.conf', use_sudo=True)


def install_emacs(c):
    """
    Install the Emacs editor
    """
    if not c.run('which emacs', warn=True).failed:
        return

    emacs = 'emacs-nox'
    debian_version = get_debian_version(c)
    if debian_version:
        if debian_version < 8:
            emacs = 'emacs23-nox'
    else:
        ubuntu_version = get_ubuntu_version(c)
        if ubuntu_version and ubuntu_version < 16:
            emacs = 'emacs23-nox'

    install(c, emacs,
            'emacs-goodies-el',
            )

    # nb. this includes tramp manual
    if c.sudo('dpkg -s emacs-common-non-dfsg', warn=True).ok:
        install(c, 'emacs-common-non-dfsg')

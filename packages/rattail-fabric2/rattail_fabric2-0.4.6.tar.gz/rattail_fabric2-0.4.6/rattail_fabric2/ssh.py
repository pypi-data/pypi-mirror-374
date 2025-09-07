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
Fabric Library for SSH
"""


def cache_host_key(c, host, port=None, user=None, **kwargs):
    """
    Cache the SSH host key for the given host, for the given user.
    """
    if 'for_user' in kwargs:
        pass                    # TODO: deprecation warning

    if not user and kwargs.get('for_user'):
        user = kwargs['for_user']

    port = '-p {}'.format(port) if port else ''

    # first try to run basic command over ssh; if it works then we don't
    # actually need to update/cache the host key
    cmd = 'ssh {} {} whoami'.format(port, host)
    if user:
        result = c.sudo(cmd, warn=True, user=None if user == 'root' else user)
    else:
        result = c.run(cmd, warn=True)
    if result.failed:

        # basic command failed, but in some cases that is simply b/c normal
        # commands are not allowed, although the ssh connection itself was
        # established okay.  here we check for that situation.
        if "Disallowed command" not in result.stderr:

            # okay then we now think that the ssh connection itself was not
            # made, which presumably means we *do* need to cache the host key,
            # so try that now
            cmd = 'ssh -o StrictHostKeyChecking=no {} {} whoami'.format(port, host)
            if user:
                c.sudo(cmd, user=None if user == 'root' else user, warn=True)
            else:
                c.run(cmd, warn=True)


def restart(c):
    """
    Restart the OpenSSH service
    """
    c.sudo('systemctl restart ssh.service')


def configure(c, allow_root=False):
    """
    Configure the OpenSSH service
    """
    set_config(c, 'PermitRootLogin', 'without-password' if allow_root else 'no')
    set_config(c, 'PasswordAuthentication', 'no')
    restart(c)


def set_config(c, setting, value, path='/etc/ssh/sshd_config'):
    """
    Configure the given SSH setting with the given value.
    """
    # first check if the setting is already defined
    if c.run("grep '^{} ' {}".format(setting, path), warn=True).failed:

        # nope, not yet defined.  maybe we can uncomment a definition?
        # (note, this looks only for '#Foo' and not '# Foo' for instance)
        if c.run("grep '^#{} ' {}".format(setting, path), warn=True).failed:

            # nope, must tack on a new definition at end of file
            c.sudo("""bash -c 'echo "{} {}" >> {}'""".format(setting, value, path))

        else: # yep, uncomment existing definition, but also overwrite
            c.sudo("sed -i.bak -e 's/^#{0} .*/{0} {1}/' {2}".format(setting, value, path))

    else: # setting is defined, so overwrite it
        c.sudo("sed -i.bak -e 's/^{0} .*/{0} {1}/' {2}".format(setting, value, path))

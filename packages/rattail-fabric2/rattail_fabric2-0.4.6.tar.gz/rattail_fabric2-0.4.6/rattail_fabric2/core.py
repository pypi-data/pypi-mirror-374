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
Core Utilities
"""

import os
import re
import tempfile
import warnings

from mako.template import Template


UNSPECIFIED = object()


def agent_sudo(c, cmd, user=None):
    """
    Run a 'sudo' command on the target server, with full agent forwarding.

    .. note::
       For this to actually work, you must have enabled agent forwarding for
       your actual connection to the target machine.  This is perhaps most
       easily accomplished via ``~/.ssh/config`` entries.  It is assumed
       however that you would only want to enable agent forwarding temporarily,
       just long enough to e.g. rsync some files.
    """
    c.sudo("bash -c 'SSH_AUTH_SOCK=$SSH_AUTH_SOCK {}'".format(cmd), user=user)


def is_link(c, path, use_sudo=False):
    """
    Return True if the given path is a symlink on the current remote host.

    If ``use_sudo`` is True, will use `.sudo` instead of `.run`.

    .. note::

       This function is derived from one copied from fabric v1.
    """
    func = c.sudo if use_sudo else c.run
    cmd = 'test -L "$(echo %s)"' % path
    result = func(cmd, warn=True)
    return False if result.failed else True


def get_os_release_id(c):
    """
    Return the "ID" field from `/etc/os-release` file
    """
    contents = c.run('cat /etc/os-release').stdout.strip()
    data = {}
    for line in contents.split('\n'):
        field, value = line.split('=')
        data[field] = value
    return data['ID']


def is_debian(c):
    """
    Return boolean indicating if this machine is Debian (proper, as opposed to
    some derivative).
    """
    release_id = get_os_release_id(c)
    return release_id == 'debian'


def get_debian_version(c):
    """
    Fetch the version of Debian running on the target system.
    """
    version = c.run('cat /etc/debian_version').stdout.strip()
    match = re.match(r'^(\d+\.\d+)$', version)
    if match:
        return float(match.group(1))


def get_ubuntu_version(c):
    """
    Fetch the version of Ubuntu running on the target system
    """
    info = c.run('cat /etc/lsb-release').stdout.strip()
    match = re.search(r'DISTRIB_RELEASE=(\d+\.\d+)', info)
    if match:
        return float(match.group(1))


def mkdir(c, paths, owner=None, mode=None,
          use_sudo=False, runas_user=None):
    """
    Recursively make one or more directories.
    """
    if isinstance(paths, str):
        paths = [paths]
    cmd = 'mkdir --parents {}'.format(' '.join(paths))
    if use_sudo:
        c.sudo(cmd, user=runas_user)
    else:
        c.run(cmd)
    if owner:
        if ':' not in owner:
            owner = '{0}:{0}'.format(owner)
        func = c.sudo if use_sudo else c.run
        func('chown {} {}'.format(owner, ' '.join(paths)))
    if mode is not None:
        func = c.sudo if use_sudo else c.run
        func('chmod {} {}'.format(mode, ' '.join(paths)))


def make_normal_user(c, username, full_name=None,
                     shell='/bin/bash',
                     password=None,
                     disabled_login=False):
    """
    Make a new "normal" user account.

    :param disabled_login: If true, will leave the account in a
       non-usable state, i.e. with invalid shell.
    """
    # do not bother if user exists
    missing = c.run(f'getent passwd {username}', warn=True).failed
    if not missing:
        return

    # nb. specify --disabled-login to avoid being prompted for password
    c.sudo("adduser --gecos '{}' --disabled-login {}".format(full_name or username,
                                                             username))

    # then fix the shell unless we shouldn't
    if not disabled_login:
        c.sudo(f'usermod -s {shell} {username}')

    # and maybe set password
    if password:
        c.sudo(f"bash -c 'echo {username}:{password} | chpasswd'",
               echo=False)


def make_system_user(c, name, home=None, uid=None, shell=None,
                     disabled_password=None):
    """
    Make a new system user account, with the given home folder and shell path.
    """
    if not c.run('getent passwd {}'.format(name), warn=True).failed:
        return

    home = '--home {}'.format(home) if home else ''
    uid = '--uid {}'.format(uid) if uid else ''
    shell = '--shell {}'.format(shell) if shell else ''
    disabled_password = '--disabled-password' if disabled_password else ''
    c.sudo('adduser --system --group {} {} {} {} {}'.format(name, home, uid, shell,
                                                            disabled_password))


def set_timezone(c, timezone):
    """
    Set the system timezone to the given value, e.g. 'America/Chicago'.
    """
    c.sudo("bash -c 'echo {} > /etc/timezone'".format(timezone))
    if is_link(c, '/etc/localtime'):
        c.sudo('ln --symbolic --force /usr/share/zoneinfo/{} /etc/localtime'.format(timezone))
    else:
        c.sudo('cp /usr/share/zoneinfo/{} /etc/localtime'.format(timezone))


def put(c, local_path, remote_path, owner=None, mode=None,
        use_sudo=False, **kwargs):
    """
    Put a file on the server, and set its ownership.
    """
    # TODO: are we mirroring now?
    # if 'mode' not in kwargs:
    #     kwargs.setdefault('mirror_local_mode', True)

    # upload file
    if use_sudo:
        tempdir = c.run('mktemp -d').stdout.strip()
        basename = os.path.basename(remote_path)
        temp_path = os.path.join(tempdir, basename)
        c.put(local_path, temp_path, **kwargs)
        # TODO: need to address single quotes within filename
        if not owner:
            c.sudo("chown root: '{}'".format(temp_path))
        c.sudo("mv '{}' '{}'".format(temp_path, remote_path))
        c.run('rmdir {}'.format(tempdir))
    else:
        c.put(local_path, remote_path, **kwargs)

    # set owner / mode if needed
    func = c.sudo if use_sudo else c.run
    if owner:
        if ':' not in owner:
            owner = '{}:'.format(owner)
        func("chown {} '{}'".format(owner, remote_path))
    if mode:
        func("chmod {} '{}'".format(mode, remote_path))


def upload_mako_template(c, local_path, remote_path, context={},
                         encoding='utf_8', **kwargs):
    """
    Render a local file as a Mako template, and upload the result to the server.
    """
    template = Template(filename=local_path)

    temp_dir = tempfile.mkdtemp(prefix='rattail-fabric.')
    temp_path = os.path.join(temp_dir, os.path.basename(local_path))
    text = template.render(**context)
    with open(temp_path, 'wt', encoding=encoding) as f:
        f.write(text)
    os.chmod(temp_path, os.stat(local_path).st_mode)

    put(c, temp_path, remote_path, **kwargs)
    os.remove(temp_path)
    os.rmdir(temp_dir)


class Deployer(object):

    def __init__(self, deploy_path, last_segment='deploy'):
        if not os.path.isdir(deploy_path):
            deploy_path = os.path.abspath(os.path.join(os.path.dirname(deploy_path), last_segment))
        self.deploy_path = deploy_path

    def __call__(self, c, local_path, remote_path, **kwargs):
        self.deploy(c, local_path, remote_path, **kwargs)

    def full_path(self, local_path):
        if local_path.startswith('/'):
            return local_path
        return '{}/{}'.format(self.deploy_path, local_path)

    def local_exists(self, local_path):
        return os.path.exists(self.full_path(local_path))

    def deploy(self, c, local_path, remote_path, context={}, **kwargs):
        local_path = self.full_path(local_path)
        if local_path.endswith('.template'):
            raise NotImplementedError
        elif local_path.endswith('.mako'):
            upload_mako_template(c, local_path, remote_path, context=context, **kwargs)
        else:
            put(c, local_path, remote_path, **kwargs)

    def sudoers(self, c, local_path, remote_path, owner='root:', mode='0440', **kwargs):
        self.deploy(c, local_path, '/tmp/sudoers', owner=owner, mode=mode, use_sudo=True, **kwargs)
        c.sudo('mv /tmp/sudoers {}'.format(remote_path))

    def apache_site(self, c, local_path, name, **kwargs):
        from rattail_fabric2.apache import deploy_site
        kwargs['use_sudo'] = True
        deploy_site(c, self, local_path, name, **kwargs)

    def apache_conf(self, c, local_path, name, **kwargs):
        from rattail_fabric2.apache import deploy_conf
        kwargs['use_sudo'] = True
        deploy_conf(c, self, local_path, name, **kwargs)

    def backup_app(self, c, envname='backup', *args, **kwargs):
        from rattail_fabric2.backup import deploy_backup_app
        deploy_backup_app(c, self, envname, *args, **kwargs)

    def certbot_account(self, c, uuid, localdir='certbot/account',
                        version='01'):
        """
        Deploy files to establish a certbot account on target server
        """
        from .util import exists

        localdir = localdir.rstrip('/')
        paths = [
            '/etc/letsencrypt/accounts',
            '/etc/letsencrypt/accounts/acme-v{}.api.letsencrypt.org'.format(version),
            '/etc/letsencrypt/accounts/acme-v{}.api.letsencrypt.org/directory'.format(version),
        ]
        final_path = '{}/{}'.format(paths[-1], uuid)
        paths.append(final_path)
        if not exists(c, final_path, use_sudo=True):
            mkdir(c, paths, mode='0700', use_sudo=True)
            self.deploy(c, '{}/private_key.json'.format(localdir), '{}/private_key.json'.format(final_path), mode='0600', use_sudo=True)
            self.deploy(c, '{}/meta.json'.format(localdir), '{}/meta.json'.format(final_path), use_sudo=True)
            self.deploy(c, '{}/regr.json'.format(localdir), '{}/regr.json'.format(final_path), use_sudo=True)

    def soffice_daemon(self, c, local_path, name=None, register=True, start=True, **kwargs):
        """
        Deploy a "soffice" (headless LibreOffice) daemon.
        """
        warnings.warn("deploy.soffice_daemon() is deprecated as it only supports "
                      "/etc/init.d scripts.  please deploy your own systemd config "
                      "instead, as needed.", DeprecationWarning)
        if name is None:
            name = local_path.split('/')[-1]
        kwargs.setdefault('use_sudo', True)
        kwargs.setdefault('mode', '0755')
        self.deploy(c, local_path, '/etc/init.d/{}'.format(name), **kwargs)
        if register:
            c.sudo('update-rc.d {} defaults'.format(name))
            if start:
                c.sudo('service {} restart'.format(name))


def make_deploy(deploy_path, last_segment='deploy'):
    """
    Make a ``deploy()`` function, for uploading files to the server.

    During a deployment, one usually needs to upload certain additional files
    to the server.  It's also often necessary to dynamically define certain
    settings etc. within these files.  The :func:`upload_template()` and
    :func:`put()` functions, respectively, handle uploading files which do and
    do not require dynamic variable substitution.

    The return value from ``make_deploy()`` is a function which will call
    ``put()`` or ``upload_template()`` based on whether or not the file path
    ends with ``'.template'``.

    To make the ``deploy()`` function even simpler for the caller, it will
    assume a certain context for local file paths.  This means one only need
    provide a base file name when calling ``deploy()``, and it will be
    interpreted as relative to the function's context path.

    The ``deploy_path`` argument is used to establish the context path for the
    function.  If it is a folder path, it will be used as-is; otherwise it will
    be constructed by joining the parent folder of ``deploy_path`` with the
    value of ``last_segment``.

    Typical usage then is something like::

       from rattail_fabric import make_deploy

       deploy = make_deploy(__file__)

       deploy('rattail/init-filemon', '/etc/init.d/rattail-filemon',
              mode='0755')

       deploy('rattail/rattail.conf.template', '/etc/rattail.conf')

    This shows what is intended to be typical, i.e. where ``__file__`` is the
    only argument required for ``make_deploy()``.  For the above to work will
    require you to have something like this file structure, where
    ``fabfile.py`` is the script which contains the above code::

       myproject/
       |-- fabfile.py
       |-- deploy/
           `-- rattail/
               |-- init-filemon
               |-- rattail.conf.template
    """
    return Deployer(deploy_path, last_segment)


def rsync(c, host, *paths, files=False, target=None):
    """
    Runs rsync as root, for the given host and file paths.

    :param files: If set, this indicates that each of the ``paths``
       are actual files, as opposed to directories.

    :param target: If set, this will be used instead of the given
       path, for destination path.  This only works correctly if
       ``paths`` contains only one path.
    """
    for path in paths:
        assert path.startswith('/')
        path = path.rstrip('/')
        # escape path for rsync
        path = path.replace(' ', r'\\\ ').replace("'", r"\\\'")
        suffix = '' if files else '/'
        agent_sudo(c, f'rsync -aP --del root@{host}:{path}{suffix} {target or path}')

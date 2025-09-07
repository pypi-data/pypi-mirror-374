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
Fabric library for Node.js
"""

import os

from rattail_fabric2 import append, exists
from rattail_fabric2.util import get_home_path


def install(c, version=None, user=None):
    """
    Install nvm and node.js for given user, or else "connection" user.
    """
    home = get_home_path(c, user)
    nvm = os.path.join(home, '.nvm')

    if not exists(c, nvm):
        cmd = "bash -c 'curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.5/install.sh | bash'"
        if user:
            c.sudo(cmd, user=user)
        else:
            c.run(cmd)

    profile = os.path.join(home, '.profile')
    kwargs = {'use_sudo': bool(user)}
    if kwargs['use_sudo']:
        c.sudo(f'touch {profile}')
        c.sudo(f'chown {user}: {profile}')
    append(c, profile, 'export NVM_DIR="{}"'.format(nvm), **kwargs)
    append(c, profile, '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"', **kwargs)
    append(c, profile, '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"', **kwargs)

    node = version or 'node'
    cmd = "bash -l -c 'nvm install {}'".format(node)
    if user:
        c.sudo(cmd, user=user)
    else:
        c.run(cmd)

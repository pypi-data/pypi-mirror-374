# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2024 Lance Edgar
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
Tasks for rattail-fabric2
"""

import os
import re
import shutil

from invoke import task


here = os.path.abspath(os.path.dirname(__file__))
__version__ = None
pattern = re.compile(r'^version = "(\d+\.\d+\.\d+)"$')
with open(os.path.join(here, 'pyproject.toml'), 'rt') as f:
    for line in f:
        line = line.rstrip('\n')
        match = pattern.match(line)
        if match:
            __version__ = match.group(1)
            break
if not __version__:
    raise RuntimeError("could not parse version!")


@task
def release(c):
    """
    Release a new version of 'rattail-fabric2'.
    """
    if os.path.exists('rattail_fabric2.egg-info'):
        shutil.rmtree('rattail_fabric2.egg-info')
    # TODO: this seems heavy-handed? for sake of recursive-include in MANIFEST
    # TODO: what i esp. don't like is, this doesn't consider .gitignore
    c.run("find . -name '*~' -delete")
    c.run('python -m build --sdist')
    c.run(f'twine upload dist/rattail_fabric2-{__version__}.tar.gz')

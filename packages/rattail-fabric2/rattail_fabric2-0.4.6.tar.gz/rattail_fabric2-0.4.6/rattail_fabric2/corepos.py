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
Fabric library for CORE-POS (IS4C)
"""

import os

from rattail_fabric2 import mysql, exists, make_deploy, mkdir


deploy_generic = make_deploy(__file__)


def install_corepos(c, rootdir, rooturl_office, production=True,
                    user='www-data',
                    repo='https://github.com/CORE-POS/IS4C.git',
                    branch='master',
                    mysql_username='corepos',
                    mysql_password='corepos',
                    mysql_name_prefix='',
                    composer='composer.phar',
                    composer_install=True,
                    make_shadowread=False,
                    fannie_config=True):
    """
    Install the CORE software to the given location.

    This will clone CORE code to the ``IS4C`` folder within the
    specified ``rootdir`` location.
    """
    rooturl_office = rooturl_office.rstrip('/')

    mkdir(c, rootdir, use_sudo=True, owner=user)

    # CORE source
    is4c = os.path.join(rootdir, 'IS4C')
    if not exists(c, is4c):
        c.sudo('git clone --branch {} {} {}'.format(branch, repo, is4c),
               user=user)
    if production:
        c.sudo('rm -f {}/fannie/DEV_MODE'.format(is4c), user=user)
    else:
        c.sudo('touch {}/fannie/DEV_MODE'.format(is4c), user=user)

    # composer install
    if composer_install:
        # TODO: these 'allow' entries are needed for composer 2.4 at least...
        c.sudo("bash -c 'cd {} && {} config --global --no-plugins allow-plugins.composer/installers true'".format(is4c, composer),
               user=user)
        c.sudo("bash -c 'cd {} && {} config --global --no-plugins allow-plugins.oomphinc/composer-installers-extender true'".format(is4c, composer),
               user=user)
        c.sudo("bash -c 'cd {} && {} config --global --no-plugins allow-plugins.corepos/composer-installer true'".format(is4c, composer),
               user=user)
        c.sudo("bash -c 'cd {} && {} install'".format(is4c, composer),
               user=user)
        # TODO: (why) is 'update' needed instead of 'install' ?
        # c.sudo("bash -c 'cd {} && {} update'".format(is4c, composer),
        #        user=user)

    # shadowread
    if make_shadowread:
        c.sudo("bash -c 'cd {}/fannie/auth/shadowread && make'".format(is4c),
               user=user)
        # nb. must run `make install` as root
        c.sudo("bash -c 'cd {}/fannie/auth/shadowread && make install'".format(is4c))

    # fannie databases
    mysql.create_db(c, '{}core_op'.format(mysql_name_prefix),
                    user='{}@localhost'.format(mysql_username))
    mysql.create_db(c, '{}core_trans'.format(mysql_name_prefix),
                    user='{}@localhost'.format(mysql_username))
    mysql.create_db(c, '{}trans_archive'.format(mysql_name_prefix),
                    user='{}@localhost'.format(mysql_username))

    # fannie config
    if fannie_config:
        remote_path = '{}/IS4C/fannie/config.php'.format(rootdir)
        if not exists(c, remote_path):
            if fannie_config is True:
                fannie_config = 'corepos/fannie-config.php.mako'
            deploy_generic(c, fannie_config, remote_path,
                           use_sudo=True, owner='www-data:{}'.format(user), mode='0640',
                           context={'rootdir': rootdir,
                                    'rooturl': rooturl_office,
                                    'mysql_username': mysql_username,
                                    'mysql_password': mysql_password,
                                    'mysql_name_prefix': mysql_name_prefix})

    # office logging
    mkdir(c, f'{is4c}/fannie/logs', use_sudo=True,
          owner=f'{user}:www-data', mode='0775')
    c.sudo(f"bash -c 'cd {is4c}/fannie/logs && touch fannie.log debug_fannie.log'",
           user='www-data')

    # lane logging
    mkdir(c, f'{is4c}/pos/is4c-nf/log', use_sudo=True,
          owner=f'{user}:www-data', mode='0775')
    c.sudo(f"bash -c 'cd {is4c}/pos/is4c-nf/log && touch lane.log debug_lane.log'",
           user='www-data')


# TODO: deprecate / remove this
def install_fannie(c, rootdir, user='www-data', branch='version-2.10',
                   mysql_user='is4c', mysql_pass='is4c'):
    """
    Install the Fannie app to the given location.

    Please note, this assumes composer is already installed and available.
    """
    mkdir(c, rootdir, owner=user, use_sudo=True)

    # fannie source
    is4c = os.path.join(rootdir, 'IS4C')
    if not exists(c, is4c):
        c.sudo('git clone https://github.com/CORE-POS/IS4C.git {}'.format(is4c), user=user)
        c.sudo("bash -c 'cd {}; git checkout {}'".format(is4c, branch), user=user)
        c.sudo("bash -c 'cd {}; git pull'".format(is4c), user=user)

    # fannie dependencies
    mkdir(c, [os.path.join(is4c, 'vendor'),
              os.path.join(is4c, 'fannie/src/javascript/composer-components')],
          owner=user, use_sudo=True)
    c.sudo("bash -c 'cd {}; composer.phar install'".format(is4c), user=user)

    # shadowread
    # TODO: check first; only 'make' if necessary
    c.sudo("bash -c 'cd {}/fannie/auth/shadowread; make'".format(is4c), user=user)
    c.sudo("bash -c 'cd {}/fannie/auth/shadowread; make install'".format(is4c)) # as root!

    # fannie logging
    c.sudo("bash -c 'cd {}/fannie/logs; touch fannie.log debug_fannie.log queries.log php-errors.log dayend.log'".format(is4c), user=user)

    # fannie databases
    mysql.create_user(c, mysql_user, host='%', password=mysql_pass)
    mysql.create_db(c, 'core_op', user="{}@'%'".format(mysql_user))
    mysql.create_db(c, 'core_trans', user="{}@'%'".format(mysql_user))
    mysql.create_db(c, 'trans_archive', user="{}@'%'".format(mysql_user))

# -*- coding: utf-8; -*-

import argparse
import os
import socket
import subprocess
import sys


def check_mounts(mountpoints):
    for path in mountpoints:
        sys.stdout.write("{} is {}mounted\n".format(
            path, '' if is_mounted(path) else 'NOT '))


def check_mounts_collectd(mountpoints):

    hostname = os.environ.get('COLLECTD_HOSTNAME')
    if not hostname:
        hostname = socket.getfqdn()

    plugin = 'mountpoints'

    interval = os.environ.get('COLLECTD_INTERVAL')
    if interval:
        interval = ' interval={}'.format(interval)
    else:
        interval = ''

    for path in mountpoints:
        name = path.strip('/').replace('/', '-')
        plugin_instance = '{}-{}'.format(plugin, name)

        data_type = 'gauge-state'

        value = 1 if is_mounted(path) else 0
        value = 'N:{}'.format(value)

        msg = 'PUTVAL {}/{}/{}{} {}\n'.format(
            hostname,
            plugin_instance,
            data_type,
            interval,
            value)

        sys.stdout.write(msg)


def is_mounted(path):
    cmd = "mount | grep '{}' || true".format(path)
    output = subprocess.check_output(cmd, shell=True)
    return bool(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--collectd', action='store_true')
    parser.add_argument('mountpoints', nargs='+', metavar='MOUNTPOINT')
    args = parser.parse_args()
    if args.collectd:
        check_mounts_collectd(args.mountpoints)
    else:
        check_mounts(args.mountpoints)

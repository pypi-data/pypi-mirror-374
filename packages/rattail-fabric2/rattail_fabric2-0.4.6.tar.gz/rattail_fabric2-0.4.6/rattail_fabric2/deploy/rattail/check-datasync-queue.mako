#!${envroot}/bin/python

import os
import sys
import argparse
import subprocess


def check_datasync_queue(timeout):
    os.chdir(sys.prefix)

    retcode = subprocess.call([
        'bin/rattail',
        '-c', 'app/${config}.conf',
        '--no-versioning',
        'datasync',
        '--timeout', timeout,
        'check',
    ])

    if retcode == 1:
        sys.exit(2)

    elif retcode:
        print("unknown issue")
        sys.exit(3)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('timeout')
    args = parser.parse_args()
    check_datasync_queue(args.timeout)

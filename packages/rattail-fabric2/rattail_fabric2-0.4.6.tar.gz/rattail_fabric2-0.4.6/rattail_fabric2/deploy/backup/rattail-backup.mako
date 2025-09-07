#!/bin/sh -e

if [ "$1" = "-v" -o "$1" = "--verbose" ]; then
    VERBOSE='--verbose'
    CONFIG='/srv/envs/${envname}/app/rattail.conf'
else
    VERBOSE=
    CONFIG='/srv/envs/${envname}/app/silent.conf'
fi

# sanity check
if [ "$HOME" != '/root' ]; then
    echo ''
    echo '$HOME is not /root - please run this as e.g.:'
    echo ''
    echo '   sudo -H rattail-backup [--verbose]'
    exit 1
fi

cd /srv/envs/${envname}

bin/rattail -c $CONFIG $VERBOSE backup $*

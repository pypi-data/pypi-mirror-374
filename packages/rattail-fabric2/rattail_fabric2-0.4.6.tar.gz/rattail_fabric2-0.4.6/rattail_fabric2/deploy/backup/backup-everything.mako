#!/bin/sh -e

if [ "$1" = "-v" -o "$1" = "--verbose" ]; then
    VERBOSE='--verbose'
    PROGRESS='--progress'
    CONFIG='/srv/envs/${envname}/app/rattail.conf'
else
    VERBOSE=
    PROGRESS=
    CONFIG='/srv/envs/${envname}/app/silent.conf'
fi

RATTAIL="/srv/envs/${envname}/bin/rattail --config=$CONFIG $PROGRESS $VERBOSE"
# nb. avoid rich-formatted traceback here since it's so "noisy"
export _TYPER_STANDARD_TRACEBACK=1


# sanity check
if [ "$HOME" != '/root' ]; then
    echo ''
    echo '$HOME is not /root - please run this as e.g.:'
    echo ''
    echo '   sudo -H backup-everything [--verbose]'
    exit 1
fi

# upgrade app
/srv/envs/${envname}/app/upgrade.sh $VERBOSE

# run backup
cd /srv/envs/${envname}
$RATTAIL backup

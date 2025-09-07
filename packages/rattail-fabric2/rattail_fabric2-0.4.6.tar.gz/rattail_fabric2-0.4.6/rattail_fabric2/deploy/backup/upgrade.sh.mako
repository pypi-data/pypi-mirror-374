#!/bin/sh -e

if [ "$1" = "-v" -o "$1" = "--verbose" ]; then
    VERBOSE='--verbose'
    QUIET=
    PROGRESSBAR='--progress-bar=on'
else
    VERBOSE=
    QUIET='--quiet'
    PROGRESSBAR='--progress-bar=off'
fi

PIP="sudo -H -u ${user} PIP_CONFIG_FILE=${envpath}/pip.conf ${envpath}/bin/pip"


# upgrade pip
$PIP install $QUIET $PROGRESSBAR --upgrade pip

# upgrade rattail
cd ${envpath}/src/rattail
if [ "$(sudo -H -u ${user} git status --porcelain)" != '' ]; then
   sudo -H -u ${user} git status
   exit 1
fi
sudo -H -u ${user} git pull $QUIET
find . -name '*.pyc' -delete
$PIP install $QUIET $PROGRESSBAR --upgrade --upgrade-strategy eager --editable .

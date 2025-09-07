#!/bin/bash
<%text>############################################################</%text>
#
# overnight automation for '${automation}'
#
<%text>############################################################</%text>

set -e

DATE=$1

if [ "$1" = "--verbose" ]; then
    DATE=$2
    VERBOSE='--verbose'
else
    VERBOSE=
fi

if [ "$DATE" = "" ]; then
    DATE=`date --date='yesterday' +%Y-%m-%d`
fi

LUIGI='${envroot}/bin/luigi --logging-conf-file logging.conf'
export PYTHONPATH=${appdir}

cd ${appdir}/luigi

$LUIGI --module luigitasks.overnight_${automation.lower()} Overnight${automation} --date $DATE

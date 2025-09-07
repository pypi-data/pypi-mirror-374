#!/bin/bash
${'#'}###############################################################################
#
# overnight "backups" automation
#
${'#'}###############################################################################

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

LUIGI='${envpath}/bin/luigi --logging-conf-file luigi-logging.conf'
export PYTHONPATH=${envpath}/app/

cd ${envpath}/app/luigi

$LUIGI --module luigitasks.overnight OvernightBackups --date $DATE

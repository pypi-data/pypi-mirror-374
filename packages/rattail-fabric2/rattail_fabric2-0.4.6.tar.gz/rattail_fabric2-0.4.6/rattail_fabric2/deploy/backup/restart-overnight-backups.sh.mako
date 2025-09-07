#!/bin/sh -e

DATE=`date --date='yesterday' +%Y-%m-%d`

echo "${envpath}/bin/rattail -c ${envpath}/app/silent.conf --no-versioning run-n-mail -S 'Backups (continued)' '${envpath}/app/overnight-backups.sh $DATE'" | at 'now + 1 minute'

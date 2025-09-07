#!/bin/sh -e
<%text>######################################################################</%text>
#
# rotate Luigi server log file
#
<%text>######################################################################</%text>

if [ "$1" = "--verbose" ]; then
    VERBOSE='--verbose'
else
    VERBOSE=
fi

/usr/sbin/logrotate $VERBOSE ${appdir}/luigi/logrotate.conf

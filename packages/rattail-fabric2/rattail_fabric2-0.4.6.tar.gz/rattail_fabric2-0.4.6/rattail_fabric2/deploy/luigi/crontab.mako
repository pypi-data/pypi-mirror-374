## -*- mode: conf; -*-

% if mailto:
MAILTO="${','.join(mailto)}"
% endif

# rotate logs and restart Luigi at *just before* 12:00am midnight
55 23 * * *  root  ${appdir}/rotate-luigi-logs.sh

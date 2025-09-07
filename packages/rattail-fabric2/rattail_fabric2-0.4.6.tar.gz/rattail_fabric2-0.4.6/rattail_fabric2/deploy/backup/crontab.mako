# -*- mode: conf; -*-

% if mailto:
MAILTO="${mailto}"
% endif

# backup everything of importance at ${pretty_time}
${'' if env.machine_is_live else '# '}${cron_time} * * *  root  /usr/local/bin/backup-everything

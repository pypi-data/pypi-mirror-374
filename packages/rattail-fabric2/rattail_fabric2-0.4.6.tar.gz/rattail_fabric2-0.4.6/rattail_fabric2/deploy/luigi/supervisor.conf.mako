## -*- mode: conf; -*-

[group:luigi]
programs=luigid

[program:luigid]
command=${envroot}/bin/luigid --logdir ${appdir}/luigi/log --state-path ${appdir}/luigi/state.pickle --address 127.0.0.1
directory=${appdir}/work
environment=LUIGI_CONFIG_PATH="${appdir}/luigi/luigi.cfg"
user=${user}
autostart=${'true' if autostart else 'false'}

## -*- mode: conf; -*-

[group:backup]
programs=luigid

[program:luigid]
command=${envpath}/bin/luigid --logdir ${envpath}/app/luigi/log --state-path ${envpath}/app/luigi/state.pickle --address ${listen_address}
directory=${envpath}/app/work
environment=LUIGI_CONFIG_PATH="${envpath}/app/luigi/luigi.cfg"
user=${user}

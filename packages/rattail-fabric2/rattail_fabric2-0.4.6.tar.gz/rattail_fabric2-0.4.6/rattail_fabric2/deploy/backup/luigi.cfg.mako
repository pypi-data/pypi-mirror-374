## -*- mode: conf; -*-

${'#'}###########################################################
#
# Luigi config
#
# cf. https://luigi.readthedocs.io/en/stable/configuration.html
#
${'#'}###########################################################


[core]

# Number of seconds to wait before timing out when making an API call. Defaults
# to 10.0
# (sometimes things can lag and we simply need to give it more time)
rpc-connect-timeout = 30

# The maximum number of retries to connect the central scheduler before giving
# up. Defaults to 3
# (occasional network issues can cause us to need more/longer retries)
rpc-retry-attempts = 10

# Number of seconds to wait before the next attempt will be started to connect
# to the central scheduler between two retry attempts. Defaults to 30
# (occasional network issues can cause us to need more/longer retries)
rpc-retry-wait = 60

[scheduler]
state_path = ${envpath}/app/luigi/state.pickle
% if history_db:
record_task_history = true

[task_history]
db_connection = ${history_db}
% endif

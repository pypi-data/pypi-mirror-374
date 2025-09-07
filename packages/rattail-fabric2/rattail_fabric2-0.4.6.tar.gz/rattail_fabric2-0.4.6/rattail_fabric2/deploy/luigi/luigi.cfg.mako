## -*- mode: conf; -*-

<%text>############################################################</%text>
#
# Luigi config
#
# cf. https://luigi.readthedocs.io/en/stable/configuration.html
#
<%text>############################################################</%text>


[core]
logging_conf_file = ${appdir}/luigi/logging.conf

% if LUIGI2:

# Number of seconds to wait before timing out when making an API call. Defaults
# to 10.0
# (sometimes things can lag for us and we simply need to give it more time)
rpc_connect_timeout = 60

# The maximum number of retries to connect the central scheduler before giving
# up. Defaults to 3
# (occasional network issues seem to cause us to need more/longer retries)
rpc_retry_attempts = 10

# Number of seconds to wait before the next attempt will be started to connect
# to the central scheduler between two retry attempts. Defaults to 30
# (occasional network issues seem to cause us to need more/longer retries)
rpc_retry_wait = 60

% endif

[retcode]
# cf. https://luigi.readthedocs.io/en/stable/configuration.html#retcode-config
# The following return codes are the recommended exit codes for Luigi
# They are in increasing level of severity (for most applications)
already_running=10
missing_data=20
not_run=25
task_failed=30
scheduling_error=35
unhandled_exception=40

[scheduler]
state_path = ${appdir}/luigi/state.pickle
% if db_connection:
record_task_history = true

[task_history]
db_connection = ${db_connection}
% endif

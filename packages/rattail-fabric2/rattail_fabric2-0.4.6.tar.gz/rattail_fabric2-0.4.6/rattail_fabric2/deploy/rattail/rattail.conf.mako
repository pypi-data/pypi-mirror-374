## -*- mode: conf; -*-

${'#'}#####################################################################
#
# machine-wide rattail config
#
${'#'}#####################################################################


${'#'}#############################
# rattail
${'#'}#############################

[rattail]
timezone.default = ${timezone}

[rattail.config]
configure_logging = true

[rattail.mail]
smtp.server = localhost
default.from = ${getattr(env, 'email_default_sender', 'rattail@localhost')}
default.to = ${', '.join(getattr(env, 'email_default_recipients', ['root@localhost']))}


${'#'}#############################
# logging
${'#'}#############################

[loggers]
keys = root, exc_logger, beaker, txn, sqlalchemy, django_db, flufl_bounce, requests

[handlers]
keys = file, console, email

[formatters]
keys = generic, console

[logger_root]
handlers = file, console
level = DEBUG

[logger_exc_logger]
qualname = exc_logger
handlers = email
level = ERROR

[logger_beaker]
qualname = beaker
handlers =
level = INFO

[logger_txn]
qualname = txn
handlers =
level = INFO

[logger_sqlalchemy]
qualname = sqlalchemy.engine
handlers =
# level = INFO

[logger_django_db]
qualname = django.db.backends
handlers =
level = INFO

[logger_flufl_bounce]
qualname = flufl.bounce
handlers =
level = WARNING

[logger_requests]
qualname = requests
handlers =
# level = WARNING

[handler_file]
class = handlers.WatchedFileHandler
args = ('rattail.log', 'a', 'utf_8')
formatter = generic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
formatter = console

[handler_email]
class = handlers.SMTPHandler
args = ('localhost', '${getattr(env, 'email_default_sender', 'rattail@localhost')}', ${getattr(env, 'email_default_recipients', ['root@localhost'])}, "[Rattail] Logging")
formatter = generic
level = ERROR

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(funcName)s: %(message)s
datefmt = %Y-%m-%d %H:%M:%S

[formatter_console]
format = %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s

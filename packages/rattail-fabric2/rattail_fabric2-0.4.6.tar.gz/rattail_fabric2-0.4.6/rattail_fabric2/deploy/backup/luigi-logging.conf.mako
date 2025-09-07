## -*- mode: conf; -*-

${'#'}###########################################################
#
# Luigi logging config
#
${'#'}###########################################################


[loggers]
keys = root

[handlers]
keys = file, console

[formatters]
keys = generic, console

[logger_root]
handlers = file, console
level = DEBUG

[handler_file]
class = handlers.RotatingFileHandler
args = ('${envpath}/app/luigi/log/luigi.log', 'a', 1000000, 20, 'utf_8')
formatter = generic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
formatter = console
level = WARNING

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s
datefmt = %Y-%m-%d %H:%M:%S

[formatter_console]
format = %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s

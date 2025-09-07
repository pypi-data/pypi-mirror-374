## -*- mode: conf; -*-

${appdir}/luigi/log/luigi.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 600 rattail rattail
}

${appdir}/luigi/log/luigi-server.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 600 rattail rattail
    postrotate
        supervisorctl restart luigi:luigid > /dev/null
    endscript
}

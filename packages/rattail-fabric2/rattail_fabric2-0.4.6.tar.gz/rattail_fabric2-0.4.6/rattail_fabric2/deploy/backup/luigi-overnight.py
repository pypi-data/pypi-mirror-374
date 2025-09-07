# -*- coding: utf-8; -*-
"""
Luigi tasks for "overnight backups"
"""

import subprocess
import logging

import luigi

from rattail.luigi import OvernightTask
from rattail.logging import LuigiSummaryFilter


# log WARNING for Luigi execution summary
logging.getLogger('luigi-interface').addFilter(LuigiSummaryFilter())


class BackupSomething(OvernightTask):
    """
    Backup the 'something' machine.
    """
    filename = 'backup-something'

    def run_command(self):
        # note, this command would assume a "local" machine backup
        # subprocess.check_call([
        #     'sudo', '/usr/local/bin/backup-everything',
        # ])
        print('backed something up!')


class BackupAnother(OvernightTask):
    """
    Backup the 'another' machine.
    """
    filename = 'backup-another'

    # note, you must daisy-chain the tasks together, so each task "requires"
    # the previous task.  (there probably should be a better way though?)
    # our goal with that is just to make sure they run sequentially.
    def requires(self):
        return BackupSomething(self.date)

    def run_command(self):
        # note, this command would assume a "remote" machine backup
        # (also assumes ssh keys/config have already been established)
        # subprocess.check_call([
        #     'ssh', '-o', 'ServerAliveInterval=120', 'another.example.com',
        #     'sudo', '/usr/local/bin/backup-everything',
        # ])
        print('backed another up!')


class OvernightBackups(luigi.WrapperTask):
    """
    Wrapper task for "overnight-backups" automation
    """
    date = luigi.DateParameter()

    # this is our "wrapper" task which is invoked from `overnight-backups.sh`
    # we list each sequential task here for clarity, even though that may be
    # redundant due to how we daisy-chain them via requires() above (i.e. we
    # might be able to just "require" the last task here? needs testing)
    def requires(self):
        yield BackupSomething(self.date)
        yield BackupAnother(self.date)

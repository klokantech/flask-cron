import re

from flask import current_app
from flask_script import Command
from schedule import Scheduler
from signal import signal, SIGINT, SIGTERM
from time import sleep


class Cron:

    pattern = re.compile(r'every (\d+ )?(\w+)(?: at (\d\d:\d\d))?$')

    def __init__(self, app=None):
        self.scheduler = Scheduler()
        self.stopped = True
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions['cron'] = self

    def task(self, when):
        def decorator(func):
            match = self.pattern.match(when)
            interval = match.group(1)
            if interval is not None:
                job = self.scheduler.every(int(interval))
            else:
                job = self.scheduler.every()
            getattr(job, match.group(2))
            time_str = match.group(3)
            if time_str is not None:
                job.at(time_str)
            job.do(func)
            return func
        return decorator

    def run(self):
        current_app.logger.info('Starting cron')
        self.stopped = False
        signal(SIGINT, lambda signo, frame: self.stop())
        signal(SIGTERM, lambda signo, frame: self.stop())
        while not self.stopped:
            self.scheduler.run_pending()
            sleep(self.scheduler.idle_seconds)
        current_app.logger.info('Terminating cron')

    def stop(self):
        self.stopped = True


@Command
def CronCommand():
    current_app.extensions['cron'].run()

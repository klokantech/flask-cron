import re

from click import Command
from schedule import Scheduler
from signal import signal, SIGINT, SIGTERM
from time import sleep


class Cron:

    pattern = re.compile(r'every (\d+ )?(\w+)(?: at (\d\d:\d\d))?$')

    def __init__(self, app=None):
        self.app = None
        self.scheduler = Scheduler()
        self.stopped = True
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.extensions['cron'] = self
        app.cli.add_command(Command('cron', callback=self.run))

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
        self.app.logger.info('Starting cron')
        self.stopped = False
        signal(SIGINT, self.stop)
        signal(SIGTERM, self.stop)
        while not self.stopped:
            self.scheduler.run_pending()
            sleep(self.scheduler.idle_seconds)
        self.app.logger.info('Terminating cron')

    def stop(self, signo=None, frame=None):
        self.stopped = True

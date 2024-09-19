import sys
from threading import Timer
from contextlib import ContextDecorator


class TimeReaper(ContextDecorator):

    stop_log = "Process stopped by timer after {time}s."

    def __init__(
        self, exit_callback,
        stop_time=10, logger=sys.stdout.write,
    ):
        if stop_time <= 0:
            raise AttributeError("`stop_time` should be a positive number.")

        self.stop_time = stop_time
        self.exit_callback = exit_callback
        self._alarm_thread = None
        self.logger = logger

    def __enter__(self, *args, **kwargs):
        self.set_alarm()

    def __exit__(self, *args, **kwargs):
        self.cancel_alarm()

    def cancel_alarm(self):
        if self._alarm_thread.is_alive():
            self._alarm_thread.cancel()

    def stop_process(self, *args, log=None):
        self.cancel_alarm()
        self.exit_callback()
        if self.logger:
            self.logger(f"\n{log}\n")

    def set_alarm(self):
        self._alarm_thread = Timer(
            self.stop_time, self.stop_process,
            kwargs={"log": self.stop_log.format(time=self.stop_time)},
        )
        self._alarm_thread.start()

import sys
from threading import Timer
from contextlib import ContextDecorator


class TimeReaper(ContextDecorator):

    def __init__(
        self, exit_callback,
        stop_time=10, logger=sys.stdout.write,
    ):
        if stop_time <= 0:
            raise AttributeError("`stop_time` should be a positive number.")

        self.exit_callback = exit_callback
        self.stop_time = stop_time
        self.logger = logger

    @property
    def stop_log(self):
        return f"Process stopped by timer after {self.stop_time}s."

    def __enter__(self, *args, **kwargs):
        self.set_alarm()

    def __exit__(self, *args, **kwargs):
        self.cancel_alarm()

    def cancel_alarm(self):
        if self._alarm_thread.is_alive():
            self._alarm_thread.cancel()

    def stop_process(self):
        self.cancel_alarm()
        self.exit_callback()
        if self.logger:
            self.logger(f"\n{self.stop_log}\n")

    def set_alarm(self):
        self._alarm_thread = Timer(self.stop_time, self.stop_process)
        self._alarm_thread.start()

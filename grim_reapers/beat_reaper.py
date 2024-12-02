# The `BeatReaper` class is a context manager that runs a beat function at a specified interval and
# triggers an exit callback when the beat function returns False.
import sys
from threading import Thread, Event
from contextlib import ContextDecorator


class BeatReaper(ContextDecorator):

    def __init__(
        self, exit_callback, beat_function,
        beat_interval=2, logger=sys.stdout.write,
    ):
        if beat_interval <= 0:
            raise AttributeError("`beat_interval` should be a positive number.")

        self.exit_callback = exit_callback
        self.beat_function = beat_function
        self.beat_interval = beat_interval
        self.beat_count = 0
        self._stop_thread = None
        self._beat_event = Event()
        self.logger = logger

    @property
    def stop_log(self):
        return f"Process stopped after {self.beat_count} beats."

    def __enter__(self, *args, **kwargs):
        self.start_beat_thread()

    def __exit__(self, *args, **kwargs):
        if self._stop_thread:
            self._stop_thread.join()

        self.cancel_beat_thread()

    def cancel_beat_thread(self):
        self._beat_event.set()
        self._beat_thread.join()

    def stop_process(self):
        self.cancel_beat_thread()
        self.exit_callback()
        if self.logger:
            self.logger(f"\n{self.stop_log}\n")

    def _call_beat_function(self):
        self.beat_count += 1
        try:
            if self.beat_function():
                return
        except Exception as err:
            self.logger(f'\n`{self.beat_function.__name__}` '
                        f'raised `{repr(err)}`')

        self._beat_event.set()
        self.start_stop_process_thread()

    def _full_sized_aortic_pump(self):
        self._call_beat_function()
        while not self._beat_event.wait(self.beat_interval):
            self._call_beat_function()

    def start_stop_process_thread(self):
        self._stop_thread = Thread(target=self.stop_process)
        self._stop_thread.start()

    def start_beat_thread(self):
        self._beat_thread = Thread(target=self._full_sized_aortic_pump)
        self._beat_thread.start()

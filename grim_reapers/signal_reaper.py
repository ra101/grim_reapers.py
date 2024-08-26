import os
import signal
import sys
from contextlib import ContextDecorator


class SignalReaper(ContextDecorator):

    stop_log = "Process stopped by `{sig_name}` signal."

    def __init__(
        self, exit_callback,
        sig_enums=(signal.SIGINT, signal.SIGTERM),
        logger=sys.stdout.write,
    ):
        self.exit_callback = exit_callback
        self.logger = logger

        # {Signal Enum: Original handler function for that Enum ...}
        self.sig_ohandler_map = {
            sig_enum: signal.getsignal(sig_enum)
            for sig_enum in sig_enums
        }

    def __enter__(self, *args, **kwargs):
        self.set_signals()

    def __exit__(self, *args, **kwargs):
        self.reset_signals()

    def stop_process(self, log=None):
        self.reset_signals()
        self.exit_callback()
        if self.logger and log:
            self.logger(f"\n{log}\n")

    def set_signals(self):

        if self.logger:
            self.logger(f"\nPID of this process: `{os.getpid()}`\n")

        for sig_enum in self.sig_ohandler_map:
            signal.signal(sig_enum, lambda *_: self.stop_process(
                log=self.stop_log.format(sig_name=sig_enum.name),
            ))

    def reset_signals(self):
        for sig_enum, original_handler in self.sig_ohandler_map.items():
            signal.signal(sig_enum, original_handler)

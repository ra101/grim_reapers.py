import os
import signal
import sys
from contextlib import ContextDecorator


class SignalReaper(ContextDecorator):

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

    @property
    def stop_log(self):
        return f"Process stopped by `{self.stopping_sig}` signal."

    def __enter__(self, *args, **kwargs):
        self.set_signals()

    def __exit__(self, *args, **kwargs):
        self.reset_signals()

    def stop_process(self, sig_name):
        self.stopping_sig = sig_name
        self.reset_signals()
        self.exit_callback()
        if self.logger:
            self.logger(f"\n{self.stop_log}\n")

    def set_signals(self):

        if self.logger:
            self.logger(f"\nPID of this process: `{os.getpid()}`\n")

        for sig_enum in self.sig_ohandler_map:
            signal.signal(
                sig_enum, lambda *_: self.stop_process(sig_name=sig_enum.name)
            )

    def reset_signals(self):
        for sig_enum, original_handler in self.sig_ohandler_map.items():
            signal.signal(sig_enum, original_handler)

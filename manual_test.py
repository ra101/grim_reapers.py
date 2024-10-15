import sys
import time
import argparse
from contextlib import ExitStack


import grim_reapers


DRIVER_RUN = True


def driver_function():
    spinner = [">    <", " >  < ", "  ><  ", "  <>  ", " <  > ", "<    >" ]
    idx, backspaces = 0, '\b'*100
    sys.stdout.write(f'Running Driver Code: [        ]{backspaces}')

    global DRIVER_RUN
    while DRIVER_RUN:
        sys.stdout.write(f'Running Driver Code: [ {spinner[idx]} ]{backspaces}')
        sys.stdout.flush()
        idx = (idx + 1) % 6
        time.sleep(0.2)


def stop_driver_function():
    global DRIVER_RUN
    DRIVER_RUN = False


REAPER_MAP = {
    'signal': grim_reapers.SignalReaper(stop_driver_function),
    'time': grim_reapers.TimeReaper(stop_driver_function, stop_time=5),
    'webhook': grim_reapers.WebhookReaper(stop_driver_function),
}


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description = 'CLI to test Grim Reapers.'
    )
    parser.add_argument(
        '--exit-early', '-e', help='Flag to exit early.', action='store_true')

    parser.add_argument(
        'reaper_types', metavar='reaper-types', nargs='+',
        help='Type of reapers.', choices=list(REAPER_MAP.keys())
    )
    args = parser.parse_args()

    with ExitStack() as stack:
        for reaper_type in args.reaper_types:
            stack.enter_context(REAPER_MAP[reaper_type])

        DRIVER_RUN = not args.exit_early
        driver_function()

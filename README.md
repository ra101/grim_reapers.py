# Grim Reapers
A collection of Context-Decorators to manage the termination of Python processes.

### Installation

```bash
pip install git+https://github.com/ra101/grim_reapers.py.git

# Install with other ratools.py utils.
pip install git+https://github.com/ra101/ratools.py.git
```



### Usage

Assume the following function needs to be gracefully terminated

```python
import time

DRIVER_RUN = True

def driver_function():
    global DRIVER_RUN
    while DRIVER_RUN:
        time.sleep(0.2)
```

and assume the following function is for terminating above function.

```python
def stop_driver_function():
    global DRIVER_RUN
    DRIVER_RUN = False
```



**We will use the following methods for calling reapers:**

```python
# Decorator
@reaper
def _driver_function()
	return driver_function()


# Context Manager
with reaper:
    driver_function()


# Context Manager (Multiple Reapers)
from contextlib import ExitStack

reaper = [...]

with ExitStack() as stack:
	for reaper in reapers:
		stack.enter_context(reaper)

	driver_function()
```
​	


#### 📟☠️ Signal Reaper

Terminates the process once the interrupt signal is received on its PID.

```python
from grim_reapers import SignalReaper


reaper = SignalReaper(
    exit_callback=stop_driver_function,
 	# sig_enums=(signal.SIGINT, signal.SIGTERM), logger=sys.stdout.write,
)
```

​	

#### 🕒☠️ Time Reaper

Terminates the process after a certain time period is over.

```python
from grim_reapers import TimeReaper


reaper = TimeReaper(
    exit_callback=stop_driver_function,
 	# stop_time=10, logger=sys.stdout.write,
)
```

​	

#### 🕸️☠️ Webhook Reaper

Terminates the process once a webhook is accessed.

```python
from grim_reapers import WebhookReaper


reaper = WebhookReaper(
    exit_callback=stop_driver_function,
 	# port=8342, logger=sys.stdout.write,
)
```

​	

#### 🫀☠️ Beat Reaper

Terminates the process once the beat_function stops returning true.

```python
from grim_reapers import BeatReaper


reaper = BeatReaper(
    exit_callback=stop_driver_function,
    beat_function=lambda check_beat: _return_true_false_or_exception(),
 	# beat_interval=2, logger=sys.stdout.write,
)
```

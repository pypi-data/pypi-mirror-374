# loggerric

**loggerric** is a lightweight Python utility library providing advanced logging, for CLI applications. It offers colorful, formatted output to make debugging, logging and tracking easier.

---

## Features

- **Logging**: Structured logging with levels: `INFO`, `WARN`, `ERROR`, `DEBUG` with highlight.
- **Pretty Printing**: Pretty print variables like arrays and dictionaries.
- **Progress Bars**: Real-time CLI progress bars with ETA calculations.
- **Prompts**: Interactive user input with optional choices and defaults.
- **Timers**: Measure execution time of code snippets.
- **Timestamps**: Optional, can be used independently, and support rolling differences.

---

## Installation

```bash
pip install loggerric
```

---

## Usage

### Logging

```python
from loggerric import Log, LogLevel

Log.pretty_print({ 'name': 'John Doe' }, indent=4)

Log.info("This is an info message", "This is also a message", ..., highlight=['This', 'message'])
Log.warn("This is a warning", ..., highlight='warning')
Log.error("This is an error", ..., quit_after_log=True, highlight='error')
Log.debug("This is a debug message", ..., highlight='debug')

# Enable or disable specific logging levels
Log.disable(LogLevel.DEBUG, LogLevel.WARN, ...)
Log.enable(LogLevel.DEBUG, ...)
```

### Progress Bar

```python
from loggerric import ProgressBar
from time import sleep

end_val = 50
bar = ProgressBar(end_value=end_val, name='Downloading', bar_length=40)
for i in range(1, end_val + 1):
    sleep(0.05)
    bar.update(i)
```

### Prompt

```python
from loggerric import prompt

# Simple input
name = prompt("Enter your name")

# Input with options
choice = prompt("Choose a letter", options=['a', 'b', 'c'], default='b', loop_until_valid=True, case_sensitive=False)
```

### Timer

```python
from loggerric import Timer
from time import sleep

with Timer(name='Calculation Timer'):
    sleep(1.5)
```

### Timestamp

```python
from loggerric import Timestamp, Log

Timestamp.set_format('{HH}:{MM}:{SS}.{MS} T+{dm}ms')

Log.info(Timestamp.get())
```
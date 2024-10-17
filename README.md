# Wazuh Agent Log Viewer (Windows)

This project is a Python-based GUI application designed for Windows that behaves like the Linux `tail` command. It reads the Wazuh Agent log file and displays the last lines in real-time, with autoscroll functionality, using a Tkinter graphical interface.

The application includes:
- A `ScrolledText` widget that displays the log contents.
- Color-coded log levels (`INFO` in blue, `WARNING` in orange, `ERROR` in red).
- Automatic scrolling to the latest lines when the log is updated, while allowing the user to manually scroll.
- Log autoscroll that pauses when the user manually scrolls away from the bottom and resumes when the user returns to the bottom.

## Features
- **Real-time Log Monitoring**: Continuously monitors the Wazuh Agent log file and updates the GUI with new log entries.
- **Color-Coded Logs**: Log entries are color-coded to highlight `INFO`, `WARNING`, and `ERROR` messages.
- **Autoscroll**: Automatically scrolls to the latest log entry unless the user manually scrolls up.
- **Tkinter GUI**: Easy-to-use graphical interface with real-time log viewing.

## Requirements

- Python 3.x (for running the code directly or compiling it)
- Libraries:
  - `tkinter`: GUI library for Python (included with Python for Windows).
  - `watchdog`: For monitoring file changes.
  - `logging`: For error logging.

You can install the required libraries with the following command:

```
pip install watchdog
pip install pyinstaller
pyinstaller --onefile --windowed --icon=C:\path\to\your\icon.ico osseclogviewer.py
```


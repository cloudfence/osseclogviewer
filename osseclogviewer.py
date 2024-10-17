#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Wazuh Agent Log Viewer
# Copyright (c) 2024 Cloudfence
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions, and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions, and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of Cloudfence nor the names of its contributors may be
#    used to endorse or promote products derived from this software without
#    specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# python -m PyInstaller --onefile --windowed --icon=C:\dev\wazuh-resources\favicon.ico --uac-admin osseclogviewer.py

import os
import tkinter as tk
from tkinter import scrolledtext
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import traceback
import logging

# Configure logging to log errors
logging.basicConfig(filename="ossec_log_viewer_errors.log", level=logging.ERROR)

class TailFileHandler(FileSystemEventHandler):
    def __init__(self, filepath, text_widget):
        self.filepath = filepath
        self.text_widget = text_widget
        self.autoscroll = True  
        self.text_widget.bind('<MouseWheel>', self.on_scroll)
        self.load_initial_content()

        # Create tags for colorization
        self.text_widget.tag_config('INFO', foreground='blue')
        self.text_widget.tag_config('WARNING', foreground='orange')
        self.text_widget.tag_config('ERROR', foreground='red')

    def load_initial_content(self):
        """Loads the initial content of the file when the app starts"""
        try:
            with open(self.filepath, 'r') as f:
                lines = f.readlines()
                # Show the last 100 lines
                last_lines = lines[-100:]
                # Insert initial content with color
                self.insert_colored_text(last_lines)  
        except Exception as e:
            logging.error(f"Error loading initial content: {e}")
            logging.error(traceback.format_exc())
            self.text_widget.insert(tk.END, f"Error loading file: {e}\n")

        self.scroll_to_end()

    def on_modified(self, event):
        """Triggered when the file is modified"""
        if event.src_path == self.filepath:
            self.update_text_widget()

    def update_text_widget(self):
        """Updates the content of the text widget when the file is modified"""
        try:
            with open(self.filepath, 'r') as f:
                lines = f.readlines()
                # Show the last 100 lines
                last_lines = lines[-100:]
                # Clear the widget
                self.text_widget.delete('1.0', tk.END) 
                # Insert new content with color                
                self.insert_colored_text(last_lines) 
        except Exception as e:
            logging.error(f"Error reading file: {e}")
            logging.error(traceback.format_exc())
            self.text_widget.insert(tk.END, f"Error reading file: {e}\n")

        # Only autoscroll if the user hasn't manually scrolled up
        if self.autoscroll:
            self.scroll_to_end()

    def insert_colored_text(self, lines):
        """Inserts text into the text widget and colorizes based on log level"""
        for line in lines:
            if 'ERROR' in line:
                self.text_widget.insert(tk.END, line, 'ERROR')
            elif 'WARNING' in line:
                self.text_widget.insert(tk.END, line, 'WARNING')
            elif 'INFO' in line:
                self.text_widget.insert(tk.END, line, 'INFO')
            else:
                self.text_widget.insert(tk.END, line)

    def scroll_to_end(self):
        """Scroll to the last line of the text widget"""
        self.text_widget.see(tk.END)

    def on_scroll(self, event):
        """Detect if the user manually scrolls and disable autoscroll"""
        # Get the current view position (top visible line) in the text widget
        visible_start = self.text_widget.index(tk.INSERT)
        total_lines = self.text_widget.index(tk.END)

        # If the user scrolls up and the last line is not visible, disable autoscroll
        if float(visible_start.split('.')[0]) < float(total_lines.split('.')[0]) - 1:
            self.autoscroll = False
        else:
            self.autoscroll = True

def on_closing(root, observer):
    """Handles the app closing to stop the observer and terminate properly"""
    if observer.is_alive():
        observer.stop()
        observer.join()
    root.destroy()  

def start_tail(filepath):
    """Starts the GUI and file observation"""
    if not os.path.exists(filepath):
        print(f"File {filepath} does not exist.")
        return
    
    # Set up the GUI
    root = tk.Tk()
    root.title("Wazuh Agent Log Viewer")

    # Set custom icon
    icon_path = r"C:\dev\wazuh-resources\favicon.ico"
    root.iconbitmap(icon_path)

    # Configure grid layout
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Create a scrolled text widget
    text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=30)
    text_widget.grid(row=0, column=0, sticky="nsew")

    # Create a file event handler and observer
    event_handler = TailFileHandler(filepath, text_widget)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(filepath), recursive=False)
    observer.start()

    # Handle window close (X button)
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, observer))

    # Run the Tkinter main loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == "__main__":
    log_file_path = r"C:\Program Files (x86)\ossec-agent\ossec.log"
    start_tail(log_file_path)

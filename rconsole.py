import Tkinter as tk
import threading
from fcntl import fcntl, F_SETFL
from os import O_NONBLOCK
import time

class ConsoleUpdater(threading.Thread):
    daemon = True
    keepgoing = True
    def __init__(self, consolewidget, process_stdout, interval = 0.1):
        threading.Thread.__init__(self)
        self.consolewidget = consolewidget
        # Set file handle to allow non-blocking read
        fcntl(process_stdout, F_SETFL, O_NONBLOCK)
        self.process_stdout = process_stdout
        self.interval = interval
        
    def run(self):
        while self.keepgoing:
            try:
                buf = self.process_stdout.read()
            except IOError: # Nothing to read
                time.sleep(self.interval)
                continue
            self.consolewidget.addtext(buf)
    
    def stop(self):
        """Stops the thread, and blocks until it finishes."""
        self.keepgoing = False
        self.join()

class ConsoleDisplay(tk.Text):
    def __init__(self, master=None, process=None, **options):
        options["state"] = tk.DISABLED
        tk.Text.__init__(self, master, **options)
        self.process = process
        if process:
            self.attach(process)
        self.updatelock = threading.Lock()
        
    def addtext(self, text):
        """Adds text to the end of the display in a thread-safe manner."""
        with self.updatelock:
            self.config(state=tk.NORMAL)
            self.insert(tk.END, text)
            self.config(state=tk.DISABLED)
            self.see(tk.END)
        
    def attach(self, process):
        """Attach a process (from subprocess.Popen) to the terminal,
        which will be updated from its stdout."""
        self.process = process
        self.updater = ConsoleUpdater(self, process.stdout)
        self.updater.start()

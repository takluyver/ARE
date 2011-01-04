import tkinter as tk
import threading
from queue import Queue
from .rexec import rconsoleexec

class ConsoleUpdater(threading.Thread):
    daemon = True
    def __init__(self, consolewidget):
        threading.Thread.__init__(self)
        self.consolewidget = consolewidget
        self.cmd_queue = Queue()
        
    def run(self):
        while True:
            next_cmd = self.cmd_queue.get()
            self.consolewidget.addtext("> "+next_cmd)
            output = rconsoleexec(next_cmd)
            print(repr(next_cmd),repr(output))
            self.consolewidget.addtext(output)

class ConsoleDisplay(tk.Text):
    def __init__(self, master=None, **options):
        options["state"] = tk.DISABLED
        tk.Text.__init__(self, master, **options)
        self.updatelock = threading.Lock()
        self.rpy_runner = ConsoleUpdater(self)
        self.rpy_runner.start()
        
    def addtext(self, text):
        """Adds text to the end of the display in a thread-safe manner."""
        with self.updatelock:
            self.config(state=tk.NORMAL)
            self.insert(tk.END, text)
            self.config(state=tk.DISABLED)
            self.see(tk.END)

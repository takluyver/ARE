import tkinter as tk
import threading
from queue import Queue
from .rexec import rconsoleexec, r_version_string

class ConsoleUpdater(threading.Thread):
    daemon = True
    def __init__(self, consolewidget):
        threading.Thread.__init__(self)
        self.consolewidget = consolewidget
        self.cmd_queue = Queue()
        
    def run(self):
        while True:
            next_cmd = self.cmd_queue.get()
            self.consolewidget.addtext("> "+next_cmd.rstrip() + "\n")
            output = rconsoleexec(next_cmd)
            #print(repr(next_cmd),repr(output))  #DEBUG
            self.consolewidget.addtext(output)


introtext = """Welcome to %s
Running in ARE, a simple R editor and runner for Linux.

Enter R commands below (shift-enter if you need more than one line), or edit scripts on the left hand side, and use the keyboard shortcuts or the menu items to run them here.

""" % r_version_string

class ConsoleDisplay(tk.Text):
    def __init__(self, master=None, **options):
        options["state"] = tk.DISABLED
        tk.Text.__init__(self, master, **options)
        self.updatelock = threading.Lock()
        self.rpy_runner = ConsoleUpdater(self)
        self.rpy_runner.start()
        self.addtext(introtext)
        
    def addtext(self, text):
        """Adds text to the end of the display in a thread-safe manner."""
        with self.updatelock:
            self.config(state=tk.NORMAL)
            self.insert(tk.END, text)
            self.config(state=tk.DISABLED)
            self.see(tk.END)

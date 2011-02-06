import tkinter as tk
import threading
from queue import Queue
from .rexec import rconsoleexec, r_version_string, rinterface

class ConsoleUpdater(threading.Thread):
    daemon = True
    def __init__(self, consolewidget):
        threading.Thread.__init__(self)
        self.console = consolewidget
        
    def run(self):
        while True:
            next_cmd = self.console.cmd_queue.get()
            self.console.replace_line(next_cmd + "\n")
            self.console.add_cmd_above(next_cmd)
            self.console.config(state=tk.DISABLED)
            output = rconsoleexec(next_cmd)
            #print(repr(next_cmd),repr(output))  #DEBUG
            self.console.addtext(output)
            self.console.prompt()


introtext = """Welcome to %s
Running in ARE, a simple R editor and runner for Linux.

Enter R commands below (shift-enter if you need more than one line), or edit scripts on the left hand side, and use the keyboard shortcuts or the menu items to run them here.

""" % r_version_string

class Console(tk.Text):
    def __init__(self, master=None, background="white", **options):
        tk.Text.__init__(self, master, background=background, **options)
        self.updatelock = threading.Lock()
        self.active_queue = self.cmd_queue = Queue()
        self.input_queue = Queue(1)
        self.rpy_runner = ConsoleUpdater(self)
        self.rpy_runner.start()
        self.cmds_above, self.cmds_below = [], []
        
        self.bind("<Home>", self.home)
        self.bind("<Up>", self.lineup)
        self.bind("<Down>", self.linedown)
        self.bind("<Return>", self.send_line)
        self.bind("<KP_Enter>", self.send_line)
        # Use shift-enter for multi-line entry, so allow default action
        self.bind("<Shift-Return>", lambda e: None)
        # Tk doesn't normally add a new line on numpad enter.
        self.bind("<Shift-KP_Enter>", lambda e: self.insert(tk.INSERT, "\n"))
        
        rinterface.set_readconsole(self.console_input)
        
        self.addtext(introtext)
        self.prompt()
        
    def home(self, e=None):
        self.mark_set(tk.INSERT, "cmd_start")
        return "break"
        
    def add_cmd_above(self, cmd):
        try:
            if cmd and (cmd != self.cmds_above[-1]):
                self.cmds_above.append(cmd)
        except IndexError:
            self.cmds_above.append(cmd)
        
    def lineup(self, e=None):
        if self.cmds_above:
            self.cmds_below.append(self.get_cmd())
            self.replace_cmd(self.cmds_above.pop())
        return "break"
        
    def linedown(self, e=None):
        if self.cmds_below:
            self.add_cmd_above(self.get_cmd())
            self.replace_cmd(self.cmds_below.pop())
        return "break"
        
    def prompt(self, prompt="> "):
        self.config(state=tk.NORMAL)
        with self.updatelock:
            self.insert(tk.END, prompt)
            self.mark_set(tk.INSERT, tk.END)
            self.mark_set("cmd_start", tk.INSERT)
            self.mark_gravity("cmd_start", tk.LEFT)
            
    def console_input(self, prompt):
        """Prompts the user for input, then blocks, and returns the text entered.
        Intended to be used in the execution thread, not the main (UI) thread."""
        self.prompt(prompt)
        self.active_queue = self.input_queue
        entered = self.input_queue.get()
        self.active_queue = self.cmd_queue
        self.insert(tk.END, "\n")
        return entered
            
    def replace_line(self, new_line):
        """Replaces the text after the prompt with the given string."""
        with self.updatelock:
            self.delete("cmd_start", tk.END)
            self.insert(tk.END, new_line)
            
    def get_line(self):
        """Returns the text after the prompt."""
        return self.get("cmd_start", tk.END).rstrip()
        
    def send_line(self, e=None):
        """Called when <Return> is pressed. Normally sends a command to
        cmd_queue, but console_input redirects this to input_queue."""
        self.active_queue.put(self.get_line())
        return "break"
        
    def addtext(self, text):
        """Adds text to the end of the display in a thread-safe manner."""
        with self.updatelock:
            self.config(state=tk.NORMAL)
            self.insert(tk.END, text)
            self.config(state=tk.DISABLED)
            self.see(tk.END)

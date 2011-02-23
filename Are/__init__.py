#!/usr/bin/env python3
import sys
from tkinter import *
from tkinter.ttk import Scrollbar  # Use newer scrollbar
from pygments.lexers import get_lexer_by_name
from . import rconsole, editor, saveload

class AREApp(Tk, saveload.SaveLoadMixin):
    def __init__(self):
        Tk.__init__(self)
        saveload.SaveLoadMixin.__init__(self)
        self.title("ARE")
                        
        # Left-right split
        split = PanedWindow(self, sashwidth=6)
        split.pack(fill=BOTH, expand=True)
        
        # Editor (left hand side)
        lexer = get_lexer_by_name("r")
        self.editor = editor.SyntaxHighlightingText(split, lexer)
        self.editor.bind("<F5>", self.editor_run_sel)
        self.editor.bind("<Control-F5>", self.editor_run_all)
        # This will mark the editor as changed since last save:
        self.editor.bind("<Key>", self.keyevent_dirty)
        split.add(self.editor)
        
        # Right hand side: console output...
        rhs = Frame(split)
        self.console = rconsole.Console(rhs)
        self.console.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar = Scrollbar(rhs, command=self.console.yview)
        self.console.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=LEFT, fill=Y)
        
        split.add(rhs)
            
        # Menus
        menubar = Menu(self)
        filemenu = Menu(menubar, tearoff=False)
        filemenu.add_command(label="New", command=self.newfile)
        filemenu.add_command(label="Open (Ctrl-O)", command=self.askopen)
        filemenu.add_command(label="Save (Ctrl-S)", command=self.quietsave)
        filemenu.add_command(label="Save as (Ctrl-Shift-S)", command=self.asksave)
        
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_command(label="Run line/selection (F5)", 
                            command=self.editor_run_sel)
        menubar.add_command(label="Run all (Ctrl-F5)",
                            command=self.editor_run_all)
        self.config(menu=menubar)
        
        # Keyboard shortcuts
        self.bind("<Control-s>", self.quietsave)
        self.bind("<Control-S>", self.asksave) # Capital S = Shift-S
        self.bind("<Control-o>", self.askopen)
        
        # Show the window
        self.editor.focus_set()
    
    def sendrcode(self, code):
        """Send an R statement to be executed."""
        self.console.rpy_runner.cmd_queue.put(code)
                        
    def editor_run_sel(self, e=None):
        try:
            startline = int(self.editor.index(SEL_FIRST).split('.')[0]) - 1
            endline = int(self.editor.index(SEL_LAST).split('.')[0])
        except TclError:  # No selection - use insert cursor
            startline = int(self.editor.index(INSERT).split('.')[0]) - 1
            endline = startline + 1
        self.editor_linesrunner(startline, endline)
        
    def editor_run_all(self, e=None):
        endline = int(self.editor.index(END).split('.')[0])
        self.editor_linesrunner(0, endline)
        
    def editor_linesrunner(self, startline, endline, ignore_comment_lines=True):
        """Run the lines of the editor from startline to endline. These should
        be numbers in the 0-based Python convention, and excludes endline (like
        slicing).
        
        This will run extra lines if the indicated lines have start or finish
        in the middle of a bracketed statement."""
        # Expand the selection based on brackets
        bracketmap = self.editor.map_bracketlevels()
        while bracketmap[startline] > 0:
            startline -= 1
        while endline < len(bracketmap) and bracketmap[endline] > 0:
            endline += 1
            
        lines = zip(bracketmap[startline:endline],
                    self.editor.getlines()[startline:endline])
        buf = []
        # Group into statements by brackets
        for bracketlevel, nextline in lines:
            if ignore_comment_lines and nextline.strip().startswith("#"):
                continue
            if bracketlevel > 0:
                buf.append(nextline)
            else:
                if buf:
                    self.sendrcode("\n".join(buf))
                buf = [nextline]
        # Send anything left in the buffer
        self.sendrcode("\n".join(buf))
        
    def inputeater(self, e=None):
        buf = self.input.get("1.0", END)
        self.sendrcode(buf)
        self.input.delete("1.0", END)
        return "break"

def main():
    root = AREApp()
    if len(sys.argv) > 1:
        fileeditor.load(sys.argv[1])
    root.mainloop()

if __name__ == '__main__':
    main()

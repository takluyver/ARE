#!/usr/bin/env python3
import sys
from tkinter import *
from tkinter.ttk import Scrollbar  # Use newer scrollbar
from subprocess import Popen, PIPE, STDOUT
from pygments.lexers import get_lexer_by_name
import rconsole, editor, saveload

class AREApp(Tk, saveload.SaveLoadMixin):
    def __init__(self):
        Tk.__init__(self)
        saveload.SaveLoadMixin.__init__(self)
        self.title("ARE")
        
        self.rprocess = Popen(["R","--interactive", "--no-save"],
                        stdin=PIPE, stdout=PIPE, stderr=STDOUT)
                        
        # Left-right split
        split = PanedWindow(self, sashwidth=6)
        split.pack(fill=BOTH, expand=True)
        
        # Editor (left hand side)
        lexer = get_lexer_by_name("r")
        self.editor = editor.SyntaxHighlightingText(split, lexer)
        self.editor.bind("<F5>", self.editorlinerunner)
        self.editor.bind("<Control-F5>", self.editorallrunner)
        split.add(self.editor)
        
        # Right hand side: console output...
        rhs = Frame(split)
        consoleframe = Frame(rhs)
        self.console = rconsole.ConsoleDisplay(consoleframe,
                                                process=self.rprocess)
        self.console.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar = Scrollbar(consoleframe, command=self.console.yview)
        self.console.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=LEFT, fill=Y)
        
        consoleframe.pack(fill=BOTH, expand=True)
        
        # ...and input
        self.input = Text(rhs, height=4, background="white")
        self.input.pack(fill=X)
        self.input.bind("<Return>", self.inputeater)
        # Use shift-enter for multi-line entry, so allow default action
        self.input.bind("<Shift-Return>", lambda e: None)
        
        split.add(rhs)
            
        # Menus
        menubar = Menu(self)
        menubar.add_command(label="Open", command=self.askopen)
        menubar.add_command(label="Save", command=self.quietsave)
        menubar.add_command(label="Save as", command=self.asksave)
        menubar.add_separator()
        menubar.add_command(label="Run line (F5)", 
                            command=self.editorlinerunner)
        menubar.add_command(label="Run all (Ctrl-F5)",
                            command=self.editorallrunner)
        self.config(menu=menubar)
        
        # Keyboard shortcuts
        self.bind("<Control-s>", self.quietsave)
        self.bind("<Control-S>", self.asksave) # Capital S = Shift-S
        self.bind("<Control-o>", self.askopen)
        
        # Show the window
        self.editor.focus_set()
    
    def sendrcode(self, code):
        self.rprocess.stdin.write(code.encode())
        self.rprocess.stdin.flush()
                        
    def editorlinerunner(self, e=None):
        bracketmap = self.editor.map_bracketlevels()
        startline = int(self.editor.index(INSERT).split('.')[0]) - 1
        while bracketmap[startline] > 0:
            startline -= 1
        endline = startline + 1
        while endline < len(bracketmap) and bracketmap[endline] > 0:
            endline += 1
        
        buf = self.editor.get("%d.0" % (startline+1),
                                "%d.0" % (endline+1))
        self.sendrcode(buf)
        
    def editorallrunner(self, e=None):
        buf = self.editor.get("1.0", END)
        self.sendrcode(buf)
        
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
    
    # Close down, without leaving an orphaned process.
    root.console.updater.stop()
    root.rprocess.terminate()

if __name__ == '__main__':
    main()

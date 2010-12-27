#!/usr/bin/env python
import Tkinter as tk
from subprocess import Popen, PIPE, STDOUT
from pygments.lexers import get_lexer_by_name
import rconsole, editor

def inputeater(process):
    def handler(e):
        buf = e.widget.get("1.0", tk.END)
        process.stdin.write(buf)
        e.widget.delete("1.0", tk.END)
        return "break"
    return handler
    
def editorlinerunner(process):
    def handler(e):
        bracketmap = e.widget.map_bracketlevels()
        startline = int(e.widget.index(tk.INSERT).split('.')[0]) - 1
        while bracketmap[startline] > 0:
            startline -= 1
        endline = startline + 1
        while endline < len(bracketmap) and bracketmap[endline] > 0:
            endline += 1
        
        buf = e.widget.get("%d.%d"%(startline+1,0), "%d.%d"%(endline+1,0))
        process.stdin.write(buf)
    return handler
    
def editorallrunner(process):
    def handler(e):
        buf = e.widget.get("1.0",tk.END)
        process.stdin.write(buf)
    return handler

if __name__ == '__main__':
    rprocess = Popen(["R","--interactive", "--no-save"], stdin=PIPE,
                        stdout=PIPE, stderr=STDOUT)
    
    # Left-right split
    root = tk.Tk()
    split = tk.PanedWindow(root, sashwidth=8)
    split.pack(fill=tk.BOTH, expand=True)
    
    # Editor (left hand side)
    lexer = get_lexer_by_name("r")
    editpane = editor.SyntaxHighlightingText(split, lexer)
    editpane.bind("<F5>", editorlinerunner(rprocess))
    editpane.bind("<Control-F5>", editorallrunner(rprocess))
    split.add(editpane)
    
    # Right hand side: console output...
    rhs = tk.Frame(split)
    consoleframe = tk.Frame(rhs)
    console = rconsole.ConsoleDisplay(consoleframe, process=rprocess)
    console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(consoleframe, command=console.yview)
    console.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.LEFT, fill=tk.Y)
    
    consoleframe.pack(fill=tk.BOTH, expand=True)
    
    # ...and input
    input = tk.Text(rhs, height=4, background="white")
    input.pack(fill=tk.X)
    input.bind("<Return>", inputeater(rprocess))
    
    split.add(rhs)
    
    # Show the window
    editpane.focus_set()
    root.mainloop()
    
    # Close down, without leaving an orphaned process.
    console.updater.stop()
    rprocess.terminate()

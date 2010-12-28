import Tkinter as tk
import tkFileDialog
import os.path

class FileEditor(object):
    filetypes = [("R script","*.r"),
    ("R script", "*.R"),
    ("All files", "*")]
    
    def __init__(self, editwidget):
        self.editwidget = editwidget
        self.lastfilename = None
        
    def load(self, filename):
        self.editwidget.delete("1.0", tk.END)
        with open(filename) as f:
            self.editwidget.insert(tk.END, f.read())
        self.editwidget.highlight()
        self.lastfilename = filename
            
    def save(self, filename):
        with open(filename, "w") as f:
            f.write(self.editwidget.get("1.0", tk.END))
        self.lastfilename = filename
            
    def saveas(self):
        initialdir, initialfile = "",""
        if self.lastfilename:
            initialdir, initialfile = os.path.split(self.lastfilename)
        fn = tkFileDialog.asksaveasfilename(defaultextension = ".r",
                    filetypes = self.filetypes,
                    initialdir = initialdir, initialfile = initialfile,
                    parent = self.editwidget)
        if fn:
            self.save(fn)
        
    def askopen(self):
        initialdir = ""
        if self.lastfilename:
            initialdir = os.path.split(self.lastfilename)[0]
        fn = tkFileDialog.askopenfilename(filetypes = self.filetypes,
                    initialdir = initialdir,
                    parent = self.editwidget)
        if fn:
            self.load(fn)

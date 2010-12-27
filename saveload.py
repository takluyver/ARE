import Tkinter as tk

class FileEditor(object):
    def __init__(self, editwidget):
        self.editwidget = editwidget
        
    def load(self, filename):
        self.editwidget.delete("1.0", tk.END)
        with open(filename) as f:
            self.editwidget.insert(tk.END, f.read())
            
    def save(self, filename):
        with open(filename, "w") as f:
            f.write(self.editwidget.get("1.0", tk.END))

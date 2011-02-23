import tkinter as tk
import tkinter.filedialog
import os.path

class SaveLoadMixin(object):
    """Include this class among a Tk application's parent classes to add
    methods to load from and save to file. This expects the application
    to have a self.editor widget like Tk's text widget."""
    filetypes = [("R script","*.r"),
    ("R script", "*.R"),
    ("All files", "*")]
    lastfilename = None
    editor_dirty = False
    
    @property
    def shortfilename(self):
        if self.lastfilename:
            return os.path.split(self.lastfilename)[-1]
        return ""
    
    def __init__(self):
        # Tell Tk to hide hidden files in dialogs. A bit hackish.
        # Borrowed from:
        # http://www.createphpbb.com/tovid/viewtopic.php?t=635
        try:
            self.tk.call('namespace', 'import', '::tk::dialog::file::')
            self.tk.call('set', '::tk::dialog::file::showHiddenBtn','1')
            self.tk.call('set', '::tk::dialog::file::showHiddenVar','0')
        except Exception:
            pass
    
    def load(self, filename):
        """Load the given filename immediately."""
        self.editor.delete("1.0", tk.END)
        with open(filename) as f:
            self.editor.insert(tk.END, f.read())
        self.editor.highlight()
        self.lastfilename = filename
        self.set_clean()
            
    def save(self, filename):
        """Save immediately to the given filename."""
        with open(filename, "w") as f:
            f.write(self.editor.get("1.0", tk.END))
        self.lastfilename = filename
        self.set_clean()
       
    # The below methods have a dummy parameter for use as event handlers
    def asksave(self, e=None):
        """Prompt the user for a filename, then save to it."""
        initialdir, initialfile = "",""
        if self.lastfilename:
            initialdir, initialfile = os.path.split(self.lastfilename)
        fn = tkinter.filedialog.asksaveasfilename(defaultextension = ".r",
                    filetypes = self.filetypes,
                    initialdir = initialdir, initialfile = initialfile,
                    parent = self)
        if fn:
            self.save(fn)
            
    def quietsave(self, e=None):
        """Save using the last filename opened or saved, or prompt the
        user if there isn't one."""
        if self.lastfilename:
            self.save(self.lastfilename)
        else:
            self.asksave()
        
    def askopen(self, e=None):
        """Prompt the user for a filename, then open it in the editor."""
        initialdir = ""
        if self.lastfilename:
            initialdir = os.path.split(self.lastfilename)[0]
        fn = tkinter.filedialog.askopenfilename(filetypes = self.filetypes,
                    initialdir = initialdir,
                    parent = self)
        if fn:
            self.load(fn)
    
    def newfile(self, e=None):
        """Clear the editor, and forget the last file name used."""
        self.editor.delete("1.0", tk.END)
        self.lastfilename = None
        self.set_clean()
    
    # Clean/dirty state    
    def keyevent_dirty(self, e):
        if e.char and not self.editor_dirty:
            self.set_dirty()
    
    def set_dirty(self):
        self.editor_dirty = True
        self.title("*"+self.shortfilename + " - ARE")

    def set_clean(self):
        self.editor_dirty = False
        self.title(self.shortfilename + " - ARE")

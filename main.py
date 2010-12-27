import Tkinter as tk
from string import ascii_letters, digits, punctuation
from pygments.lexers import get_lexer_by_name
from pygments.token import Literal, Comment
lexer = get_lexer_by_name("r")

class SyntaxHighlightingText(tk.Text):

    tags = {'kw': 'orange',
            'num': '#0099FF',    
            'str': 'green',
            'com': '#999999'}
    
    tokentags = {Literal.String: 'str',
                 Literal.Number: 'num',
                 Comment.Single: 'com'}
    #rkeywords = set(["
    
    def __init__(self, root, **options):
        tk.Text.__init__(self, root, background="white", **options)
        self.config_tags()
        self.characters = ascii_letters + digits + punctuation

        self.bind('<Key>', self.key_press)

    def config_tags(self):
        for tag, val in self.tags.items():
            self.tag_config(tag, foreground=val)

    def remove_tags(self, start, end):
        for tag in self.tags.keys():
            self.tag_remove(tag, start, end)

    def key_press(self, key):
        cline = self.index(tk.INSERT).split('.')[0]
        lineend = self.search("\n",self.index(tk.INSERT))

        buffer = self.get('%s.%d'%(cline,0),lineend)
        tokenized = lexer.get_tokens(buffer)

        self.remove_tags('%s.%d'%(cline, 0), lineend)
        
        start, end = 0, 0
        for ttype, token in tokenized:
            end = start + len(token)
            
            if ttype in self.tokentags:
                self.tag_add(self.tokentags[ttype], '%s.%d'%(cline, start), '%s.%d'%(cline, end))
            #if token in keyword.kwlist:
            #    self.tag_add('kw', '%s.%d'%(cline, start), '%s.%d'%(cline, end))
            #else:
            #    for index in range(len(token)):
            #        try:
            #            int(token[index])
            #        except ValueError:
            #            pass
            #        else:
            #            self.tag_add('int', '%s.%d'%(cline, start+index))

            start += len(token)

if __name__ == '__main__':
    root = tk.Tk()
    split = tk.PanedWindow(root, sashwidth=8)
    split.pack(fill=tk.BOTH, expand=True)
    
    editpane = SyntaxHighlightingText(split)
    split.add(editpane)
    
    rhs = tk.Frame(split)
    console = tk.Text(rhs)
    console.pack(fill=tk.BOTH, expand=True)
    input = tk.Text(rhs, height=4)
    input.pack(fill=tk.X, expand=True)
    split.add(rhs)
    
    editpane.focus_set()
    root.mainloop()

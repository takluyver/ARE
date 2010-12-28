import Tkinter as tk
from string import ascii_letters, digits, punctuation
from pygments.token import Literal, Comment, Punctuation

class SyntaxHighlightingText(tk.Text):

    tags = {'kw': 'orange',
            'num': '#0099FF',    
            'str': 'green',
            'com': '#999999'}
    
    tokentags = {Literal.String: 'str',
                 Literal.Number: 'num',
                 Comment.Single: 'com'}
    #rkeywords = set(["
    
    def __init__(self, root, lexer, **options):
        tk.Text.__init__(self, root, background="white", **options)
        self.config_tags()
        self.characters = ascii_letters + digits + punctuation
        self.lexer = lexer

        self.bind('<Key>', self.key_press)

    def config_tags(self):
        for tag, val in self.tags.items():
            self.tag_config(tag, foreground=val)

    def remove_tags(self, start, end):
        for tag in self.tags.keys():
            self.tag_remove(tag, start, end)
            
    def getlines(self):
        return self.get("1.0", tk.END).split("\n")[:-1]
        
    def map_bracketlevels(self):
        bracketlevels = [0]
        for line in self.getlines()[:-1]: # We needn't read the last line
            opened, closed = 0, 0
            for _, token in self.lexer.get_tokens(line):
                if token == "(":
                    opened += 1
                elif token == ")":
                    closed += 1
            newlevel = bracketlevels[-1] + opened - closed
            bracketlevels.append(newlevel if newlevel > 0 else 0)
        return bracketlevels

    def highlight(self, lineno=None):
        """Perform syntax highlighting on a specific line, or if no line
        is specified, on the entire text."""
        if not lineno:
            lastline = int(self.index(tk.END).split(".")[0])
            for x in xrange(lastline):
                self.highlight(x+1)
            return
        
        linestart = "%s.0" % lineno
        lineend = self.search("\n",linestart)
        self.remove_tags(linestart, lineend)
        buffer = self.get(linestart, lineend)
        tokenized = self.lexer.get_tokens(buffer)

        start, end = 0, 0
        for ttype, token in tokenized:
            end = start + len(token)
            
            if ttype in self.tokentags:
                self.tag_add(self.tokentags[ttype],
                             '%s.%d'%(lineno, start), '%s.%d'%(lineno, end))
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

    def key_press(self, key):
        cline = self.index(tk.INSERT).split('.')[0]
        self.highlight(cline)

from rpy2.robjects import r as R
from rpy2.rinterface import RRuntimeError, setWriteConsole

class TranslatedRRuntimeError(RRuntimeError):
    pass
    
NULL = R("NULL")

def Rexec(command):
    command = command.strip()
    if not command:
        return      # Special case for no input
    parsecommand = 'parse(text = "%s")' % command
    try:
        R('.__currexpr__ = ' + parsecommand)
    except RRuntimeError as e:
        parsecommand = parsecommand.replace("\n","\\n").replace("\t","\\t")
        raise TranslatedRRuntimeError("Error: " +\
                        e.args[0].partition(parsecommand + " : ")[2])
    try:
        result, visible = R('withVisible(eval(.__currexpr__))')
    except RRuntimeError as e:
        m = e.args[0].partition("eval(expr, envir, enclos) : ")[2]
        if m:
            raise TranslatedRRuntimeError("Error: " + m)
        else:
            raise TranslatedRRuntimeError(*e.args)
    visible = visible[0]
    if visible:
        return result

# There are various possibilities:
# * An error can be raised in parsing or evaling. We try to translate back
#     to the R error message, and show it.
# * The command may have a visible return value, e.g. "5 + 4", or not,
#     e.g. "a <- 1"
# * The command may cause output to the console, e.g. "print(1:4)".
consolebuffer = []
setWriteConsole(consolebuffer.append)
def Rconsoleexec(command):
    try:
        res = Rexec(command)
    except RRuntimeError as e:
        out = e.args[0]
    else:
        out = ""
        if consolebuffer:
            out += "".join(consolebuffer)
        if res:
            out += str(res) + "\n"
    del consolebuffer[:]
    return out

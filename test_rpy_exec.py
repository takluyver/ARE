from __future__ import print_function
from rpy_exec_test import Rconsoleexec

# Inputs and outputs
tests = [("123",'[1] 123\n'),
("print(123)\n",'[1] 123\n'),
("",""),
("   \n",""),
("NULL","NULL\n"),
(")", 'Error: unexpected \')\' in ")"\n'),
("(123\n", 'Error: unexpected end of input in "(123"\n'),
(")\n)","Error: unexpected ')' in \")\"\n"),
("a", "Error: object 'a' not found\n"),
("a=3*5", ""),
("a", '[1] 15\n'),
("pi", '[1] 3.141593\n'),
("a ~ B*c", 'a ~ B * c\n')]

def runtests():
    print("Starting tests")
    for input, correctoutput in tests:
        output = Rconsoleexec(input)
        assert output == correctoutput, "%s != %s    (from %s)" %\
                                        (output, correctoutput, input)
        print(".", end="")
    print("\n%d OK" % len(tests))
    
if __name__ == "__main__":
    runtests()

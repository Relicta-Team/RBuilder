from Constants import ExitCodes
import sys

def appExit(ex:ExitCodes):
    print("Exiting with code: {} ({})".format(ex.value,ex.name))
    if isExecutable():
        raise SystemExit(ex.value)
    else:
        exit(ex.value)
    
def isExecutable():
    return getattr(sys, 'frozen', False)
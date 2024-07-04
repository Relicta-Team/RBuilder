from Constants import ExitCodes
import sys

def appExit(ex:ExitCodes):
    if isExecutable():
        raise SystemExit(ex.value)
    else:
        exit(ex.value)
    
def isExecutable():
    return getattr(sys, 'frozen', False)
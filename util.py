from Constants import ExitCodes
import sys

def appExit(ex:ExitCodes|int):
    if isinstance(ex,ExitCodes):
        print("Exiting with code: {} ({})".format(ex.value,ex.name))
        if isExecutable():
            raise SystemExit(ex.value)
        else:
            exit(ex.value)
    else:
        print("Exiting with code: {}".format(ex))
        if isExecutable():
            raise SystemExit(ex)
        else:
            exit(ex)
    
def isExecutable():
    return getattr(sys, 'frozen', False)
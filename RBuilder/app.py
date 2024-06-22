import sys
import logging
from CLI import getParser
from Constants import ExitCodes
from util import appExit
import cfg

try:
    cobj = cfg.loadCfg()

    parser = getParser(cobj)
    #parser.print_help()
    args = parser.parse_args(['run'])
    
    if len(sys.argv) == 1:
        parser.print_help()
        appExit(ExitCodes.NO_ARGUMENTS_PROVIDED)

    paramDict = vars(args)

    if args.init:
        cfg.initCfg()

    if args.actionType == 'build':
        print("Building not supported in this version")
        appExit(ExitCodes.NOT_SUPPORTED)
    elif args.actionType == 'run':
        print("Running...")
    

except Exception as e:
    print(e)
    appExit(ExitCodes.UNKNOWN_FATAL_ERROR)
import sys
import logging
from CLI import getParser
from Constants import ExitCodes
from util import appExit
import cfg
import deploy
from AppCtx import AppContext

try:
    logging.basicConfig(level=logging.INFO,format='[%(name)s] %(levelname)s - %(message)s')
    ctx = AppContext()
    _mainLog = logging.getLogger("APP")
    ctx.setContextVar("main_logger",_mainLog)
    ctx.setContextVar("logger",_mainLog)
    
    cobj = ctx.setContextVar("cfg",cfg.loadCfg())

    ctx.logger.info("Starting...")

    parser = getParser(ctx,cobj)
    #parser.print_help()
    args = parser.parse_args(['-init','run'])
    ctx.setContextVar("args",args)
    
    if len(sys.argv) == 1:
        parser.print_help()
        appExit(ExitCodes.NO_ARGUMENTS_PROVIDED)

    paramDict = vars(args)

    if args.init:
        cfg.initCfg()
        if not deploy.deployMain(ctx): appExit(ExitCodes.UNKNOWN_FATAL_ERROR)

    if args.actionType == 'build':
        print("Building not supported in this version")
        appExit(ExitCodes.NOT_SUPPORTED)
    elif args.actionType == 'run':
        print("Running...")
    

except Exception as e:
    print(e)
    appExit(ExitCodes.UNKNOWN_FATAL_ERROR)
import sys
import logging
from CLI import getParser
from Constants import ExitCodes
from util import appExit
import cfg
import deploy
from Builder.package import buildProcess
from Runner import RBuilderRun
from AppCtx import AppContext

APP_VERSION = "1.0.0"

try:
    logging.basicConfig(level=logging.INFO,format='[%(name)s] %(levelname)s - %(message)s')
    ctx = AppContext()
    _mainLog = logging.getLogger("APP")
    ctx.setContextVar("main_logger",_mainLog)
    ctx.setContextVar("logger",_mainLog)
    
    cobj = ctx.setContextVar("cfg",cfg.loadCfg())

    ctx.logger.info("RBuilder version: {}".format(APP_VERSION))

    parser = getParser(ctx,cobj)
    #parser.print_help()
    # modes = [
    #     ['run','-f','DEBUG','-f',"TEST_ALGORITHMS","-ar"],
    #     ['-init','build'],
    #     ['b','-link']
    # ]
    # args = parser.parse_args(modes[0])
    args = parser.parse_args()
    ctx.setContextVar("args",args)
    
    if len(sys.argv) == 1:
        parser.print_help()
        appExit(ExitCodes.NO_ARGUMENTS_PROVIDED)

    paramDict = vars(args)

    if args.init:
        cfg.initCfg()
        if not deploy.deployMain(ctx): appExit(ExitCodes.UNKNOWN_FATAL_ERROR)

    if args.actionType in ('build','b','compile','make'):
        c = buildProcess(ctx)
        if not c:
            appExit(ExitCodes.UNKNOWN_FATAL_ERROR)
        appExit(ExitCodes.SUCCESS)
    elif args.actionType in ('run','r','start','exec'):
        appExit(RBuilderRun(ctx))
    
except KeyboardInterrupt:
    ctx.logger.warning("Pressed keyboard interrupt...")
    appExit(ExitCodes.USER_INTERRUPT)
except Exception as e:
    #print(e)
    ctx.logger.fatal(f"Unhandled exception: {e}; {e.with_traceback(e.__traceback__)}")
    appExit(ExitCodes.UNKNOWN_FATAL_ERROR)
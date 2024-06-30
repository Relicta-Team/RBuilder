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
    modes = [
        ['run','-f','RELEASE','-f',"VALCOUNT","123"],
        ['-init','build']
    ]
    args = parser.parse_args(modes[0])
    ctx.setContextVar("args",args)
    
    if len(sys.argv) == 1:
        parser.print_help()
        appExit(ExitCodes.NO_ARGUMENTS_PROVIDED)

    paramDict = vars(args)

    if args.init:
        cfg.initCfg()
        if not deploy.deployMain(ctx): appExit(ExitCodes.UNKNOWN_FATAL_ERROR)

    if args.actionType == 'build':
        buildProcess(ctx)
        appExit(ExitCodes.SUCCESS)
    elif args.actionType == 'run':
        appExit(RBuilderRun(ctx))
    

except Exception as e:
    print(e)
    appExit(ExitCodes.UNKNOWN_FATAL_ERROR)
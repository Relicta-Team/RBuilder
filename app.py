import sys
import logging
from CLI import getParser
from Constants import ExitCodes
from util import appExit
import cfg
import deploy
from Builder.package import buildProcess
from Runner import RBuilderRun
from deployCode.deployMain import deployProcess
from AppCtx import AppContext
from APP_VERSION import APP_VERSION
import os


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
    # args = parser.parse_args(modes[3])
    #args = parser.parse_args(['r','-d','TEST_IO','-d','DEBUG'])
    args = parser.parse_args()
    #temporary register src path
    src = os.path.join(args.ReSDK_dir,"Src")
    setattr(args, "src", src)
    
    ctx.setContextVar("args",args)
    ctx.setContextVar("parser",parser)

    if args.testapp:
        import os
        envvar = os.getenv('GITHUB_OUTPUT')
        if envvar != None:
            with open(envvar, "a") as f:
                f.write("RBUILDER_TESTAPP=OK")
        else:
            print("TESTAPP: OK")
        appExit(ExitCodes.SUCCESS)

    if args.verbose:
        ctx.setContextVar("verbose",True)
    
    if args.logToFile:
        _mainLog.addHandler(ctx.fileHandler)
    
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
    elif args.actionType in ('deploy','d','pack'):
        appExit(deployProcess(ctx))
    
except KeyboardInterrupt:
    if ctx.logger:
        ctx.logger.warning("Pressed keyboard interrupt...")
    else:
        print("Pressed keyboard interrupt...")
    appExit(ExitCodes.USER_INTERRUPT)
except Exception as e:
    if ctx.logger:
        ctx.logger.fatal(f"Unhandled exception: {e}; TB: {e.with_traceback(e.__traceback__)}")
    else:
        print(f"Unhandled exception: {e}; TB: {e.with_traceback(e.__traceback__)}")
    appExit(ExitCodes.UNKNOWN_FATAL_ERROR)
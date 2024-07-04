from AppCtx import AppContext
from Constants import *
from os.path import abspath as getAbsPath
from os.path import exists as fileExists
import os
import sys
import subprocess
import time
import win32gui
import win32process
import win32con
import psutil
from ctypes import *

def RBuilderRun(ctx:AppContext):
    ctx.setCurrentLogger("RB")

    ctx.logger.info("Starting...")

    rtCfg = ctx.cfg['runtime']
    vmDir = ctx.cfg['pathes']['vm_dir']
    macroCfg = ctx.cfg['defines']
    cfgFile = "init.cfg"
    runner = "cmp.exe"
    runnerPath = vmDir+"\\"+runner
    # -noLogs for disable logs !warning! - nologs not throws modal windows
    argsRun = f"-debug -config={cfgFile} -serverMod=""@server"" -port=5678 -filePatching -autoInit -limitFPS=150 -noSplash"
    prof = f"""-profiles={getAbsPath(vmDir)}\\profile"""

    if not fileExists(runnerPath):
        ctx.logger.error(f"Compiler not found: {getAbsPath(runnerPath)}. Please use init command")
        return ExitCodes.RBUILDER_RUN_FAILED
    if not fileExists(vmDir+"\\"+cfgFile):
        ctx.logger.error(f"Config not found: {getAbsPath(vmDir+"\\"+cfgFile)}. Please reinstall RBuilder")
        return ExitCodes.RBUILDER_RUN_FAILED

    preloadTimeout = rtCfg['preload_timeout']/1000 #ms to sec
    show_window = rtCfg['show_window']
    cleanup_logs_prestart = rtCfg['cleanup_logs_on_start']
    outputToRBuilder = rtCfg['rb_output']

    ctx.logger.info("Preparing macros")
    macroDict = {} #pre test defines
    macroList = [] #finalized dict of defines

    for md in ctx.args.macroDefines:
        macname = md[0]
        val = md[1] if len(md) > 1 else ""

        if macname in macroDict:
            ctx.logger.warning(f"Macro {macname} already defined. Value will be overwritten")
        else:
            macroDict[macname] = val or ""

    if process_defines(ctx,macroDict,macroCfg,macroList):
        ctx.logger.error("Failed to prepare defines")
        return ExitCodes.RBUILDER_RUN_FAILED_DEFINES_PREP

    ctx.logger.info("Added {} define flags from CLI".format(len(macroList)))

    if outputToRBuilder:
        macroList.append(createPreprocessorDefineCLI("RBUILDER_OUTPUT"))

    macroList.append(createPreprocessorDefineCLI("RBUILDER_DEFINE_LIST",f'createhashmapfromarray{[[m,v] for m,v in macroDict.items()]}'))

    cliArgs = f'{argsRun} {prof} {' '.join(macroList)}'
    cliArgsList = cliArgs.split(' ') + [prof] + macroList

    ctx.logger.info(f"Compiler: {getAbsPath(vmDir+"\\"+runner)}")
    ctx.logger.info(f"CLI: {cliArgs}")

    preloadTimeout = 50

    preloaded = False
    readyConsole = False

    stinf = subprocess.STARTUPINFO()
    stinf.hStdOutput = sys.stdout.fileno()
    stinf.hStdError = sys.stderr.fileno()
    #stinf.wShowWindow = subprocess.SW_HIDE
    
    #stinf.dwFlags = subprocess.STARTF_USESHOWWINDOW | subprocess.STARTF_USESTDHANDLES
    
    hndl = subprocess.Popen([runnerPath]+cliArgsList,
        stdout=sys.stdout.fileno(),
        #creationflags=subprocess.CREATE_NEW_CONSOLE,
        startupinfo=stinf
        )
    
    proc = psutil.Process(hndl.pid)
    
    log = open_rpt_log(hndl.pid)
    startTime = time.time()
    exitCode = ExitCodes.SUCCESS
    if log == None:
        ctx.logger.error("Can't open log file")

    while hndl.poll() is None:
        if log==None:
            log = open_rpt_log(hndl.pid)
        
        #region Preloader work
        if not preloaded:
            if time.time() - startTime > preloadTimeout:
                
                for line in read_and_get_info_from_rpt(log,True): 
                    ctx.logger.info(line)

                ctx.logger.error("Preloader timeout")

                #win32gui.ShowWindow(hndl.pid, win32con.SW_MAXIMIZE)
                
                #win32gui.SetWindowLong(10096302, win32con.GWL_STYLE,win32con.SW_HIDE) 
                hndl.kill()
                exitCode = ExitCodes.RBUILDER_RUN_LOADING_TIMEOUT
                break
        #endregion

        #region Hiding windows
        hwnds = get_hwnds_for_pid(hndl.pid)
        for hwnd in hwnds:
            if not readyConsole and process_hinig_windows(hwnd):
                readyConsole = True
            if win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & win32con.WS_EX_DLGMODALFRAME:
                
                for line in read_and_get_info_from_rpt(log,True): 
                    ctx.logger.info(line)
                    log.close()

                lstwid = []
                win32gui.EnumChildWindows(hwnd, lambda hwnd, param: lstwid.append(hwnd), 0)
                if len(lstwid) > 2:
                    ctx.logger.error("Fatal error: {}".format(win32gui.GetWindowText(lstwid[2])))
                else:
                    ctx.logger.error("Unknown error; Wintexts: {}".format('; '.join([win32gui.GetWindowText(th) for th in lstwid]) ))
                
                hndl.kill()
                exitCode = ExitCodes.RBUILDER_RUN_FATAL
                break
        #endregion

        time.sleep(0.01)

    if log and not log.closed: 
        for line in read_and_get_info_from_rpt(log,True): 
                ctx.logger.info(line)

    if hndl.returncode:
        cext = conv_cmp_exitCode(hndl.returncode)
        ctx.logger.error("RBuilder exited with unknown exit code {}".format(cext))
        exitCode = ExitCodes.RBUILDER_RUN_APPLICATION_PRELOAD_ERROR

    return exitCode


def get_hwnds_for_pid(pid):
    # faster use win32gui.FindWindow(None, "Modal Window Title")
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds

def get_opened_rpt_log(pid):
    for f in psutil.Process(pid).open_files():
        if f.path.endswith(".rpt"):
            return f.path
    return None

def open_rpt_log(pid):
    rpath = get_opened_rpt_log(pid)
    if rpath is None: return None
    return open(rpath,'r')

def read_and_get_info_from_rpt(fhandle,doclose=False):
    if fhandle is None: return []
    lret = []
    startReading = False
    for line in fhandle.readlines():
        #skip warnings
        fpart = line[9:]
        if fpart.startswith("\"[RB] Start initialize engine\""): #fpart.startswith("Starting mission:"):
            startReading = True
        if fpart.startswith("Warning Message: "):
            continue
        if startReading:
            lret.append(line[:-1])
    if doclose:
        fhandle.close()
    return lret


def process_hinig_windows(hl):
    if win32gui.GetWindowText(hl).startswith("Arma 3"):
        win32gui.ShowWindow(hl,win32con.SW_HIDE)
        return True
    if win32gui.GetWindowText(hl).startswith("KK"):
        # get console stdout and redirect to my stdout
        import win32api
        import win32console
        import sys
        return False
    return False

def conv_cmp_exitCode(uintCode):
    return cast(pointer(c_uint32(uintCode)),POINTER(c_int32)).contents.value


def process_defines(ctx:AppContext,macroDict,macroCfg,outlist):
    import dep_tools
    itmsNeeds = {} # value: list, need any of them
    itmsEnaOn = {} # for depobject validation. autoadding dependencies
    for k,v in macroCfg.items():
        if k not in itmsNeeds:
            itmsNeeds[k] = []
        if v and v.get('needs'):
            varr = v['needs'].split(',') if v['needs'] else []
            itmsNeeds[k].extend(varr)
        
        if k not in itmsEnaOn: itmsEnaOn[k] = []
        if v and v.get('enable_on'):
            varr = v['enable_on'].split(',') if v['enable_on'] else []
            itmsEnaOn[k].extend(varr)
    
    enaOnDep = dep_tools.Dependencies(itmsEnaOn)
    enaOnDepDict = enaOnDep.complete_dependencies_dict()

    for depK,depV in enaOnDepDict.items():
        for req in depV:
            if req in macroDict:
                macroDict[depK] = macroDict.get(depK,macroCfg.get(depK,{}).get('value',''))
        pass
    hasFoundErr = False
    for mdef,mval in macroDict.items():
        needsList = itmsNeeds.get(mdef)
        if needsList:
            found = False
            needs_list = []
            for nd in needsList:
                if nd.startswith("!"):
                    needs_list.append("NOT " + nd[1:])
                    if nd[1:] not in macroDict:
                        found = True
                        break
                else:
                    needs_list.append(nd)
                    if nd in macroDict:
                        found = True
                        break
            if not found:
                ctx.logger.warning(f"Macro {mdef} require: {",".join(needs_list)}")
                hasFoundErr = True
                continue
        outlist.append(createPreprocessorDefineCLI(mdef,mval))
    return hasFoundErr

def createPreprocessorDefineCLI(name,arg=''):
    return f"-preprocDefine={name}{'='+arg if arg else ''}"

if __name__ == "__main__":
    import logging
    import cfg
    import argparse
    logging.basicConfig(level=logging.INFO,format='[%(name)s] %(levelname)s - %(message)s')
    ctx = AppContext()
    ctx.setContextVar("cfg",cfg.loadCfg())
    ctx.logger = logging.getLogger("test_defines")
    ctx.logger.setLevel(logging.INFO)
    ctx.logger.info("DEBUG START")
    ctx.args = argparse.Namespace()

    deflist = ctx.cfg['defines']
    deflist = {
        "RELEASE":None,
        "DEBUG":None,
        
        "TEST_1":{
            "enable_on":"TEST_ALL",
            "needs": "!TEST_2"
        },

        "TEST_ALL":{
            "enable_on":"DEBUG"
        },

        "TEST_2":{
            "needs":"RELEASE,DEBUG",
            #"enable_on":"TEST_ALL",
            "value":"123"
        },
        "TEST_COMMON":{
            "enable_on":"RELEASE,TEST_ALL"
        },

        "base": None,
        "node_ena":{
            "enable_on": "base,testbase"
        },
        "node_child": {
            "enable_on": "node_ena"
        },
        "testbase": {
            "needs": "node_ena"
        },

    }
    out = []
    i1 = {
        "DEBUG":'',"TEST_2":""
    }
    i2 = {'base':''}
    i3 = {'testbase':''}

    process_defines(ctx,i1.copy(),deflist,out)
    ctx.logger.info("Test 1: {} => {}".format(i1,out))

    out = []
    process_defines(ctx,i2.copy(),deflist,out)
    ctx.logger.info("Test 2: {} => {}".format(i2,out))

    out = []
    process_defines(ctx,i3.copy(),deflist,out)
    ctx.logger.info("Test 3: {} => {}".format(i3,out))
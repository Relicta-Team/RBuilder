from AppCtx import AppContext
from Constants import *
from os.path import abspath as getAbsPath
from os.path import exists as fileExists
import os
import subprocess
import time
import win32gui
import win32process
import win32con
import psutil

def RBuilderRun(ctx:AppContext):
    ctx.setCurrentLogger("RB")

    ctx.logger.info("Starting...")

    vmDir = ctx.cfg['pathes']['vm_dir']
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

    ctx.logger.info("Preparing macros")
    macroList = []

    for md in ctx.args.macroDefines:
        macname = md[0]
        val = md[1] if len(md) > 1 else ""
        #ctx.logger.info(f"Added macro {macname}{' with value '+val if val else ''}")
        macroList.append(f"-preprocDefine={md[0]}{'='+val if val else ''}")

    ctx.logger.info("Added {} define flags".format(len(macroList)))

    cliArgs = f'{argsRun} {prof} {' '.join(macroList)}'
    cliArgsList = cliArgs.split(' ') + [prof] + macroList

    ctx.logger.info(f"Compiler: {getAbsPath(vmDir+"\\"+runner)}")
    ctx.logger.info(f"CLI: {cliArgs}")

    rtCfg = ctx.cfg['runtime']
    preloadTimeout = rtCfg['preload_timeout']/1000 #ms to sec

    preloadTimeout = 10
    import sys
    stinf = subprocess.STARTUPINFO()
    stinf.hStdOutput = sys.stdout.fileno()
    stinf.hStdError = sys.stderr.fileno()
    stinf.wShowWindow = subprocess.SW_HIDE
    stinf.dwFlags = subprocess.STARTF_USESHOWWINDOW | subprocess.STARTF_USESTDHANDLES

    hndl = subprocess.Popen([runnerPath]+cliArgsList,
        creationflags=subprocess.CREATE_NO_WINDOW,
        umask=0o000,
        startupinfo=stinf)
    proc = psutil.Process(hndl.pid)
    log = open_rpt_log(hndl.pid)
    startTime = time.time()
    if log == None:
        ctx.logger.error("Can't open log file")
    

    # def __callbackEnumwindow(hwnd, param):
    #     if win32gui.IsWindowVisible(hwnd):
    #         print(win32gui.GetWindowText(hwnd))
    # win32gui.EnumChildWindows(hndl.pid, __callbackEnumwindow, 0)

    #logfilePath = psutil.Process(hndl.pid).open_files()[0]
    #hwnds = get_hwnds_for_pid(hndl.pid)

    
    exitCode = ExitCodes.SUCCESS
    preloaded = False
    while hndl.poll() is None:
        if log==None:
            log = open_rpt_log(hndl.pid)
        
        if not preloaded:
            if time.time() - startTime > preloadTimeout:
                
                for line in read_and_get_info_from_rpt(log): 
                    ctx.logger.info(line)
                    log.close()

                ctx.logger.error("Preloader timeout")
                hndl.kill()
                exitCode = ExitCodes.RBUILDER_RUN_LOADING_TIMEOUT
                break
            preloaded = False

        hwnds = get_hwnds_for_pid(hndl.pid)
        for hwnd in hwnds:
            if win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & win32con.WS_EX_DLGMODALFRAME:
                
                for line in read_and_get_info_from_rpt(log): 
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
        time.sleep(0.01)
        
    if log and not log.closed: 
        for line in read_and_get_info_from_rpt(log): 
                ctx.logger.info(line)
        log.close()

    if hndl.returncode:
        ctx.logger.error("RBuilder exited with unknown exit code {}".format(hndl.returncode))
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

def read_and_get_info_from_rpt(fhandle):
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
    return lret
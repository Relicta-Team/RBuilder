from AppCtx import AppContext
import logging
from Constants import *
from os.path import exists as fileExists
from os.path import abspath as getAbsPath
from shutil import copytree as dirCopy
from shutil import rmtree as dirRemove
from shutil import copyfile as fileCopy
from shutil import copy
from pathlib import *
import os
from glob import glob

def createPackage(ctx:AppContext,destPath=None):

    src = ctx.args.src
    if destPath is None:
        vmDir = ctx.cfg['pathes']['vm_dir']
        dest = vmDir + f"\\{RBUILDER_SOURCE_FOLDERNAME}"
    else:
        dest = destPath
    incfiles:str = ctx.cfg['build']['include']
    excfiles:str = ctx.cfg['build']['exclude']

    ctx.logger.info("Start builder...")
    ctx.logger.info(f"\tSource path: {getAbsPath(src)}")
    ctx.logger.info(f"\tDest path: {getAbsPath(dest)}")
    ctx.logger.info(f"\tInclude pathes: {incfiles}")
    ctx.logger.info(f"\tExclude pathes: {excfiles}")

    excFileList = excfiles.split(';')
    #by default add client in excluded files
    excFileList.append("Src\\client")

    if fileExists(dest):
        ctx.logger.info(f"Removing previous sources: {getAbsPath(dest)}")
        dirRemove(dest)
    
    def __ignoreFunc(src, names):
        rf = []
        for name in names:
            for ex in excFileList:
#                if os.path.join(src,name) == os.path
                if Path(src,name).match(ex):
                    ctx.logger.debug(f"Excluded: {os.path.join(src,name)} (because found '{ex}')")
                    rf.append(name)
        return rf

    ctx.logger.info("Copying files...")
    dirCopy(src,dest,ignore=__ignoreFunc)

    ctx.logger.info("Including files...")
    for f in incfiles.split(';'):
        ctx.logger.info(f"Including: {f}")
        f = "client\\" + f
        origPath = src + "\\" + f
        destPath = dest + "\\"
        for ff in glob(origPath):
            relpath = os.path.relpath(ff,src)
            ctx.logger.info(f"\t copy: {relpath}")
            os.makedirs(os.path.dirname(destPath+relpath),exist_ok=True)
            fileCopy(ff,destPath + relpath)

def isVMBuildMounted(ctx:AppContext):
    vmDir = ctx.cfg['pathes']['vm_dir']
    return fileExists(os.path.join(vmDir,RBUILDER_SOURCE_FOLDERNAME))

def buildProcess(ctx:AppContext):
    ctx.setCurrentLogger("BUILD")
    vmDir = ctx.cfg['pathes']['vm_dir']
    dest = vmDir + f"\\{RBUILDER_SOURCE_FOLDERNAME}"
    src = ctx.args.src
    #remove prevbuild
    if fileExists(dest):
        if os.path.islink(dest):
            ctx.logger.info(f"Removing previous simlink source: {getAbsPath(dest)}")
            os.unlink(dest)
        elif os.path.isdir(dest):
            ctx.logger.info(f"Removing previous source folder: {getAbsPath(dest)}")
            dirRemove(dest)
        else:
            ctx.logger.error(f"Can't remove previous unknown source type: {getAbsPath(dest)}")
            return False

    
    if ctx.args.symlink:
        srcAbs = getAbsPath(src)
        destAbs = getAbsPath(dest)
        ctx.logger.info(f"Symlink src: {getAbsPath(src)}")
        ctx.logger.info(f"Creating symlink: {getAbsPath(dest)}")
        os.symlink(srcAbs,destAbs,True)
    else:
        ctx.logger.info(f"Generaing package: {getAbsPath(src)}")
        createPackage(ctx)

    ctx.logger.info("Build done!")
    ctx.setCurrentLogger()
    return True


def clearCache(ctx:AppContext):
    ctx.setCurrentLogger("CACHE_CLEAR")
    vmDir = ctx.cfg['pathes']['vm_dir']
    listDirs = ["config","appcache","profile","logs"]

    for d in listDirs:
        ctx.logger.info(f"Clearing: {d}")
        path = vmDir + f"\\{d}"
        if fileExists(path):
            ctx.logger.info(f"Removing: {getAbsPath(path)}")
            dirRemove(path)
    
    ctx.setCurrentLogger()
    return True
    
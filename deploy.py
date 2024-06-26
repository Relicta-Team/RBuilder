import os
from Constants import *
import urllib.request
from AppCtx import AppContext
import requests
from packlib.a3lib import *
from os.path import exists as fileExists
from os.path import abspath as getAbsPath
from shutil import copytree as dirCopy
from shutil import rmtree as dirRemove

RBUILDER_DOWNLOAD_PATH = "https://relicta.ru/HostVM/cmp_2.16.exe"


RBUILDER_LOADER_PATH = "loader"
RBUILDER_PRELOADER_PATH = "preload"

def pack(ctx:AppContext,fromDir,toFile):
    try:
        fromDir = os.path.abspath(fromDir)
        toFile = os.path.abspath(toFile)

        ctx.logger.info("Packing...")
        ctx.logger.info(f"Src: {fromDir}")
        ctx.logger.info(f"Dest: {toFile}")
        if not os.path.exists(fromDir):
            raise FileNotFoundError(f"Folder {fromDir} not found")
        if os.path.exists(toFile):
            os.remove(toFile)
        
        pbo(create_pbo=True,pbo_path=toFile,files=[fromDir],custom_saver=True)
        
        ctx.logger.info("Created binary content: {}".format(toFile))
        
        return True
    except Exception as e:
        ctx.logger.error(f"Error initializing compiler: ({e.__class__.__name__}) {e}")
        return False

def deployMain(ctx:AppContext):
    ctx.setCurrentLogger("INIT")
    
    vmDir = ctx.cfg['pathes']['vm_dir']
    if not downloadCompiler(ctx): return False

    pathLoader = RBUILDER_LOADER_PATH
    destLoader = vmDir + "\\mpmissions\\" + RBUILDER_LOADER_FILENAME
    ctx.logger.info("Creating loader binary content")

    if not pack(ctx,pathLoader,destLoader): return False

    ctx.logger.info("Creating preloader")
    pathPreloaderSrc = RBUILDER_PRELOADER_PATH
    pathPreloaderDest = vmDir + f"\\{RBUILDER_PRELOADER_FOLDERNAME}"
    if fileExists(pathPreloaderDest):
        ctx.logger.info(f"Removing previous preloader folder: {getAbsPath(pathPreloaderDest)}")
        dirRemove(pathPreloaderDest)
    
    ctx.logger.info(f"Preloader src: {getAbsPath(pathPreloaderSrc)}")
    ctx.logger.info(f"Preloader dest: {getAbsPath(pathPreloaderDest)}")
    dirCopy(pathPreloaderSrc,pathPreloaderDest)
    ctx.logger.info(f"Preloader created: {getAbsPath(pathPreloaderDest)}")

    generateRbuilderHeader(ctx)
    

    return True

def generateRbuilderHeader(ctx:AppContext):
    ctx.logger.info("Generating RBuilder header")
    preloadDest = ctx.cfg['pathes']['vm_dir'] + f"\\{RBUILDER_PRELOADER_FOLDERNAME}"
    defList = ["//Autogenerated RBuilder header","#define RBUILDER"]
    
    def _createConditionalDefine(k,v=None):
        rv = f"#ifdef CMD__{k}\n\t#define {k}"
        if v is not None and v.get('value') is not None:
            rv += f" {v.get('value')}"
        rv += "\n#endif"
        return rv
    
    preloaderHeader = preloadDest + f"\\{RBUILDER_PRELOADER_HEADER_FILENAME}"

    ctx.logger.info(f"Preloader header: {getAbsPath(preloaderHeader)}")
    
    for k,v in ctx.cfg['defines'].items():
        defList.append(_createConditionalDefine(k,v))

    defStr = "\n".join(defList)
    with open(preloaderHeader,'w') as f:
        f.write(defStr)

    ctx.logger.info("RBuilder header generated")

    return True

def downloadCompiler(ctx:AppContext):
    try:
        ctx.logger.info("Initialize compiler")
        
        rbuilder_path = ctx.cfg['pathes']['vm_dir'] + "\\" + RBUILDER_NAME

        rbuilder_path = os.path.abspath(rbuilder_path)

        if os.path.exists(rbuilder_path):
            ctx.logger.info(f"Removing {rbuilder_path}")
            os.remove(rbuilder_path)

        ctx.logger.info(f"Downloading {RBUILDER_DOWNLOAD_PATH}")
        
        with open(rbuilder_path, 'wb') as f:
            respone = requests.get(RBUILDER_DOWNLOAD_PATH, stream=True)
            total = respone.headers.get("Content-Length")
            if total is None:
                raise Exception("No content length header")
            else:
                dl = 0
                total = int(total)
                for data in respone.iter_content(chunk_size=4096 * 1000):
                    dl += len(data)
                    f.write(data)
                    done = int(100 * dl / total)
                    ctx.logger.info('Downloading {}%'.format(done))
                    #ctx.logger.info("\r[{}{}]".format('█' * done, '.' * (50 - done)))
        
        ctx.logger.info("Compiler downloaded")

        return True
    except Exception as e:
        ctx.logger.error(f"Error initializing compiler: ({e.__class__.__name__}) {e}")
        return False
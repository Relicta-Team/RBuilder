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

def createPackage(ctx:AppContext):

    src = ctx.args.src
    vmDir = ctx.cfg['pathes']['vm_dir']
    dest = vmDir + f"\\{RBUILDER_SOURCE_FOLDERNAME}"
    incfiles:str = ctx.cfg['build']['include']
    excfiles:str = ctx.cfg['build']['exclude']

    ctx.logger.info("Start builder...")
    ctx.logger.info(f"\tSource path: {getAbsPath(src)}")
    ctx.logger.info(f"\tDest path: {getAbsPath(dest)}")
    ctx.logger.info(f"\tInclude pathes: {incfiles}")
    ctx.logger.info(f"\tExclude pathes: {excfiles}")

    excFileList = excfiles.split(';')
    #by default add client in excluded files
    excFileList.append("client")

    if fileExists(dest):
        ctx.logger.info(f"Removing previous sources: {getAbsPath(dest)}")
        dirRemove(dest)
    
    def __ignoreFunc(src, names):
        rf = []
        for name in names:
            for ex in excFileList:
#                if os.path.join(src,name) == os.path
                if Path(src,name).match(ex):
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

def buildProcess(ctx:AppContext):
    ctx.setCurrentLogger("BUILD")
    
    createPackage(ctx)

    br = createModelConfigTemplate(ctx)
    if not br: return False

    ctx.logger.info("Build done!")
    ctx.setCurrentLogger()
    return True

def createModelConfigTemplate(ctx:AppContext):
    src = ctx.args.src
    m2cpath = os.path.join(src,"M2C.sqf")
    
    ctx.logger.info(f"Starting scan model configs")
    
    if not fileExists(m2cpath):
        ctx.logger.error("M2C.sqf not found")
        return False
    cfgList = []
    tempModel = "core\default\default.p3d"
    savePath = ctx.cfg['pathes']['vm_dir'] + f"\\{RBUILDER_PRELOADER_PATH}\\CfgVehicles.hpp"
    #region Possible cfgvehicles types
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/access
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/All
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Logic
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/AllVehicles
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Land
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/LandVehicle
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Car
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Motorcycle
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Bicycle
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Tank
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/APC
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Man
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Animal
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Air
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Helicopter
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Plane
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Ship
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/SmallShip
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/BigShip
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Truck
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/ParachuteBase
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/LaserTarget
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/NVTarget
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/ArtilleryTarget
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/ArtilleryTargetW
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/ArtilleryTargetE
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/SuppressTarget
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/PaperCar
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/FireSectorTarget
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Static
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Rope
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Fortress
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Building
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/NonStrategic
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/HeliH
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/AirportBase
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Strategic
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/FlagCarrierCore
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Land_VASICore
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/Thing
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/ThingEffect
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/ThingEffectLight
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/ThingEffectFeather
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/FxExploArmor1
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/FxExploArmor2
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/FxExploArmor3
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/FxExploArmor4
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/FxCartridge
# RBuilder(cprint): cfg:bin\config.bin/CfgVehicles/WindAnomaly
    #endregion

    cfgTemplate = "class CLASSNAME : PBASE_CLASS {};"
    unicalSet = set()
    with open(m2cpath,"r") as f:
        for line in f.readlines():
            if line.startswith("['"):
                cfgList.append(line[2:line.find('\',\'')])

    ctx.logger.info("Finded {} configs".format(len(cfgList)))
    if len(cfgList) > 0:
        ctx.logger.info("Creating model config template")
        try:
            with open(savePath,"w+") as fhd:
                fhd.write("class CfgVehicles {class Static; class PBASE_CLASS : Static { scope = 2; };\n")
                for lc in cfgList:
                    if lc in unicalSet:
                        ctx.logger.error("Duplicate config: " + lc)
                    unicalSet.add(lc)
                    fhd.write(cfgTemplate.replace("CLASSNAME",lc))
                fhd.write("};")
        except Exception as ex:
            ctx.logger.error(f"Ex for save: {ex.__class__.__name__}: {ex}")
            return False
        ctx.logger.info("Model config template created")


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
    
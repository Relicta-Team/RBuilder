import psutil
from AppCtx import AppContext
import os
from deployCode.util import *

PLATFORM_CACHE_FILENAME = ".\\platform_path.cache"

def deployProcess(ctx:AppContext):
	ctx.setCurrentLogger("Deploy")
	
	if ctx.args.editor:
		ctx.logger.info("Start deploying editor")
		pdir = ctx.args.editor
		if fileExists(PLATFORM_CACHE_FILENAME):
			ctx.logger.info(f"Loading platform dir from cache: {os.path.abspath(PLATFORM_CACHE_FILENAME)}")
			with open(PLATFORM_CACHE_FILENAME, "r") as f:
				pdir = f.read()
			
		if pdir == ".":
			ctx.logger.error("Platform dir not set")
			print("\n"*2)
			pdir = input("Type path to platform dir and press enter: ")
		else:
			ctx.logger.info(f"Platform dir: {pdir}")

		if not os.path.exists(pdir):
			ctx.logger.error(f"Platform dir not found: {pdir}")
			return -1

		if not os.path.isdir(pdir):
			ctx.logger.error(f"Platform dir is not a directory: {pdir}")
			return -2

		pExe = f'{pdir}\\arma3_x64.exe'

		if not os.path.exists(pExe):
			ctx.logger.error(f"Platform executable not found: {pExe}")
			return -3
		
		if not fileExists(PLATFORM_CACHE_FILENAME):
			ctx.logger.info(f"Saving platform dir in cache: {os.path.abspath(PLATFORM_CACHE_FILENAME)}")
			with open(PLATFORM_CACHE_FILENAME, "w") as f:
				f.write(pdir)

		# find if process arma3_x64.exe is running
		ctx.logger.debug("Check if process is running")
		for p in psutil.process_iter():
			if p.name() == "arma3_x64.exe" and p.cmdline()[0].lower() == pExe.lower():
				ctx.logger.info("Process arma3_x64.exe is running. Close process and try again")
				return -4
		deployDir = ctx.cfg['pathes']['deploy_dir']

		if not os.path.exists(deployDir):
			ctx.logger.error(f"Deploy dir not found: {deployDir}")
			return -5

		pathFrom = os.path.join(deployDir,"editor")
		pathTo = os.path.join(pdir,"@EditorContent")
		
		ctx.logger.debug(f"Source path: {pathFrom}")
		if not os.path.exists(pathFrom):
			ctx.logger.error(f"Source path not found: {pathFrom}")
			return -6
		
		ctx.logger.debug(f"Dest path: {pathTo}")
		
		if os.path.exists(pathTo):
			dirRemove(pathTo)
		dirCopy(pathFrom,pathTo)

		ctx.logger.info("Installing mission file")
		sdkDir = ctx.cfg['pathes']['resdk_dir']
		missionFrom = os.path.join(deployDir,"editor_bootload.sqm")
		missionTo = os.path.join(sdkDir,"mission.sqm")
		ctx.logger.debug(f"Mission from: {missionFrom}")
		ctx.logger.debug(f"Mission to: {missionTo}")
		if not os.path.exists(missionFrom):
			ctx.logger.error(f"Mission file not found: {missionFrom}")
			return -7
		if os.path.exists(missionTo):
			yes = {'yes','y', 'ye'}
			no = {'no','n',''}
			ctx.logger.info("Mission file already exists. Overwrite? [y/n] (Enter to skip)")
			choice = input().lower()
			if choice in yes:
				fileRemove(missionTo)
			elif choice in no:
				ctx.logger.info("Skipping deletion of previous mission file")
		fileCopy(missionFrom,missionTo)

		return 0

	return -1
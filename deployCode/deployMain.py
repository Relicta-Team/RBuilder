import copy
import time
import psutil
from AppCtx import AppContext
import os
from Builder.package import createPackage, isVMBuildMounted,buildProcess
from Constants import ExitCodes
from Runner import RBuilderRun
from deploy import isCompilerInitialized,deployMain, pack
from deployCode.util import *

PLATFORM_CACHE_FILENAME = ".\\platform_path.cache"

class CompileMetainfo:
	def __init__(self,version,revision,storageDir,binDir):
		self.version = version
		self.revision = revision
		self.versionFull = f"{version}+{revision}"
		# here placed version of server
		self.storageRoot = storageDir #root is A3Master folder
		#versions folder
		self.versionsStorage = ""
		# game folder
		self.masterStorage = ""
		self.binaryDir = binDir
		self.cryptEnabled = False

	def resolveServerStorage(self,ctx):
		if self.storageRoot == ".":
			ctx.logger.error(f"Server storage not found: \"{self.storageRoot}\"")
			return False
		ctx.logger.debug("Autodetect server storage directories")
		rootAbs = getAbsPath(self.storageRoot)
		if self.versionsStorage == "":
			self.versionsStorage = pathJoin(rootAbs,"Versions")

			if not dirExists(self.versionsStorage):
				ctx.logger.error(f"Versions folder not found: \"{self.versionsStorage}\"")
				return False
			curFile = pathJoin(self.versionsStorage,f"current")
			if not fileExists(curFile):
				ctx.logger.error(f"Metafile not found: \"{curFile}\"")
				return False
		if self.masterStorage == "":
			self.masterStorage = pathJoin(rootAbs,"A3Master")

			if not dirExists(self.masterStorage):
				ctx.logger.error(f"Master folder not found: \"{self.masterStorage}\"")
				return False
			executable = pathJoin(self.masterStorage,"arma3server_x64.exe")
			if not fileExists(executable):
				ctx.logger.error(f"Executable not found: \"{executable}\"")
				return False
		return True
	
	def packServer(self,ctx,srcPbo):
		vfoldName = self.versionFull
		verStorFold = pathJoin(self.versionsStorage,vfoldName)
		
		verToPath = pathJoin(verStorFold,"src.pbo")
		if fileExists(verToPath):
			ctx.logger.info(f"Updating server version: \"{vfoldName}\"")
			fileRemove(verToPath)
		else:
			ctx.logger.info(f"Creating new server version: \"{vfoldName}\"")
		fileCopy(srcPbo,verToPath)
		if not fileExists(verToPath):
			ctx.logger.error(f"Failed to copy server build: \"{verToPath}\"")
			return False
		return True

	def packClient(self,ctx,srcPbo):
		vfoldName = self.versionFull
		verStorFold = pathJoin(self.versionsStorage,vfoldName)
		verToPath = pathJoin(verStorFold,"relicta.vr.pbo")
		if fileExists(verToPath):
			ctx.logger.info(f"Updating client version: \"{vfoldName}\"")
			fileRemove(verToPath)
		else:
			ctx.logger.info(f"Creating new client version: \"{vfoldName}\"")
		fileCopy(srcPbo,verToPath)
		if not fileExists(verToPath):
			ctx.logger.error(f"Failed to copy client build: \"{verToPath}\"")
			return False
		return True
	
	def postCompile(self,ctx):
		currentFolder = pathJoin(self.versionsStorage,self.versionFull)
		fileClient = pathJoin(currentFolder,"relicta.vr.pbo")
		fileServer = pathJoin(currentFolder,"src.pbo")
		unstableMark = pathJoin(self.versionsStorage,"UNSTABLE")
		inver_unstableMark = pathJoin(currentFolder,"UNSTABLE")

		if not fileExists(unstableMark):
			ctx.logger.info(f"Metafile not found: \"{unstableMark}\"")
			return False

		preparedVersion = True
		if not fileExists(fileClient):
			preparedVersion = False
			ctx.logger.warning(f"Client build not found: \"{fileClient}\"")
		if not fileExists(fileServer):
			preparedVersion = False
			ctx.logger.warning(f"Server build not found: \"{fileServer}\"")
		
		if ctx.args.unstable:
			ctx.logger.info("Unstable flag enabled")
			fileCopy(unstableMark,pathJoin(currentFolder,"UNSTABLE"))
		else:
			ctx.logger.info("Unstable flag disabled")
			if fileExists(inver_unstableMark):
				ctx.logger.debug(f"Removing unstable metafile: {inver_unstableMark}")
				fileRemove(inver_unstableMark)

		#check current version
		curFile = pathJoin(self.versionsStorage,f"current")
		with open(curFile,"r") as f:
			curVersion = f.read().splitlines()[0]
		ctx.logger.info(f"Compare versions (from storage '{curVersion}', build '{self.versionFull}')")
		if curVersion == self.versionFull:
			if not preparedVersion:
				ctx.logger.error("Cannot deploy prepared version (is not full build)")
				return False
			fileServerTo = pathJoin(self.masterStorage,"@server","Addons","src.pbo")
			fileClientTo = pathJoin(self.masterStorage,"mpmissions","relicta.vr.pbo")

			ctx.logger.debug(f"Copy server build: \"{fileServer}\" -> \"{fileServerTo}\"")
			fileCopy(fileServer,fileServerTo)

			ctx.logger.debug(f"Copy client build: \"{fileClient}\" -> \"{fileClientTo}\"")
			fileCopy(fileClient,fileClientTo)

			# ctx.logger.debug("Update current version metafile")
			# with open(curFile,"w") as f:
			# 	f.write(self.versionFull)

			ctx.logger.info("Version synchronized")
		else:
			ctx.logger.info("Version synchronization is not required")
		
		return True

def deployProcess(ctx:AppContext):
	ctx.setCurrentLogger("Deploy")
	#ctx.logger.info(ctx.args)
	if ctx.args.editor:
		return deployEditor(ctx)
	
	if ctx.args.client or ctx.args.server:
		return deployCodebase(ctx)
	return -1

def getSDKDir(ctx):
	return ctx.args.ReSDK_dir

def getSourceDir(ctx):
	return pathJoin(getSDKDir(ctx),"Src")

def preinitDeploy(ctx:AppContext):
	ctx.setCurrentLogger("PreInitDeploy")

	# if isCompilerInitialized(ctx):
	# 	ctx.logger.debug("Skipping compiler initialization")
	# else:
	# 	ctx.logger.info("Initializing compiler")
	# 	if not deployMain(ctx): 
	# 		ctx.logger.error("Failed to initialize compiler")
	# 		return -201

	# if isVMBuildMounted(ctx):
	# 	ctx.logger.debug("Skipping preinit check")
	# else:
	# 	oldargs = ctx.args
	# 	copyargs = copy(oldargs)
	# 	#!not tested
	# 	c = buildProcess(ctx)
	# 	ctx.args = oldargs
	# 	if not c: 
	# 		ctx.logger.error("Failed to mount build")
	# 		return -202

	if not isCompilerInitialized(ctx):
		ctx.logger.error("Compiler not initialized. Use -init flag")
		return -201
	if not isVMBuildMounted(ctx):
		ctx.logger.error("Build not compiled. Use -build flag")
		return -202

	ctx.logger.debug("Preinit check passed")
	ctx.setCurrentLogger()
	return 0

def deployCodebase(ctx:AppContext):
	timestart = time.time()
	
	pstat = preinitDeploy(ctx)
	if pstat: return pstat

	ctx.setCurrentLogger("DeployCode")
	#prepare versionfile
	verFile = os.path.join(getSourceDir(ctx),"VERSION")
	ctx.logger.debug(f"Prepare version file: {getAbsPath(verFile)}")
	if not fileExists(verFile):
		ctx.logger.error(f"Version file not found: {verFile}")
		return -1
	revFile = os.path.join(getSourceDir(ctx),"REVISION")
	ctx.logger.debug(f"Revision file: {getAbsPath(revFile)}")
	if fileExists(revFile):
		with open(revFile,"r") as f:
			revision = f.read().splitlines()[0]
		if len(revision) >= 7 and not revision.lower().startswith("unrevisioned"):
			revision = revision[:7]
	else:
		ctx.logger.warning(f"Revision file not found: {revFile}")
		revision = "unrevisioned"

	ctx.logger.debug("Scanning version")
	with open(verFile,"r") as f:
		version = f.read().splitlines()[0]
	if not re.match(r"^\d+\.\d+\.\d+$",version):
		ctx.logger.error(f"Invalid version: {version}")
		return -3

	compObj = CompileMetainfo(version,revision,ctx.args.storage,ctx.args.bin)

	if not compObj.resolveServerStorage(ctx):
		ctx.logger.error("Failed to resolve server storage")
		return -4

	ctx.logger.debug("Checking private header")
	privDir = os.path.join(getSourceDir(ctx),"private.h")
	if fileExists(privDir):
		with open(privDir,"r",encoding="utf-8") as f:
			data = f.read()
			m = re.match(r"#define\s+RBUILDER_PRIVATE_COMPILE_CRYPT\s+(.+)",data)
			if m:
				compObj.cryptEnabled = os.environ["RBUILDER_PRIVATE_COMPILE_CRYPT"] == m.group(1)
	
	ctx.logger.info(f"Compile with crypt: {compObj.cryptEnabled}")

	if ctx.args.client:
		c = deployClient(ctx,compObj)
		if c: return c
	if ctx.args.server:
		c = deployServer(ctx,compObj)
		if c: return c

	ctx.logger.info("Post compile actions")
	if not compObj.postCompile(ctx):
		ctx.logger.error("Failed to perform post compile actions")
		return -5

	ctx.logger.info(f"	Version: {compObj.version}")
	ctx.logger.info(f"	Revision: {compObj.revision}")
	ctx.logger.info(f"Deploy done at {(time.time() - timestart):.2f} seconds")

	return 0

def deployClient(ctx:AppContext,compObj:CompileMetainfo):
	ctx.setCurrentLogger("DeployClient")
	ctx.logger.info("Start deploying client")
	buildType = ctx.args.client
	ctx.logger.info(f"Build type: {buildType}")
	buildTypeMacro = buildType.upper()

	tempFolder = os.path.join(compObj.binaryDir,"client")
	tempClientBinary = os.path.join(tempFolder,"client_mission.pbo")
	tempClientMissionFolder = os.path.join(tempFolder,"mission")

	srcDeployDir = os.path.join(ctx.cfg['pathes']['deploy_dir'],"client")

	if fileExists(tempClientBinary):
		ctx.logger.info(f"Removing previous client binary: {tempClientBinary}")
		fileRemove(tempClientBinary)
	if dirExists(tempClientMissionFolder):
		ctx.logger.info(f"Removing previous client mission folder: {tempClientMissionFolder}")
		dirRemove(tempClientMissionFolder)
	
	ctx.logger.info("Copy m2c lib")
	m2cPath = os.path.join(getSourceDir(ctx),"M2C.sqf")
	if not fileExists(m2cPath):
		ctx.logger.error(f"M2C.sqf not found: {m2cPath}")
		return -101
	
	fileCopy(m2cPath,os.path.join(tempClientMissionFolder,"src","M2C.sqf"))

	ctx.logger.info("Copy ui config")
	uiConfigPath = os.path.join(getSDKDir(ctx),"Resources","ui_schemas")
	if not dirExists(uiConfigPath):
		ctx.logger.error(f"UI config not found: {uiConfigPath}")
		return -102
	
	dirCopy(uiConfigPath,os.path.join(tempClientMissionFolder,"ui"))

	for file in os.listdir(srcDeployDir):
		ctx.logger.info(f"Copy file: {file}")
		fileCopy(os.path.join(srcDeployDir,file),os.path.join(tempClientMissionFolder,file))
	
	if not fileExists(tempClientMissionFolder):
		ctx.logger.error(f"Client mission folder not found: {tempClientMissionFolder}")

	ctx.logger.info("Compiling...")
	#clientBinaryOutput = getAbsPath(pathJoin(tempClientMissionFolder,"CLIENT"))
	ns = ctx.parser.parse_args(['-sdk',ctx.args.ReSDK_dir,'run','-d',buildTypeMacro,'-d','BUILD_CLIENT'])
	ctx.logger.debug(f"Args: {ns}")
	oldargs = ctx.args
	ctx.args = ns
	exitCode = RBuilderRun(ctx)
	ctx.args = oldargs
	ctx.setCurrentLogger("DeployClient") #restore logger category
	if isinstance(exitCode,ExitCodes):
		exitCode = exitCode.value
	if exitCode:
		ctx.logger.error(f"Client build failed; Code: {exitCode}")
		return exitCode
	
	ctx.logger.debug("Crpypting clinent binary")
	if compObj.cryptEnabled and compObj.revision.lower() != "unrevisioned":
		ctx.logger.error("Crypting not implemented")
		return -103
	else:
		ctx.logger.debug("Skip crypting")
	
	ctx.logger.info("Packing client")

	if fileExists(tempClientBinary):
		ctx.logger.info(f"Removing previous client binary: {tempClientBinary}")
		fileRemove(tempClientBinary)

	if not pack(ctx,tempClientMissionFolder,tempClientBinary):
		ctx.logger.error("Failed to pack client")
		return -104
	
	if not compObj.packClient(ctx,tempClientBinary):
		ctx.logger.error("Failed to deploy client")
		return -105

	return 0

def deployServer(ctx:AppContext,compObj:CompileMetainfo):
	ctx.setCurrentLogger("DeployServer")
	ctx.logger.info("Start deploying server")
	
	serverTemp = os.path.join(compObj.binaryDir,"server","sources")
	serverTempPBO = os.path.join(serverTemp,"src.pbo")
	if fileExists(serverTemp):
		ctx.logger.debug(f"Removing previous server folder: {serverTemp}")
		dirRemove(serverTemp)

	if fileExists(serverTempPBO):
		ctx.logger.debug(f"Removing previous server pbo: {serverTempPBO}")
		fileRemove(serverTempPBO)
	
	createPackage(ctx,serverTemp)
	if not dirExists(serverTemp):
		ctx.logger.error(f"Server folder not found: {serverTemp}")
		return -105
	
	if not pack(ctx,serverTemp,serverTempPBO):
		ctx.logger.error("Failed to pack server")
		return -106

	if not compObj.packServer(ctx,serverTempPBO):
		ctx.logger.error("Failed to deploy server")
		return -107

	return 0

def deployEditor(ctx:AppContext):
	ctx.setCurrentLogger("DeployEditor")
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
	sdkDir = ctx.args.ReSDK_dir #ctx.cfg['pathes']['resdk_dir']
	missionFrom = os.path.join(deployDir,"editor_bootload.sqm")
	missionTo = os.path.join(sdkDir,"mission.sqm")
	ctx.logger.debug(f"Mission from: {missionFrom}")
	ctx.logger.debug(f"Mission to: {missionTo}")
	if not os.path.exists(missionFrom):
		ctx.logger.error(f"Mission file not found: {missionFrom}")
		return -7
	if os.path.exists(missionTo):
		yes = {'yes','y', 'ye'}
		#no = {'no','n',''}
		ctx.logger.info("Mission file already exists. Overwrite? [y/n] (Enter to skip)")
		choice = input().lower()
		if choice in yes:
			fileRemove(missionTo)
			fileCopy(missionFrom,missionTo)
		else:
			ctx.logger.info("Skipping deletion of previous mission file")
	else:
		fileCopy(missionFrom,missionTo)

	return 0
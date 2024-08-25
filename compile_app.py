import sys
import os
import re
import shutil

reqPipLibs = False
reqTxt = ".\\req_build.txt"

try:
	import iniparser2
	import requests
except:
	reqPipLibs = True

if reqPipLibs:
	print("Missing pip modules. Installing from req_build.txt")
	installRes = os.system("pip install -r {}".format(reqTxt)) 
	print("PIP install result: " + str(installRes))
	if installRes != 0:
		print("PIP install error")
		sys.exit(-10)

curAppDir = os.path.dirname(sys.argv[0])

shaNum = os.environ['SHA_FULL']
if shaNum is None:
	print("Missing SHA_FULL environment variable")
	sys.exit(-11)

shaNum = shaNum[0:7]
print("SHA: " + shaNum)

iconPath = os.path.join(curAppDir,"icon.ico")
if not os.path.exists(iconPath):
	print("Missing icon.ico")
	sys.exit(-12)

iconPath = os.path.abspath(iconPath)
print("Icon path: " + iconPath)

# loading app_version
appver_list = []
appver_tuple = (1,0,0,0)
appverDir = os.path.join(curAppDir,"APP_VERSION.py")
with open(appverDir,mode='r',encoding='utf-8') as f:
	appver_list = [int(x) for x in re.findall(r"\d+",f.readlines()[0])]
	appver_list.append(shaNum)
	appver_tuple = [appver_list[0],appver_list[1],appver_list[2],0]
	appver_tuple = str(tuple(appver_tuple))

vinf = os.path.join(curAppDir,"vinf.txt")
if not os.path.exists(vinf):
	print("Missing vinf.txt")
	sys.exit(-13)

vinfData = ""
with open(vinf,mode='r',encoding='utf-8') as f:
	vinfData = f.read().replace("VER_STR",'.'.join([str(x) for x in appver_list])).replace("VER_TUPLE",appver_tuple)

vinf_gen = os.path.join(curAppDir,"vinf_gen.txt")
if os.path.exists(vinf_gen): os.remove(vinf_gen)
with open(vinf_gen,mode='w',encoding='utf-8') as f:
	f.write(vinfData)


data = f"pyinstaller --noconfirm --onefile --windowed --icon \"{iconPath}\" --name \"RBuilder\" --paths \"./Builder;./packlib;./yaml\" \".\\app.py\" --version-file \"{vinf_gen}\""
print("PYINSTALLER CLI: " + data)
return_ = os.system(data)
print("Compiler result " + str(return_))
if return_ != 0:
	print("Compiler error")
	sys.exit(-14)

rbPath = curAppDir+"/rb.exe"
if os.path.exists(rbPath):
	os.remove(rbPath)

shutil.copyfile(os.path.join(curAppDir,'dist/RBuilder.exe'),rbPath)
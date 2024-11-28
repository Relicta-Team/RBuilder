from glob import glob
import shutil
import os
import re
from os.path import exists as fileExists
from os.path import exists as dirExists
from os.path import abspath as getAbsPath
from os.path import dirname as getDirFromFile
from os.path import basename as getFilenameFromPath
from os.path import join as pathJoin
from shutil import copytree as dirCopy
from shutil import rmtree as dirRemove
from os import remove as fileRemove

def copyGlob(srcDir,pattern,destDir):
	"""Копирование директории/файлов по glob-паттерну"""
	for ff in glob(pathJoin(srcDir,pattern)):
		relpath = os.path.relpath(ff,srcDir)
		fileCopy(ff,pathJoin(destDir,relpath))

def fileCopy(src,dest):
	"""Копирование файла"""
	os.makedirs(getDirFromFile(dest),exist_ok=True)
	shutil.copyfile(src,dest)

def dirMove(source,destination):
	"""Перемещение директории"""
	files = os.listdir(source) 
	for file in files: 
		file_name = os.path.join(source, file) 
		shutil.move(file_name, destination)
	dirRemove(source)

def getPatternFromFile(path,pattern):
	"""Получить содержимое файла по regex-паттерну"""
	lst:list[str] = []
	with open(path,'r') as f:
		lst = re.findall(pattern,f.read())
	return lst
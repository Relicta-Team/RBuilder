from os.path import *
import iniparser2
import logging
#os.path.dirname(os.path.realpath(__file__))

CFG_MAP = {
	"main": {
		"version": 1,
		"src": "",
	}
}

class Config:
	
	parser : iniparser2.INI
	cfgPath : str = "config.ini"
	logger = logging.getLogger("main")
	isLoaded : bool = False

	@staticmethod
	def initConfigObject():
		Config.parser = iniparser2.INI()

	@staticmethod
	def init():
		Config.logger.info("Initialize config reader")
		Config.initConfigObject()
		
		#check if config file exists
		if exists(Config.cfgPath):
			Config.readConfig()
		else:
			Config.createConfig()
		ver = Config.parser.get_int("version","main")
		Config.logger.info(f"Loaded config version: {ver}")
		
		if (ver != CFG_MAP["main"]["version"]):
			Config.logger.info(f"Version not actual; Old: {ver}; New: {CFG_MAP['main']['version']}")
			Config.updateConfig()
		
		if Config.parser.get_str("sdkdir",'main') == "do_locate_dir":
			Config.logger.info("Detect sdk source directory...")
			Config.parser.set('sdkdir',Config.getFileManager().allocateSDKSourceDir(),'main')

		Config.logger.info(f"Config initialized (version {ver})")
		Config.isLoaded = True
	
	@staticmethod
	def readConfig():
		Config.logger.info("Reading config")
		Config.parser.read_file(Config.cfgPath)

	@staticmethod
	def updateConfig():

		# проход по секциям конфигов в файле. несуществующие удаляем
		allSections = CFG_MAP.keys()
		for sectionName in Config.parser.sections():
			if sectionName not in allSections:
				Config.parser.remove_section(sectionName)
				Config.logger.debug(f"Removed old section {sectionName}")

		# проход по секциям конфигов в конфиге. несуществующие добавляем
		for sectionName,sectionItems in CFG_MAP.items():

			if not Config.parser.has_section(sectionName):
				Config.parser.set_section(sectionName)
				Config.logger.debug(f"Added new section {sectionName}")
				#register values
				# Register values in the existing section
				for key, value in sectionItems.items():
					Config.parser.set(key, value, section=sectionName)
					Config.logger.debug(f"Registered value {key} in section {sectionName}")
			else:
				Config.logger.debug(f"Validating section {sectionName} values")
				for key, value in sectionItems.items():
					existsProp = Config.parser.has_property(key, sectionName)
					equalVals = existsProp and value == Config.parser.get(key, sectionName)
					if not existsProp or not equalVals:
						Config.parser.set(key, value, section=sectionName)
						Config.logger.debug(f"Property updated [{sectionName}]{key} -> (exists: {existsProp}, equals: {equalVals})")

		Config.logger.info("Config updated")


	
	@staticmethod
	def createConfig():
		Config.logger.info("Creating new config")
		parser = Config.parser
		#clear config
		for sect in Config.parser.sections().copy():
			parser.remove_section(sect)

		# insert config values from configValues
		for key in CFG_MAP:
			parser.set_section(key)
			for kint in CFG_MAP[key]:
				parser.set(kint,CFG_MAP[key][kint],section=key)
		#print(parser)
	@staticmethod
	def saveConfig():
		if not Config.isLoaded: return
		Config.parser.write(Config.cfgPath)
		Config.logger.info("Config saved")
	
	@staticmethod
	def get(key,section="main"):
		return Config.parser.get(key,section)
	
	@staticmethod
	def set(key,value,section="main"):
		if isinstance(value,str) and value=="":
			#raise ValueError(f"[{section}]{key}: Value can't be empty string")
			Config.logger.error(f"[{section}]{key}: Value can't be empty string")
		Config.parser.set(key,value,section)
	
	@staticmethod
	def get_int(key,section="main"):
		return Config.parser.get_int(key,section)
	
	@staticmethod
	def get_float(key,section="main"):
		return Config.parser.get_float(key,section)

	@staticmethod
	def get_str(key,section="main"):
		return Config.parser.get_str(key,section)

	@staticmethod
	def get_bool(key,section="main"):
		return Config.parser.get_bool(key,section)
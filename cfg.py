import os
import yaml
import sys
baseFolder = os.path.dirname(sys.argv[0])
CFG_FILEPATH = os.path.join(baseFolder,"config.yml")

def initCfg():
    pass

def loadCfg():
    if not os.path.exists(CFG_FILEPATH):
        return None
    with open(CFG_FILEPATH) as f:
        obj = yaml.safe_load(f)    
    return obj
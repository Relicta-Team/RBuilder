import os
import yaml
CFG_FILEPATH = "config.yml"

def initCfg():
    pass

def loadCfg():
    if not os.path.exists(CFG_FILEPATH):
        return None
    with open(CFG_FILEPATH) as f:
        obj = yaml.safe_load(f)    
    return obj
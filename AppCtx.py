from typing import Literal, TypeAlias
import logging
import argparse

ContextVarName: TypeAlias = Literal["cfg","logger","args","verbose"]

class AppContext:
    cfg: dict = None
    logger: logging.Logger = None
    main_logger: logging.Logger = None
    args: argparse.Namespace = None
    verbose: bool = False
    fileHandler = None

    def setContextVar(self,vname: ContextVarName,vval):
        setattr(self,vname,vval)
        if vname=='args':
            if vval.logToFile:
                self.fileHandler = logging.FileHandler(vval.logToFile,mode='w')
        return vval

    def setCurrentLogger(self,loggername=""):
        if loggername=="":
            self.logger = self.main_logger
            if self.verbose: self.logger.setLevel(logging.DEBUG)
            return
        self.logger = logging.getLogger(loggername)
        if self.verbose: self.logger.setLevel(logging.DEBUG)
        if self.logger != self.main_logger:            
            if self.args.logToFile and len(self.logger.handlers) ==0:
                self.logger.addHandler(self.fileHandler)
    
from typing import Literal, TypeAlias
import logging
import argparse

ContextVarName: TypeAlias = Literal["cfg","logger","args"]

class AppContext:
    cfg: dict = None
    logger: logging.Logger = None
    main_logger: logging.Logger = None
    args: argparse.Namespace = None
    def setContextVar(self,vname: ContextVarName,vval):
        setattr(self,vname,vval)
        return vval

    def setCurrentLogger(self,loggername):
        self.logger = logging.getLogger(loggername)
    
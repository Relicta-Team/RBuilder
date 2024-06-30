

from enum import Enum

RBUILDER_NAME = "cmp.exe"
RBUILDER_LOADER_FILENAME = "loader.vr.pbo"
RBUILDER_PRELOADER_FOLDERNAME = "preload"

RBUILDER_PRELOADER_HEADER_FILENAME = "RBuilder.h"


class ExitCodes(Enum):
    SUCCESS = 0

    # fatal
    UNKNOWN_FATAL_ERROR = -1
    UNHANDLED_EXCEPTION = -2
    NO_ARGUMENTS_PROVIDED = 0#-3

    NOT_SUPPORTED = -3
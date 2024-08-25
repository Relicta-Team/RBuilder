

from enum import Enum

RBUILDER_NAME = "cmp.exe"
RBUILDER_LOADER_FILENAME = "loader.vr.pbo"
RBUILDER_PRELOADER_FOLDERNAME = "preload"

RBUILDER_PRELOADER_HEADER_FILENAME = "RBuilder.h"

RBUILDER_SOURCE_FOLDERNAME = "src"

RBUILDER_LOADER_PATH = "loader"
RBUILDER_MDL_LOADER_PATH = "mdl_loader"
RBUILDER_MDL_LOADER_DEST_PATH = "@server\\Addons\\mdl_loader.pbo"
RBUILDER_PRELOADER_PATH = "preload"

RBUILDER_DB_PATH_SRC = "DB\\GameMain.db"
RBUILDER_DB_PATH_DEST = "@server\\db\\GameMain.db"

class RBUILDER_PREDEFINED_MACROS(Enum):
    RBUILDER_PID = "Process id of current process",
    RBUILDER_OUTPUT = "Output to RBuilder",
    RBUILDER_DEFINE_LIST = "All CLI arguments passed from RBuilder to VM"
    RBUILDER_AUTO_RELOAD = "Autoreload rbuilder on executed vm commands"
    RBUILDER_IS_SYMLINK_SOURCES = "Source code running from simlink directory"
    RBUILDER_RESDK_PATH = "Path to ReSDK directory"


class ExitCodes(Enum):
    SUCCESS = 0

    # fatal
    UNKNOWN_FATAL_ERROR = -1
    UNHANDLED_EXCEPTION = -2
    NO_ARGUMENTS_PROVIDED = 0#-3
    USER_INTERRUPT = -4

    NOT_SUPPORTED = -3

    RBUILDER_RUN_FAILED = -105
    RBUILDER_RUN_LOADING_TIMEOUT = -106
    RBUILDER_RUN_FATAL = -107
    RBUILDER_RUN_APPLICATION_PRELOAD_ERROR = -108
    RBUILDER_RUN_FAILED_DEFINES_PREP = -109


from enum import Enum

class ExitCodes(Enum):
    SUCCESS = 0

    # fatal
    UNKNOWN_FATAL_ERROR = -1
    UNHANDLED_EXCEPTION = -2
    NO_ARGUMENTS_PROVIDED = 0#-3

    NOT_SUPPORTED = -3
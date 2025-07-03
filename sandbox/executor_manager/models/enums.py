from enum import Enum


class SupportLanguage(str, Enum):
    PYTHON = "python"
    NODEJS = "nodejs"


class ResultStatus(str, Enum):
    SUCCESS = "success"
    PROGRAM_ERROR = "program_error"
    RESOURCE_LIMIT_EXCEEDED = "resource_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RUNTIME_ERROR = "runtime_error"
    PROGRAM_RUNNER_ERROR = "program_runner_error"


class ResourceLimitType(str, Enum):
    TIME = "time"
    MEMORY = "memory"
    OUTPUT = "output"


class UnauthorizedAccessType(str, Enum):
    DISALLOWED_SYSCALL = "disallowed_syscall"
    FILE_ACCESS = "file_access"
    NETWORK_ACCESS = "network_access"


class RuntimeErrorType(str, Enum):
    SIGNALLED = "signalled"
    NONZERO_EXIT = "nonzero_exit"

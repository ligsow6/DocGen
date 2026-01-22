"""Error types and exit codes for DocGen."""


class ExitCode:
    SUCCESS = 0
    UNEXPECTED = 1
    CONFIG = 2
    IO = 3
    USAGE = 4


class DocGenError(Exception):
    exit_code = ExitCode.UNEXPECTED

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ConfigError(DocGenError):
    exit_code = ExitCode.CONFIG


class DocGenIOError(DocGenError):
    exit_code = ExitCode.IO


class UsageError(DocGenError):
    exit_code = ExitCode.USAGE


def exit_code_for_exception(exc: Exception) -> int:
    if isinstance(exc, DocGenError):
        return exc.exit_code
    return ExitCode.UNEXPECTED

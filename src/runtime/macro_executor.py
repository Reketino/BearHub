
import sys

from models.macro import Macro
from runtime.input.base import InputBackend


class MacroExecutor:
    """Executes macros using the platform-specific input backend."""

    def __init__(self):
        self._backend: InputBackend = self._create_backend()

    @staticmethod
    def _create_backend() -> InputBackend:
        if sys.platform.startswith("linux"):
            from runtime.input.linux_input import LinuxInputBackend

            return LinuxInputBackend()

        if sys.platform == "win32":
            from runtime.input.windows_input import WindowsInputBackend

            return WindowsInputBackend()

        raise RuntimeError(
            f"Unsupported operating system: {sys.platform}"
        )

    def execute(self, macro: Macro) -> None:
        print(
            f"Executing macro: "
            f"name={macro.name!r}, "
            f"value={macro.value!r}"
        )

        self._backend.write(macro.value)

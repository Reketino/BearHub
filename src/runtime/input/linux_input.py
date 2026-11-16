
import shutil
import subprocess


class LinuxInputBackend:
    """Handles keyboard input on Linux using xdotool."""

    def __init__(self):
        self._xdotool_path = shutil.which("xdotool")

        if self._xdotool_path is None:
            raise RuntimeError(
                "xdotool was not found. "
                "Install it with: sudo apt install xdotool"
            )

    def write(self, text: str) -> None:
        if not text:
            return

        try:
            subprocess.run(
                [
                    self._xdotool_path,
                    "type",
                    "--clearmodifiers",
                    "--delay",
                    "1",
                    "--",
                    text,
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            )

        except subprocess.TimeoutExpired as error:
            raise RuntimeError(
                "xdotool timed out while writing text."
            ) from error

        except subprocess.CalledProcessError as error:
            raise RuntimeError(
                f"xdotool failed: {error.stderr.strip()}"
            ) from error

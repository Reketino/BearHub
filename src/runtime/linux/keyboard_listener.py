
import threading
from collections.abc import Callable

from Xlib import X, XK, display
from Xlib.display import Display
from Xlib.xobject.drawable import Window
from Xlib.error import BadAccess


KEYSYM_ALIASES = {
    "Return": "Return",
    "space": "space",
    "Tab": "Tab",
    "Escape": "Escape",
    "BackSpace": "BackSpace",
    "Delete": "Delete",
    "Insert": "Insert",
    "Home": "Home",
    "End": "End",
    "Page_Up": "Page_Up",
    "Page_Down": "Page_Down",
    "Up": "Up",
    "Down": "Down",
    "Left": "Left",
    "Right": "Right",
    "minus": "minus",
    "equal": "equal",
    "bracketleft": "bracketleft",
    "bracketright": "bracketright",
    "backslash": "backslash",
    "semicolon": "semicolon",
    "apostrophe": "apostrophe",
    "comma": "comma",
    "period": "period",
    "slash": "slash",
    "grave": "grave",
}


class KeyboardListener:
    def __init__(
        self,
        on_key_pressed: Callable[[str], None],
        triggers: dict[str, bool],
    ):
        self._callback = on_key_pressed
        self._triggers = triggers

        self._display: Display | None = None
        self._root: Window | None = None
        self._thread: threading.Thread | None = None
        
        self._running = False
        self._stop_event = threading.Event()

        self._keycodes: dict[int, tuple[str, bool]] = {}

        self._lock = threading.RLock()

    def start(self) -> None:
        if self._running:
            return

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._run,
            name="BearHub-KeyboardListener",
            daemon=True,
        )

        self._running = True
        self._thread.start()


    def stop(self) -> None:
        if not self._running:
            return

        self._stop_event.set()

        if (
            self._thread is not None
            and self._thread.is_alive()
        ):
            self._thread.join(timeout=3)

        if self._thread is not None and self._thread.is_alive():
            raise TimeoutError(
                "Keyboard listener did not stop in time."
            )

        self._thread = None
        self._running = False

    def _run(self) -> None:
        try:
            self._display = display.Display()
            self._root = self._display.screen().root

            self._register_triggers()

            print(
                f"Keyboard listener started. "
                f"Registered {len(self._keycodes)} keys."
            )

            while not self._stop_event.is_set():
                if self._display.pending_events():
                    event = self._display.next_event()
                    self._handle_event(event)
                else:
                    self._stop_event.wait(0.01)

        except Exception as error:
            if not self._stop_event.is_set():
                print(f"Keyboard listener error: {error}")

        finally:
            self._ungrab_all()

            if self._display is not None:
                try:
                    self._display.close()
                except Exception:
                    pass

            self._display = None
            self._root = None
            self._running = False

            print("Keyboard listener stopped.")

    def _register_triggers(self) -> None:
        if self._display is None or self._root is None:
            raise RuntimeError(
            "X11 display is not initialized."
        )

        
        for trigger_value, suppress in self._triggers.items():
            keysym_name = KEYSYM_ALIASES.get(
                trigger_value,
                trigger_value,
            )

            keysym = XK.string_to_keysym(keysym_name)

            if not keysym:
                print(
                    f"Unsupported keyboard trigger: "
                    f"{trigger_value}"
                )
                continue

            keycode = self._display.keysym_to_keycode(keysym)

            if not keycode:
                print(
                    f"Could not resolve keycode for "
                    f"{trigger_value}"
                )
                continue

            try:
                self._root.grab_key(
                    keycode,
                    0,
                    False,
                    X.GrabModeAsync,
                    X.GrabModeSync,
                )

                self._keycodes[keycode] = (
                    trigger_value,
                    suppress,
                )

            except BadAccess:
                print(
                    f"Could not grab {trigger_value}. "
                    "Another application may own this key."
                )

        self._display.sync()

    def _handle_event(self, event) -> None:
        if event.type != X.KeyPress:
            return

        trigger = self._keycodes.get(event.detail)

        if trigger is None:
            self._allow_keyboard(X.AsyncKeyboard)
            return

        trigger_value, suppress = trigger

        if suppress:
            # Consume the original key press.
            self._allow_keyboard(X.AsyncKeyboard)
        else:
            # Replay the original key press to other applications.
            self._allow_keyboard(X.ReplayKeyboard)

        self._callback(trigger_value)


    def _allow_keyboard(self, mode: int) -> None:
        if self._display is None:
            raise RuntimeError(
                "X11 display is not initialized."
            )

        self._display.allow_events(
            mode,
            X.CurrentTime,
        )
        self._display.flush()

    def _ungrab_all(self) -> None:
        if self._display is None or self._root is None:
            return

        try:
            self._root.ungrab_key(
                X.AnyKey,
                X.AnyModifier,
            )
            self._display.sync()
        except Exception:
            pass

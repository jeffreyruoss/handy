"""
Hotkey Listener Module
Handles global keyboard shortcut detection.
"""

from pynput import keyboard, mouse


class HotkeyListener:
    """Listens for keyboard shortcut presses globally."""

    def __init__(self, menu_ui):
        """
        Initialize the hotkey listener.

        Args:
            menu_ui: MenuUI instance to show when hotkey is pressed
        """
        self.menu_ui = menu_ui
        self.listener = None
        self.current_keys = set()
        self.mouse_controller = mouse.Controller()

    def on_press(self, key):
        """
        Callback for key press events.

        Args:
            key: Key that was pressed
        """
        self.current_keys.add(key)

        # Check for Cmd+Shift+Space
        if (keyboard.Key.cmd in self.current_keys and
            keyboard.Key.shift in self.current_keys and
            keyboard.Key.space in self.current_keys):

            # Get current mouse position
            x, y = self.mouse_controller.position

            print(f"Hotkey pressed at ({x}, {y})")
            self.menu_ui.show_menu(x, y)

    def on_release(self, key):
        """
        Callback for key release events.

        Args:
            key: Key that was released
        """
        try:
            self.current_keys.remove(key)
        except KeyError:
            pass

    def start(self):
        """Start listening for keyboard events."""
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()
        print("Listening for Cmd+Shift+Space hotkey...")

    def join(self):
        """Wait for the listener thread to finish."""
        if self.listener:
            self.listener.join()

    def stop(self):
        """Stop listening for keyboard events."""
        if self.listener:
            self.listener.stop()

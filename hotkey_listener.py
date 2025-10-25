"""
Hotkey Listener Module
Handles global mouse button detection.
"""

from pynput import mouse


class HotkeyListener:
    """Listens for mouse wheel button presses globally."""

    def __init__(self, menu_ui):
        """
        Initialize the hotkey listener.

        Args:
            menu_ui: MenuUI instance to show when hotkey is pressed
        """
        self.menu_ui = menu_ui
        self.listener = None

    def on_click(self, x, y, button, pressed):
        """
        Callback for mouse click events.

        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate
            button: Mouse button that was clicked
            pressed: True if pressed, False if released
        """
        # Check for middle button (mouse wheel) press
        if button == mouse.Button.middle and pressed:
            # Toggle menu: close if open, show if closed
            if self.menu_ui.is_menu_visible():
                print("Mouse wheel clicked - closing menu")
                self.menu_ui.close_menu()
            else:
                print(f"Mouse wheel clicked at ({x}, {y})")
                self.menu_ui.show_menu(x, y)

    def start(self):
        """Start listening for mouse events."""
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        print("Listening for mouse wheel button press...")

    def join(self):
        """Wait for the listener thread to finish."""
        if self.listener:
            self.listener.join()

    def stop(self):
        """Stop listening for mouse events."""
        if self.listener:
            self.listener.stop()

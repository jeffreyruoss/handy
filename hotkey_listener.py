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
        self.captured_clipboard = None  # Temporary storage for captured clipboard
        self.middle_button_held = False  # Track if middle button is being held

    def capture_selection_immediately(self):
        """
        Capture the current selection to temporary storage.
        This is needed for browsers that deselect text on middle-click.
        We use CGEvent for fastest possible execution.
        """
        import time
        import Cocoa
        import Quartz

        try:
            # Save current clipboard content
            pasteboard = Cocoa.NSPasteboard.generalPasteboard()
            old_clipboard = pasteboard.stringForType_(Cocoa.NSPasteboardTypeString)

            # Send Cmd+C using CGEvent (much faster than AppleScript)
            # Create a Cmd+C key event
            source = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateHIDSystemState)

            # Key code for 'C' is 8
            key_down = Quartz.CGEventCreateKeyboardEvent(source, 8, True)
            key_up = Quartz.CGEventCreateKeyboardEvent(source, 8, False)

            # Set Command flag
            Quartz.CGEventSetFlags(key_down, Quartz.kCGEventFlagMaskCommand)
            Quartz.CGEventSetFlags(key_up, Quartz.kCGEventFlagMaskCommand)

            # Post the events
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, key_down)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, key_up)

            # Wait for clipboard to update
            time.sleep(0.1)

            # Read the newly captured text
            self.captured_clipboard = pasteboard.stringForType_(Cocoa.NSPasteboardTypeString)

            # Restore the old clipboard content
            if old_clipboard:
                pasteboard.clearContents()
                pasteboard.setString_forType_(old_clipboard, Cocoa.NSPasteboardTypeString)
                print(f"Captured selection to temporary storage (restored original clipboard)")
            else:
                print(f"Captured selection to temporary storage")

        except Exception as e:
            print(f"Error capturing selection: {e}")
            self.captured_clipboard = None

    def on_click(self, x, y, button, pressed):
        """
        Callback for mouse click events.

        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate
            button: Mouse button that was clicked
            pressed: True if pressed, False if released
        """
        # Check for middle button (mouse wheel)
        if button == mouse.Button.middle:
            if pressed:
                # Middle button pressed
                self.middle_button_held = True
                # Toggle menu: close if open, show if closed
                if self.menu_ui.is_menu_visible():
                    print("Mouse wheel clicked - closing menu")
                    self.menu_ui.close_menu()
                else:
                    print(f"Mouse wheel clicked at ({x}, {y})")
                    # Capture selection BEFORE showing menu (helps with browsers that deselect on middle-click)
                    self.capture_selection_immediately()
                    # Pass captured clipboard to menu UI
                    self.menu_ui.set_captured_text(self.captured_clipboard)
                    self.menu_ui.show_menu(x, y)
            else:
                # Middle button released
                if self.middle_button_held and self.menu_ui.is_menu_visible():
                    print(f"Mouse wheel released at ({x}, {y}) - triggering menu item")
                    self.menu_ui.trigger_item_at_cursor()
                self.middle_button_held = False

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

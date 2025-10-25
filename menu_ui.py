"""
Menu UI Module
Handles the popup pie menu display and interaction.
"""

import objc
import Cocoa
from actions import Actions
from pie_menu_view import PieMenuView


class MenuUI(Cocoa.NSObject):
    """Creates and displays a circular pie menu at cursor position."""

    def init(self):
        """Initialize the menu UI."""
        self = objc.super(MenuUI, self).init()
        if self is None:
            return None

        self.actions = Actions.alloc().init()
        self.menu_window = None
        return self

    def showMenuAtLocation_(self, location_dict):
        """
        Display the pie menu at the specified coordinates.
        This method is called on the main thread.

        Args:
            location_dict: Dictionary with 'x' and 'y' keys for coordinates
        """
        x = location_dict['x']
        y = location_dict['y']

        # Close any existing menu window first
        if self.menu_window and self.menu_window.isVisible():
            self.menu_window.orderOut_(None)
        self.menu_window = None

        # Remember the currently active app so we can return focus to it
        workspace = Cocoa.NSWorkspace.sharedWorkspace()
        active_app = workspace.frontmostApplication()
        if active_app:
            self.actions.setPreviousApp_(active_app)

        # Define menu items
        menu_items = [
            {'title': 'Copy', 'action': 'performCopy:', 'target': self.actions},
            {'title': 'Paste', 'action': 'performPaste:', 'target': self.actions},
            {'title': 'Select All', 'action': 'performSelectAll:', 'target': self.actions},
            {'title': 'Select All & Copy', 'action': 'performSelectAllCopy:', 'target': self.actions},
            {'title': 'Pastebot', 'action': 'performPastebot:', 'target': self.actions},
            {'title': 'Paste Plain', 'action': 'performPastePlain:', 'target': self.actions},
            {'title': 'Dictation', 'action': 'performDictation:', 'target': self.actions},
            {'title': 'Restart', 'action': 'performRestart:', 'target': self.actions},
        ]

        # Create window size (radius * 2 + padding)
        menu_size = 260

        # Get screen height for coordinate conversion
        # macOS screen coords: origin at bottom-left, y increases upward
        # Window positioning: origin at top-left of screen, y increases downward
        main_screen = Cocoa.NSScreen.mainScreen()
        screen_frame = main_screen.frame()
        screen_height = screen_frame.size.height

        # Convert from screen coordinates (bottom-left origin) to window position (top-left origin)
        # Center the menu on the cursor position
        window_x = x - menu_size / 2
        window_y = screen_height - y - menu_size / 2

        window_rect = Cocoa.NSMakeRect(
            window_x,
            window_y,
            menu_size,
            menu_size
        )

        # Create a borderless, transparent window
        style_mask = Cocoa.NSWindowStyleMaskBorderless
        self.menu_window = Cocoa.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            window_rect,
            style_mask,
            Cocoa.NSBackingStoreBuffered,
            False
        )

        # Configure window
        self.menu_window.setOpaque_(False)
        self.menu_window.setBackgroundColor_(Cocoa.NSColor.clearColor())
        self.menu_window.setLevel_(Cocoa.NSFloatingWindowLevel)
        self.menu_window.setHasShadow_(True)
        self.menu_window.setIgnoresMouseEvents_(False)

        # Create pie menu view
        pie_view = PieMenuView.alloc().initWithFrame_(
            Cocoa.NSMakeRect(0, 0, menu_size, menu_size)
        )
        pie_view.setMenuItems_(menu_items)

        # Set view as window content
        self.menu_window.setContentView_(pie_view)

        # Show the window
        self.menu_window.makeKeyAndOrderFront_(None)

        # Make app active to show window
        app = Cocoa.NSApplication.sharedApplication()
        app.activateIgnoringOtherApps_(True)

    def show_menu(self, x, y):
        """
        Show the menu at the specified coordinates.
        This can be called from any thread; it will execute on the main thread.

        Args:
            x: X coordinate for menu position
            y: Y coordinate for menu position
        """
        # Schedule the menu to appear on the main thread
        location_dict = {'x': x, 'y': y}
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "showMenuAtLocation:",
            location_dict,
            False
        )

    def close_menu(self):
        """
        Close the menu if it's currently visible.
        This can be called from any thread; it will execute on the main thread.
        """
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "closeMenuOnMainThread:",
            None,
            False
        )

    def closeMenuOnMainThread_(self, _):
        """
        Close the menu window on the main thread.
        """
        if self.menu_window and self.menu_window.isVisible():
            self.menu_window.orderOut_(None)
            self.menu_window = None

    def is_menu_visible(self):
        """
        Check if the menu is currently visible.

        Returns:
            True if menu is visible, False otherwise
        """
        return self.menu_window is not None and self.menu_window.isVisible()

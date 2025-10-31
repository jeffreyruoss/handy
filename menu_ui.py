"""
Menu UI Module
Handles the popup pie menu display and interaction.
"""

import objc
import Cocoa
from actions import Actions
from pie_menu_view import PieMenuView
from icon_helper import icon_path


class MenuUI(Cocoa.NSObject):
    """Creates and displays a circular pie menu at cursor position."""

    def init(self):
        """Initialize the menu UI."""
        self = objc.super(MenuUI, self).init()
        if self is None:
            return None

        self.actions = Actions.alloc().init()
        self.menu_window = None
        self.captured_text = None
        return self

    def set_captured_text(self, text):
        """Store captured text for later use by Copy action."""
        self.captured_text = text
        self.actions.set_captured_text(text)

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

        # Define menu items for pie menu (frequently used)
        # Icons are loaded from the icons/ directory
        # Add PNG files to icons/ and they'll be automatically found
        # Pie starts at top and goes clockwise
        menu_items = [
            {'title': 'Dictation', 'action': 'performDictation:', 'target': self.actions, 'icon': icon_path('dictation.png')},
            {'title': 'Paste Plain', 'action': 'performPastePlain:', 'target': self.actions, 'icon': icon_path('paste-plain.png')},
            {'title': 'Pastebot', 'action': 'performPastebot:', 'target': self.actions, 'icon': icon_path('pastebot.png')},
            {'title': 'Paste', 'action': 'performPaste:', 'target': self.actions, 'icon': icon_path('paste.png')},
            {'title': 'Copy', 'action': 'performCopy:', 'target': self.actions, 'icon': icon_path('copy.png')},
            {'title': 'Notion', 'action': 'activateApp:', 'target': self.actions, 'app_path': '/Applications/Notion.app', 'icon': icon_path('notion.png')},
            {'title': 'VS Code', 'action': 'activateApp:', 'target': self.actions, 'app_path': '/Applications/Visual Studio Code - Insiders.app', 'icon': icon_path('vscode.png')},
            {'title': 'Dia', 'action': 'activateApp:', 'target': self.actions, 'app_path': '/Applications/Dia.app', 'icon': icon_path('dia.png')},
        ]

        # Define secondary menu items (less frequently used)
        secondary_items = [
            {'title': 'Select All', 'action': 'performSelectAll:', 'target': self.actions, 'icon': icon_path('select-all.png')},
            {'title': 'Select All & Copy', 'action': 'performSelectAllCopy:', 'target': self.actions, 'icon': icon_path('select-all-copy.png')},
            {'title': 'PixelSnap', 'action': 'performPixelSnap:', 'target': self.actions, 'icon': icon_path('pixelsnap.png')},
            {'title': 'ColorSlurp', 'action': 'performColorSlurp:', 'target': self.actions, 'icon': icon_path('colorslurp.png')},
            {'title': 'Screenshot', 'action': 'performScreenCapture:', 'target': self.actions, 'icon': icon_path('screenshot.png')},
            {'title': 'Restart Handy', 'action': 'performRestart:', 'target': self.actions, 'icon': icon_path('restart.png')},
        ]

        # Create window size (radius * 2 + padding)
        menu_size = 420  # Increased from 340 to accommodate larger pie menu
        secondary_menu_height = 150  # Height for 2 rows of 3 columns (85px per row + spacing)

        # Get screen height for coordinate conversion
        # macOS screen coords: origin at bottom-left, y increases upward
        # Window positioning: origin at top-left of screen, y increases downward
        main_screen = Cocoa.NSScreen.mainScreen()
        screen_frame = main_screen.frame()
        screen_height = screen_frame.size.height

        # Convert from screen coordinates (bottom-left origin) to window position (top-left origin)
        # Center the menu on the cursor position
        total_height = menu_size + secondary_menu_height + 10
        window_x = x - menu_size / 2
        window_y = screen_height - y - menu_size / 2

        window_rect = Cocoa.NSMakeRect(
            window_x,
            window_y - secondary_menu_height - 10,  # Shift up to account for secondary menu
            menu_size,
            total_height
        )        # Create a borderless, transparent window
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

        # Create container view that holds both pie menu and secondary menu
        from secondary_menu_view import SecondaryMenuView

        total_height = menu_size + secondary_menu_height + 10  # 10px gap
        container_view = Cocoa.NSView.alloc().initWithFrame_(
            Cocoa.NSMakeRect(0, 0, menu_size, total_height)
        )

        # Position pie menu at the top of container
        pie_view.setFrameOrigin_(Cocoa.NSMakePoint(0, secondary_menu_height + 10))
        container_view.addSubview_(pie_view)

        # Create and position secondary menu at the bottom
        secondary_view = SecondaryMenuView.alloc().initWithFrame_(
            Cocoa.NSMakeRect(0, 0, menu_size, secondary_menu_height)
        )
        secondary_view.setMenuItems_(secondary_items)
        container_view.addSubview_(secondary_view)

        # Set container as window content
        self.menu_window.setContentView_(container_view)

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

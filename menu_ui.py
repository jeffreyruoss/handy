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

        # Define left menu items (app shortcuts)
        left_menu_items = [
            {'title': 'Notion', 'action': 'activateApp:', 'target': self.actions, 'app_path': '/Applications/Notion.app', 'icon': icon_path('notion.png')},
            {'title': 'Dia', 'action': 'activateApp:', 'target': self.actions, 'app_path': '/Applications/Dia.app', 'icon': icon_path('dia.png')},
            {'title': 'VS Code', 'action': 'activateApp:', 'target': self.actions, 'app_path': '/Applications/Visual Studio Code - Insiders.app', 'icon': icon_path('vscode.png')},
            {'title': 'Alfred', 'action': 'performAlfred:', 'target': self.actions, 'icon': icon_path('alfred.png')},
            {'title': 'Pastebot', 'action': 'performPastebot:', 'target': self.actions, 'icon': icon_path('pastebot.png')},
        ]

        # Define menu items for pie menu (frequently used)
        # Icons are loaded from the icons/ directory
        # Add PNG files to icons/ and they'll be automatically found
        # Pie starts at top and goes clockwise
        menu_items = [
            {'title': 'Paste Plain', 'action': 'performPastePlain:', 'target': self.actions, 'icon': icon_path('paste-plain.png')},
            {'title': 'Paste', 'action': 'performPaste:', 'target': self.actions, 'icon': icon_path('paste.png')},
            {'title': 'Copy', 'action': 'performCopy:', 'target': self.actions, 'icon': icon_path('copy.png')},
            {'title': 'Save', 'action': 'performSave:', 'target': self.actions, 'icon': icon_path('save.png')},
            {'title': 'Find', 'action': 'performFind:', 'target': self.actions, 'icon': icon_path('find.png')},
            {'title': 'Dictation', 'action': 'performDictation:', 'target': self.actions, 'icon': icon_path('dictation.png')},
            {'title': 'Undo', 'action': 'performUndo:', 'target': self.actions, 'icon': icon_path('undo.png')},
            {'title': 'Escape', 'action': 'performEscape:', 'target': self.actions, 'icon': icon_path('escape.png')},
            {'title': 'Tab', 'action': 'performTab:', 'target': self.actions, 'icon': icon_path('tab.png')},
            {'title': 'Switch Window', 'action': 'performSwitchWindow:', 'target': self.actions, 'icon': icon_path('switch-window.png')},
        ]

        # Define secondary menu items (less frequently used)
        secondary_items = [
            {'title': 'PixelSnap', 'action': 'performPixelSnap:', 'target': self.actions, 'icon': icon_path('pixelsnap.png')},
            {'title': 'ColorSlurp', 'action': 'performColorSlurp:', 'target': self.actions, 'icon': icon_path('colorslurp.png')},
            {'title': 'Screenshot', 'action': 'performScreenCapture:', 'target': self.actions, 'icon': icon_path('screenshot.png')},
            {'title': 'Select All', 'action': 'performSelectAll:', 'target': self.actions, 'icon': icon_path('select-all.png')},
            {'title': 'Select All & Copy', 'action': 'performSelectAllCopy:', 'target': self.actions, 'icon': icon_path('select-all-copy.png')},
            {'title': 'Deselect', 'action': 'performDeselect:', 'target': self.actions, 'icon': icon_path('deselect.png')},
            {'title': 'Restart Handy', 'action': 'performRestart:', 'target': self.actions, 'icon': icon_path('restart.png')},
        ]

        # === SECONDARY MENU PARAMETERS (must match secondary_menu_view.py) ===
        button_spacing = 8
        vertical_button_padding = 6
        icon_text_spacing = 4
        icon_size = 30
        text_height = 12
        max_columns = 3
        # ======================================================================

        # Calculate secondary menu height dynamically
        num_secondary_items = len(secondary_items)
        num_columns = min(num_secondary_items, max_columns)
        num_rows = (num_secondary_items + num_columns - 1) // num_columns
        button_height = (vertical_button_padding * 2) + icon_size + icon_text_spacing + text_height
        secondary_menu_height = (num_rows * button_height) + ((num_rows + 1) * button_spacing)

        # Create window size
        menu_size = 420  # Pie menu size
        left_menu_width = 60  # Width for left menu
        gap = 10  # Gap between menus

        # Get screen height for coordinate conversion
        # macOS screen coords: origin at bottom-left, y increases upward
        # Window positioning: origin at top-left of screen, y increases downward
        main_screen = Cocoa.NSScreen.mainScreen()
        screen_frame = main_screen.frame()
        screen_height = screen_frame.size.height

        # Convert from screen coordinates (bottom-left origin) to window position (top-left origin)
        # Center the menu on the cursor position
        total_height = menu_size + secondary_menu_height + gap
        total_width = left_menu_width + gap + menu_size
        window_x = x - (left_menu_width + gap + menu_size / 2)
        window_y = screen_height - y - menu_size / 2

        window_rect = Cocoa.NSMakeRect(
            window_x,
            window_y - secondary_menu_height - gap,  # Shift up to account for secondary menu
            total_width,
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
        self.menu_window.setAcceptsMouseMovedEvents_(True)

        # Create container view that holds all menus
        from secondary_menu_view import SecondaryMenuView
        from left_menu_view import LeftMenuView

        container_view = Cocoa.NSView.alloc().initWithFrame_(
            Cocoa.NSMakeRect(0, 0, total_width, total_height)
        )

        # Create pie menu view first (at the top)
        pie_view = PieMenuView.alloc().initWithFrame_(
            Cocoa.NSMakeRect(left_menu_width + gap, secondary_menu_height + gap, menu_size, menu_size)
        )
        pie_view.setMenuItems_(menu_items)
        container_view.addSubview_(pie_view)

        # Create and position left menu (vertical, same height as pie menu)
        left_view = LeftMenuView.alloc().initWithFrame_(
            Cocoa.NSMakeRect(0, secondary_menu_height + gap, left_menu_width, menu_size)
        )
        left_view.setMenuItems_(left_menu_items)
        container_view.addSubview_(left_view)

        # Create and position secondary menu at the bottom (below pie menu, offset by left menu width)
        # Y position is 0, which is at the bottom of the container
        secondary_view = SecondaryMenuView.alloc().initWithFrame_(
            Cocoa.NSMakeRect(left_menu_width + gap, 0, menu_size, secondary_menu_height)
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

    def update_hover_at_position(self, x, y):
        """
        Update hover state based on global mouse position.
        This can be called from any thread; it will execute on the main thread.

        Args:
            x: X coordinate in screen space
            y: Y coordinate in screen space
        """
        position_dict = {'x': x, 'y': y}
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "updateHoverAtPositionOnMainThread:",
            position_dict,
            False
        )

    def trigger_item_at_cursor(self):
        """
        Trigger the menu item currently under the cursor.
        This can be called from any thread; it will execute on the main thread.
        """
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "triggerItemAtCursorOnMainThread:",
            None,
            False
        )

    def updateHoverAtPositionOnMainThread_(self, position_dict):
        """
        Update hover state at the given screen position on the main thread.

        Args:
            position_dict: Dictionary with 'x' and 'y' keys for screen coordinates
        """
        if not self.menu_window or not self.menu_window.isVisible():
            return

        x = position_dict['x']
        y = position_dict['y']

        # Convert from screen coordinates (pynput uses top-left origin)
        # to Cocoa screen coordinates (bottom-left origin)
        main_screen = Cocoa.NSScreen.mainScreen()
        screen_frame = main_screen.frame()
        screen_height = screen_frame.size.height

        # Create NSPoint in Cocoa screen coordinates
        mouse_location = Cocoa.NSMakePoint(x, screen_height - y)

        # Convert to window coordinates
        window_point = self.menu_window.convertPointFromScreen_(mouse_location)

        # Get the content view
        content_view = self.menu_window.contentView()
        if not content_view:
            return

        # Hit test to find which view is under the cursor
        hit_view = content_view.hitTest_(window_point)

        if hit_view and hasattr(hit_view, 'updateHoveredIndex_'):
            # Convert point to hit view's coordinate system
            point_in_view = hit_view.convertPoint_fromView_(window_point, None)
            # Update the hover state
            hit_view.updateHoveredIndex_(point_in_view)

    def triggerItemAtCursorOnMainThread_(self, _):
        """
        Trigger the menu item at the current cursor position on the main thread.
        """
        if not self.menu_window or not self.menu_window.isVisible():
            return

        # Get current mouse location in screen coordinates
        mouse_location = Cocoa.NSEvent.mouseLocation()

        # Convert to window coordinates
        window_point = self.menu_window.convertPointFromScreen_(mouse_location)

        # Get the content view
        content_view = self.menu_window.contentView()
        if not content_view:
            return

        # Hit test to find which view is under the cursor
        hit_view = content_view.hitTest_(window_point)

        if hit_view:
            # Convert point to hit view's coordinate system
            point_in_view = hit_view.convertPoint_fromView_(window_point, None)

            # Create a fake mouse down event at this location
            fake_event = Cocoa.NSEvent.mouseEventWithType_location_modifierFlags_timestamp_windowNumber_context_eventNumber_clickCount_pressure_(
                Cocoa.NSEventTypeLeftMouseDown,
                window_point,
                0,
                0,
                self.menu_window.windowNumber(),
                None,
                0,
                1,
                1.0
            )

            # Send the mouse down event to the view
            if hasattr(hit_view, 'mouseDown_'):
                hit_view.mouseDown_(fake_event)

    def is_menu_visible(self):
        """
        Check if the menu is currently visible.

        Returns:
            True if menu is visible, False otherwise
        """
        return self.menu_window is not None and self.menu_window.isVisible()

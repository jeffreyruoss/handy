"""
Menu UI Module
Handles the popup menu display and interaction.
"""

import objc
import Cocoa
from actions import Actions


class MenuUI(Cocoa.NSObject):
    """Creates and displays a popup menu at cursor position."""

    def init(self):
        """Initialize the menu UI."""
        self = objc.super(MenuUI, self).init()
        if self is None:
            return None

        self.actions = Actions.alloc().init()
        return self

    def showMenuAtLocation_(self, location_dict):
        """
        Display the popup menu at the specified coordinates.
        This method is called on the main thread.

        Args:
            location_dict: Dictionary with 'x' and 'y' keys for coordinates
        """
        x = location_dict['x']
        y = location_dict['y']

        # Remember the currently active app so we can return focus to it
        workspace = Cocoa.NSWorkspace.sharedWorkspace()
        active_app = workspace.frontmostApplication()
        if active_app:
            self.actions.setPreviousApp_(active_app)
            print(f"Previous app: {active_app.localizedName()}")

        # Create the menu
        menu = Cocoa.NSMenu.alloc().init()
        menu.setAutoenablesItems_(False)

        # Add Copy menu item
        copy_item = Cocoa.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Copy", "performCopy:", ""
        )
        copy_item.setTarget_(self.actions)
        copy_item.setEnabled_(True)
        menu.addItem_(copy_item)

        # Add Paste menu item
        paste_item = Cocoa.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Paste", "performPaste:", ""
        )
        paste_item.setTarget_(self.actions)
        paste_item.setEnabled_(True)
        menu.addItem_(paste_item)

        # Add Select All menu item
        select_all_item = Cocoa.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Select All", "performSelectAll:", ""
        )
        select_all_item.setTarget_(self.actions)
        select_all_item.setEnabled_(True)
        menu.addItem_(select_all_item)

        # Add Select All & Copy menu item
        select_all_copy_item = Cocoa.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Select All & Copy", "performSelectAllCopy:", ""
        )
        select_all_copy_item.setTarget_(self.actions)
        select_all_copy_item.setEnabled_(True)
        menu.addItem_(select_all_copy_item)

        # Add Pastebot menu item
        pastebot_item = Cocoa.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Pastebot (Cmd+Shift+V)", "performPastebot:", ""
        )
        pastebot_item.setTarget_(self.actions)
        pastebot_item.setEnabled_(True)
        menu.addItem_(pastebot_item)

        # Add Paste Without Formatting menu item
        paste_plain_item = Cocoa.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Paste Without Formatting", "performPastePlain:", ""
        )
        paste_plain_item.setTarget_(self.actions)
        paste_plain_item.setEnabled_(True)
        menu.addItem_(paste_plain_item)

        # Add separator
        menu.addItem_(Cocoa.NSMenuItem.separatorItem())

        # Add Quit menu item
        quit_item = Cocoa.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Quit Handy App", "performQuit:", ""
        )
        quit_item.setTarget_(self.actions)
        quit_item.setEnabled_(True)
        menu.addItem_(quit_item)

        # Convert coordinates (macOS uses bottom-left origin, pynput uses top-left)
        screen_height = Cocoa.NSScreen.mainScreen().frame().size.height
        cocoa_y = screen_height - y

        # Create a point for the menu location
        location = Cocoa.NSMakePoint(x, cocoa_y)

        # Pop up the menu at the location
        # We need to activate the app first to make the menu appear in front
        app = Cocoa.NSApplication.sharedApplication()
        app.activateIgnoringOtherApps_(True)

        menu.popUpMenuPositioningItem_atLocation_inView_(
            None,  # positioning item
            location,  # location
            None  # view (None means screen coordinates)
        )

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

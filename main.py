#!/usr/bin/env python3
"""
Handy App - Quick Menu Launcher
Main entry point for the application.
"""

import sys
import objc
import Cocoa
from PyObjCTools import AppHelper
from hotkey_listener import HotkeyListener
from menu_ui import MenuUI


class AppDelegate(Cocoa.NSObject):
    """Application delegate to handle app lifecycle."""

    def init(self):
        """Initialize the delegate."""
        self = objc.super(AppDelegate, self).init()
        if self is None:
            return None

        self.listener = None
        self.menu_ui = None
        return self

    def applicationDidFinishLaunching_(self, notification):
        """Called when the application finishes launching."""
        print("Starting Handy App...")
        print("Press Cmd+Shift+Space to open the quick menu.")
        print("Press Ctrl+C in terminal to quit.\n")

        # Create menu UI instance (on main thread)
        self.menu_ui = MenuUI()

        # Create and start hotkey listener
        self.listener = HotkeyListener(self.menu_ui)
        self.listener.start()


def main():
    """Initialize and start the application."""
    # Create the app
    app = Cocoa.NSApplication.sharedApplication()

    # Create and set the delegate
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)

    # Set activation policy to accessory (no dock icon)
    app.setActivationPolicy_(Cocoa.NSApplicationActivationPolicyAccessory)

    # Run the app
    AppHelper.runEventLoop()


if __name__ == "__main__":
    main()

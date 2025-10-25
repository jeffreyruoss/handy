"""
Actions Module
Implements menu actions like copy, paste, and quit.
"""

import sys
import subprocess
import objc
import Cocoa
from PyObjCTools import AppHelper


class Actions(Cocoa.NSObject):
    """Handles menu actions using PyObjC."""

    def init(self):
        """Initialize the actions handler."""
        self = objc.super(Actions, self).init()
        if self is None:
            return None
        self.previous_app = None
        return self

    def setPreviousApp_(self, app):
        """Store the previously active application."""
        self.previous_app = app

    def sendKeystroke_(self, key_name):
        """
        Send a keystroke using AppleScript to the previously active app.

        Args:
            key_name: The key name ('c' for copy, 'v' for paste)
        """
        # Reactivate the previous app first
        if self.previous_app:
            app_name = self.previous_app.localizedName()
            print(f"Reactivating: {app_name}")
            self.previous_app.activateWithOptions_(Cocoa.NSApplicationActivateIgnoringOtherApps)

        # Use AppleScript with proper error handling
        # The delay helps ensure the app is reactivated
        script = f'''
        delay 0.2
        tell application "System Events"
            keystroke "{key_name}" using command down
        end tell
        '''

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                print(f"Keystroke '{key_name}' sent successfully")
            else:
                print(f"AppleScript error: {result.stderr.strip()}")

                # Check if it's a permission error
                if "not allowed" in result.stderr or "1002" in result.stderr:
                    print("\n⚠️  PERMISSION NEEDED:")
                    print("   Terminal/Warp needs permission to control your computer.")
                    print("   Run this command to open System Settings:")
                    print("   open 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'")
                    print("   Then manually add Warp or Terminal and enable it.\n")

        except subprocess.TimeoutExpired:
            print("Keystroke timed out")
        except Exception as e:
            print(f"Error sending keystroke: {e}")

    def performCopy_(self, sender):
        """
        Perform copy action (Cmd+C).

        Args:
            sender: The menu item that triggered this action
        """
        print("Executing Copy (Cmd+C)")
        self.sendKeystroke_('c')

    def performPaste_(self, sender):
        """
        Perform paste action (Cmd+V).

        Args:
            sender: The menu item that triggered this action
        """
        print("Executing Paste (Cmd+V)")
        self.sendKeystroke_('v')

    def performRestart_(self, sender):
        """
        Restart the application.

        Args:
            sender: The menu item that triggered this action
        """
        print("Restarting Handy App...")
        import os
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def performQuit_(self, sender):
        """
        Quit the application.

        Args:
            sender: The menu item that triggered this action
        """
        print("Quitting Handy App...")
        AppHelper.stopEventLoop()
        sys.exit(0)

    def performSelectAll_(self, sender):
        """
        Perform select all action (Cmd+A).
        """
        print("Executing Select All (Cmd+A)")
        self.sendKeystrokeWithModifiers_({'key_name': 'a', 'modifiers': ['command']})

    def performSelectAllCopy_(self, sender):
        """
        Perform select all and copy action (Cmd+A then Cmd+C).
        """
        print("Executing Select All & Copy (Cmd+A then Cmd+C)")
        self.sendKeystrokeWithModifiers_({'key_name': 'a', 'modifiers': ['command']})
        # Small delay between commands
        import time
        time.sleep(0.15)
        self.sendKeystrokeWithModifiers_({'key_name': 'c', 'modifiers': ['command']})

    def performPastebot_(self, sender):
        """
        Perform Pastebot action (Cmd+Shift+V).
        """
        print("Executing Pastebot (Cmd+Shift+V)")
        self.sendKeystrokeWithModifiers_({'key_name': 'v', 'modifiers': ['command', 'shift']})

    def performPastePlain_(self, sender):
        """
        Perform Paste Without Formatting (Cmd+Option+Shift+V).
        """
        print("Executing Paste Without Formatting (Cmd+Option+Shift+V)")
        self.sendKeystrokeWithModifiers_({'key_name': 'v', 'modifiers': ['command', 'shift', 'option']})

    def performDictation_(self, sender):
        """
        Perform Dictation by directly starting dictation.
        """
        print("Executing Dictation")
        if self.previous_app:
            app_name = self.previous_app.localizedName()
            print(f"Reactivating: {app_name}")
            self.previous_app.activateWithOptions_(Cocoa.NSApplicationActivateIgnoringOtherApps)

        # Use AppleScript to start dictation directly
        script = '''
        delay 0.25
        tell application "System Events"
            tell (first application process whose frontmost is true)
                click menu item "Start Dictation" of menu "Edit" of menu bar 1
            end tell
        end tell
        '''
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                print("Dictation started successfully")
            else:
                print(f"AppleScript error: {result.stderr.strip()}")
                # Fallback: try using the keyboard shortcut fn+fn
                print("Trying alternate method with fn key...")
                script2 = '''
                tell application "System Events"
                    key code 63
                    delay 0.1
                    key code 63
                end tell
                '''
                result2 = subprocess.run(
                    ['osascript', '-e', script2],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result2.returncode == 0:
                    print("Dictation triggered with fn key")
                else:
                    print(f"Fn key method also failed: {result2.stderr.strip()}")
        except subprocess.TimeoutExpired:
            print("Dictation trigger timed out")
        except Exception as e:
            print(f"Error triggering dictation: {e}")

    def sendKeystrokeWithModifiers_(self, args):
        """
        Send a keystroke with specified modifiers using AppleScript.
        """
        if self.previous_app:
            app_name = self.previous_app.localizedName()
            print(f"Reactivating: {app_name}")
            self.previous_app.activateWithOptions_(Cocoa.NSApplicationActivateIgnoringOtherApps)

        # Build AppleScript modifiers string
        key_name = args['key_name']
        modifiers = args['modifiers']
        mod_str = ' using ' + ' & '.join([f'{mod} down' for mod in modifiers]) if modifiers else ''
        script = f'''
        delay 0.25
        tell application "System Events"
            keystroke "{key_name}"{mod_str}
        end tell
        '''
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                print(f"Keystroke '{key_name}' with {modifiers} sent successfully")
            else:
                print(f"AppleScript error: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            print("Keystroke timed out")
        except Exception as e:
            print(f"Error sending keystroke: {e}")

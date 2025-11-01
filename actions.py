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

    # Delay in seconds before sending keystrokes (adjust this value to tune responsiveness)
    KEYSTROKE_DELAY = 0.01

    def init(self):
        """Initialize the actions handler."""
        self = objc.super(Actions, self).init()
        if self is None:
            return None
        self.previous_app = None
        self.captured_text = None
        return self

    def set_captured_text(self, text):
        """Store captured text for use by Copy action."""
        self.captured_text = text

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
        delay {self.KEYSTROKE_DELAY}
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

    def activateApp_(self, app_path_obj):
        """
        Activate (bring to front) the specified application.

        Args:
            app_path_obj: Dictionary with 'path' key containing app path
        """
        app_path = app_path_obj['path'] if isinstance(app_path_obj, dict) else app_path_obj

        workspace = Cocoa.NSWorkspace.sharedWorkspace()

        # Try to find the running app by bundle identifier or path
        bundle_url = Cocoa.NSURL.fileURLWithPath_(app_path)
        bundle = Cocoa.NSBundle.bundleWithURL_(bundle_url)

        if bundle:
            bundle_id = bundle.bundleIdentifier()
            running_apps = workspace.runningApplications()

            # Look for the app in running applications
            for app in running_apps:
                if app.bundleIdentifier() == bundle_id:
                    print(f"Activating {app.localizedName()}")
                    app.activateWithOptions_(Cocoa.NSApplicationActivateIgnoringOtherApps)
                    return

            # App not running, launch it
            print(f"Launching {app_path}")
            workspace.openURL_(bundle_url)
        else:
            print(f"Could not find bundle for {app_path}")

    def performCopy_(self, sender):
        """
        Perform copy action - use captured text if available, otherwise Cmd+C.

        Args:
            sender: The menu item that triggered this action
        """
        if self.captured_text:
            print(f"Copying captured text to clipboard: {self.captured_text[:50]}...")
            import Cocoa
            pasteboard = Cocoa.NSPasteboard.generalPasteboard()
            pasteboard.clearContents()
            pasteboard.setString_forType_(self.captured_text, Cocoa.NSPasteboardTypeString)
        else:
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

    def performSave_(self, sender):
        """
        Perform save action (Cmd+S).

        Args:
            sender: The menu item that triggered this action
        """
        print("Executing Save (Cmd+S)")
        self.sendKeystroke_('s')

    def performAlfred_(self, sender):
        """
        Perform Alfred action (Option+Space).

        Args:
            sender: The menu item that triggered this action
        """
        print("Executing Alfred (Option+Space)")
        self.sendKeystrokeWithModifiers_({'key_name': ' ', 'modifiers': ['option']})

    def performSwitchWindow_(self, sender):
        """
        Perform Switch Window action (Cmd+`).

        Args:
            sender: The menu item that triggered this action
        """
        print("Executing Switch Window (Cmd+`)")
        self.sendKeystrokeWithModifiers_({'key_name': '`', 'modifiers': ['command']})

    def performEscape_(self, sender):
        """
        Perform Escape action (Esc key).

        Args:
            sender: The menu item that triggered this action
        """
        print("Executing Escape")
        self.sendKeystrokeWithModifiers_({'key_name': '\x1b', 'modifiers': []})

    def performTab_(self, sender):
        """
        Perform Tab action (Tab key).

        Args:
            sender: The menu item that triggered this action
        """
        print("Executing Tab")
        self.sendKeystrokeWithModifiers_({'key_name': '\t', 'modifiers': []})

    def performFind_(self, sender):
        """
        Perform Find action (Cmd+F).

        Args:
            sender: The menu item that triggered this action
        """
        print("Executing Find (Cmd+F)")
        self.sendKeystrokeWithModifiers_({'key_name': 'f', 'modifiers': ['command']})

    def performUndo_(self, sender):
        """
        Perform Undo action (Cmd+Z).

        Args:
            sender: The menu item that triggered this action
        """
        print("Executing Undo (Cmd+Z)")
        self.sendKeystrokeWithModifiers_({'key_name': 'z', 'modifiers': ['command']})

    def performDeselect_(self, sender):
        """
        Perform Deselect action (Cmd+D).

        Args:
            sender: The menu item that triggered this action
        """
        print("Executing Deselect (Cmd+D)")
        self.sendKeystrokeWithModifiers_({'key_name': 'd', 'modifiers': ['command']})

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

    def performPixelSnap_(self, sender):
        """
        Perform PixelSnap action (Cmd+Option+S).
        """
        print("Executing PixelSnap (Cmd+Option+S)")
        self.sendKeystrokeWithModifiers_({'key_name': 's', 'modifiers': ['command', 'option']})

    def performColorSlurp_(self, sender):
        """
        Perform ColorSlurp action (Cmd+Option+Control+C).
        """
        print("Executing ColorSlurp (Cmd+Option+Control+C)")
        self.sendKeystrokeWithModifiers_({'key_name': 'c', 'modifiers': ['command', 'option', 'control']})

    def performScreenCapture_(self, sender):
        """
        Perform Screen Capture using native macOS screencapture command.
        """
        print("Executing Screen Capture")
        try:
            # Use the native screencapture command with interactive mode
            # -i = interactive mode (click and drag to select area)
            # -c = copy to clipboard instead of saving to file
            subprocess.Popen(['screencapture', '-i', '-c'])
            print("Screenshot tool launched")
        except Exception as e:
            print(f"Error launching screenshot: {e}")

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
        script = f'''
        delay {self.KEYSTROKE_DELAY}
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
        delay {self.KEYSTROKE_DELAY}
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

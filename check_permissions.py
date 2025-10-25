#!/usr/bin/env python3
"""Check if we have accessibility permissions."""

import Quartz

def check_accessibility():
    """Check if the app has accessibility permissions."""
    trusted = Quartz.AXIsProcessTrusted()
    print(f"Accessibility permissions: {'✓ Granted' if trusted else '✗ Not granted'}")

    if not trusted:
        print("\nTo grant accessibility permissions:")
        print("1. Open System Settings")
        print("2. Go to Privacy & Security → Accessibility")
        print("3. Add Python or Warp to the list and enable it")
        print("\nOr run this to trigger the permission prompt:")
        print("Run the app and use the Copy/Paste features")

if __name__ == "__main__":
    check_accessibility()

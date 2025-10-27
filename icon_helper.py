"""
Icon Helper
Utility to get absolute paths for icons.
"""

import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(SCRIPT_DIR, 'icons')


def icon_path(filename):
    """
    Get the absolute path to an icon file.

    Args:
        filename: Name of the icon file (e.g., 'copy.png')

    Returns:
        Absolute path to the icon file, or None if it doesn't exist
    """
    path = os.path.join(ICONS_DIR, filename)
    return path if os.path.exists(path) else None


def list_icons():
    """List all icon files in the icons directory."""
    if not os.path.exists(ICONS_DIR):
        return []

    icons = []
    for file in os.listdir(ICONS_DIR):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            icons.append(file)
    return icons


if __name__ == '__main__':
    """Print all available icons when run as a script."""
    icons = list_icons()
    if icons:
        print("Available icons:")
        for icon in icons:
            print(f"  - {icon}")
    else:
        print(f"No icons found in {ICONS_DIR}")
        print("Add 40x40px PNG files to start using icons.")

# Handy App

A macOS productivity utility featuring a circular pie menu activated by the mouse wheel button. Designed to make common actions accessible with one hand, this app was created to improve workflow efficiency while recovering from a hand injury.

## Features

- **Global Mouse Wheel Hotkey**: Press the middle mouse button anywhere to open the menu (press again to close)
- **Circular Pie Menu**: Beautiful radial menu with 8 frequently-used actions
- **Secondary Menu Bar**: Horizontal menu below the pie for less common actions
- **One-Handed Operation**: All actions accessible via mouse clicks - no keyboard required
- **Quick Actions**:
  - Copy (Cmd+C)
  - Paste (Cmd+V)
  - Pastebot (Cmd+Shift+V)
  - Paste Plain Text (Cmd+Option+Shift+V)
  - Dictation
  - Select All (Cmd+A)
  - Select All & Copy
- **App Launchers**: Instantly switch to or launch:
  - Dia
  - Visual Studio Code (Insiders)
  - Notion
- **Customizable**: Easy to add more apps or modify actions in the code
- **Lightweight**: Runs in the background with minimal resource usage
- **Hover Effects**: Visual feedback showing which action you're about to select

## Origin Story

This app was developed out of necessity during recovery from a hand injury that limited me to working with one hand. Traditional keyboard shortcuts became difficult, so I created a mouse-centric interface that puts all essential commands within reach of a single click. The circular pie menu design maximizes the number of actions while minimizing mouse movement.

## Requirements

- macOS 10.14 or later (tested on macOS Sequoia 15.1)
- Python 3.8+ (tested with Python 3.13)
- Accessibility and Automation permissions for the terminal

## Setup

1. **Clone or download this repository**:
   ```bash
   git clone <repository-url>
   cd handy-app
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Grant Permissions

For the app to work globally, you need to grant two types of permissions:

### 1. Input Monitoring (for mouse detection)
1. Run the app once - you may see a permission prompt
2. Open **System Settings** → **Privacy & Security** → **Input Monitoring**
3. Enable your terminal (Warp, Terminal, or iTerm2)

### 2. Accessibility & Automation (for sending keystrokes)
1. Open **System Settings** → **Privacy & Security** → **Accessibility**
2. Click the lock icon and authenticate
3. Add your terminal app (Warp, Terminal, or iTerm2) to the list
4. Enable the checkbox next to it

4. Also check **Privacy & Security** → **Automation**
5. Ensure your terminal is allowed to control "System Events"

**Important**: After granting permissions, fully quit and restart your terminal app for the changes to take effect.

## Usage

Run the app with:

```bash
python main.py
```

Or use the convenience script:

```bash
./run.sh
```

Once running:
- **Press the mouse wheel button** to open the menu (press again to close it)
- **Hover** over an action to highlight it
- **Click** on any menu item to execute it
- Press **Ctrl+C** in the terminal to quit

### Menu Layout

**Pie Menu (Circular)**:
- Copy
- Paste
- Pastebot
- Paste Plain
- Dictation
- Dia (app launcher)
- VS Code (app launcher)
- Notion (app launcher)

**Secondary Menu (Horizontal Bar)**:
- Select All
- Select All & Copy
- Restart Handy (restarts the app)

## Customization

### Adjusting Response Speed
In `actions.py`, modify the `KEYSTROKE_DELAY` constant (line 17):
```python
KEYSTROKE_DELAY = 0.01  # Lower = faster, higher = more reliable
```

### Adding More Apps
In `menu_ui.py`, add new items to the `menu_items` list:
```python
{'title': 'MyApp', 'action': 'activateApp:', 'target': self.actions, 'app_path': '/Applications/MyApp.app'},
```

### Changing Menu Size
In `pie_menu_view.py`, adjust the `radius` (line 22):
```python
self.radius = 160  # Increase for larger menu
```

In `menu_ui.py`, adjust `menu_size` (line 66):
```python
menu_size = 340  # Should be radius * 2 + padding
```

## Project Structure

```
handy-app/
├── main.py                   # Entry point with NSApplication event loop
├── hotkey_listener.py        # Global mouse button detection via pynput
├── menu_ui.py               # Menu display coordinator
├── pie_menu_view.py         # Custom NSView for circular pie menu
├── secondary_menu_view.py   # Custom NSView for horizontal button menu
├── actions.py               # Action handlers using AppleScript
├── requirements.txt         # Python dependencies
├── run.sh                   # Convenience launch script
├── README.md               # This file
└── MACOS_PYTHON_APP_GUIDE.md  # Development notes and gotchas
```

## Technical Details

- **UI Framework**: PyObjC (Cocoa/AppKit) for native macOS integration
- **Input Detection**: pynput for global mouse event listening
- **Keystroke Simulation**: AppleScript via subprocess for reliable key sending
- **Threading**: Main thread for all UI operations, background thread for input monitoring
- **Drawing**: Custom NSView subclasses with NSBezierPath for pie slices and rounded buttons

## Troubleshooting

**Menu doesn't appear**:
- Check that you've granted Input Monitoring permissions
- Ensure Accessibility permissions are granted to your terminal
- Make sure the virtual environment is activated
- Verify all dependencies are installed with `pip list`

**Copy/Paste doesn't work**:
- Ensure Accessibility AND Automation permissions are granted
- Restart your terminal completely after granting permissions
- Check terminal output for "osascript is not allowed" errors
- Some apps have their own clipboard handling that may interfere

**App launches but crashes on second menu open**:
- This was fixed in recent commits - make sure you have the latest code
- The window cleanup logic now properly manages window lifecycle

**Menu appears in wrong location**:
- This is normal - macOS uses bottom-left origin for screen coordinates
- The code handles coordinate conversion automatically

## Future Enhancements

- Configuration file (JSON/YAML) for menu customization without editing code
- Support for user-defined keyboard shortcuts in addition to mouse wheel
- Icon/emoji support for menu items
- Themes and color customization
- Package as standalone .app bundle for easier distribution
- Multi-monitor support improvements
- Configurable menu position offset
- Action history/favorites

## License

This project is open source and available for personal use and modification.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

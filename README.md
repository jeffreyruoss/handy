# Handy App

A macOS utility that displays a quick menu when you press the mouse wheel button, providing instant access to common actions like Copy and Paste.

## Features

- **Global Hotkey**: Press the mouse wheel button anywhere to open the menu
- **Quick Actions**: Copy and Paste shortcuts
- **Lightweight**: Runs in the background with minimal resource usage

## Requirements

- macOS 10.14 or later
- Python 3.8+
- Accessibility permissions for the terminal or Python

## Setup

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Grant Accessibility Permissions

For the app to work globally, you need to grant accessibility permissions:

1. Open **System Preferences** → **Privacy & Security** → **Accessibility**
2. Click the lock icon and authenticate
3. Add **Terminal** (or **iTerm2** if you use that) to the list
4. Enable the checkbox next to it

Alternatively, if running Python directly, you may need to add Python to the accessibility list.

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
- **Press the mouse wheel button** to open the quick menu
- Select **Copy** or **Paste** from the menu
- Press **Ctrl+C** in the terminal to quit

## Project Structure

```
handy-app/
├── main.py              # Entry point
├── hotkey_listener.py   # Mouse event detection
├── menu_ui.py          # Popup menu UI
├── actions.py          # Menu action handlers
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Troubleshooting

**Menu doesn't appear**:
- Check that you've granted Accessibility permissions
- Make sure the virtual environment is activated
- Verify all dependencies are installed

**Copy/Paste doesn't work**:
- Ensure the target application is focused before selecting the menu item
- Some applications may have their own clipboard handling

## Future Enhancements

- Customizable menu items
- Configuration file for hotkey customization
- Additional quick actions
- App bundle for easier distribution

# Icons Directory

Place your 40x40px icon files here in PNG, JPEG, or WebP format.

## Icon naming suggestions:
- `copy.png` - Copy action icon
- `paste.png` - Paste action icon
- `pastebot.png` - Pastebot action icon
- `paste-plain.png` - Paste plain action icon
- `dictation.png` - Dictation action icon
- `dia.png` - Dia app icon
- `vscode.png` - VS Code app icon
- `notion.png` - Notion app icon

## Usage:

After adding icons to this directory, update the menu items in `menu_ui.py`:

```python
menu_items = [
    {
        'title': 'Copy',
        'action': 'performCopy:',
        'target': self.actions,
        'icon': '/Users/jeffreyruoss/Projects/handy-app/icons/copy.png'
    },
    # ... more items
]
```

**Note:** PNG format is recommended for best quality and transparency support.

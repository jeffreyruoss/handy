# Works on this Mac system (tested October 25, 2025)

- **Model:** Mac mini (2024)
- **Chip:** Apple M4 Pro
- **Memory:** 48 GB
- **Startup disk:** Macintosh HD
- **Serial number:** HXCHXVG27C
- **macOS:** Sequoia 15.1

---

# Building Python Mac Apps - Quick Guide

## Minimal Setup

- **Use PyObjC** for native macOS integration (`pyobjc-framework-Cocoa`)
- **Use pynput** for global keyboard/mouse listening (requires `pyobjc-framework-Quartz`)
- **Run with NSApplication event loop** for UI elements to work properly:
  ```python
  from PyObjCTools import AppHelper
  AppHelper.runEventLoop()
  ```

## Critical Permissions Gotchas

### Input Monitoring
- Required for: Global keyboard/mouse event listening
- **Auto-granted**: macOS prompts automatically when app first tries to listen
- Location: System Settings → Privacy & Security → **Input Monitoring**
- Grant to: Your terminal app (Warp, Terminal, iTerm2)

### Accessibility
- Required for: Sending keystrokes, controlling other apps
- **The Gotcha**: There are TWO "Accessibility" windows in macOS!
  - ❌ **Wrong one**: Search "Accessibility" in System Settings (shows features like VoiceOver, Zoom)
  - ✅ **Right one**: Privacy & Security → scroll down → **Accessibility** (shows apps list)
- Grant to: Your terminal app or `osascript` (for AppleScript approach)

## Threading for UI

- **Problem**: macOS UI must run on main thread
- **Solution**: Use `performSelectorOnMainThread_withObject_waitUntilDone_()` to call UI methods from background threads
- Example:
  ```python
  self.performSelectorOnMainThread_withObject_waitUntilDone_(
      "showMenuAtLocation:",
      {'x': x, 'y': y},
      False
  )
  ```

## Sending Keystrokes

Two approaches:
1. **CGEvent** (Quartz) - Fast but requires Accessibility permission
2. **AppleScript** - Slower but more reliable with permissions
   ```python
   subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "c" using command down'])
   ```

## Background Apps (No Dock Icon)

```python
app.setActivationPolicy_(Cocoa.NSApplicationActivationPolicyAccessory)
```

## Key Takeaway

The biggest gotcha is the **two Accessibility settings pages**. Always go through Privacy & Security to find the actual permissions list.

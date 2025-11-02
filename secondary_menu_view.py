"""
Secondary Menu View Module
Creates a horizontal menu bar below the pie menu for less frequently used actions.
"""

import objc
import Cocoa


class SecondaryMenuView(Cocoa.NSView):
    """Custom view that draws a horizontal menu bar with clickable buttons."""

    def initWithFrame_(self, frame):
        """Initialize the secondary menu view."""
        self = objc.super(SecondaryMenuView, self).initWithFrame_(frame)
        if self is None:
            return None

        self.menu_items = []
        self.hovered_index = -1
        self.tracking_area = None
        self.icon_cache = {}  # Cache loaded icons

        return self

    def updateTrackingAreas(self):
        """Set up mouse tracking for hover effects."""
        objc.super(SecondaryMenuView, self).updateTrackingAreas()

        if self.tracking_area:
            self.removeTrackingArea_(self.tracking_area)

        tracking_options = (
            Cocoa.NSTrackingMouseEnteredAndExited |
            Cocoa.NSTrackingMouseMoved |
            Cocoa.NSTrackingActiveAlways |
            Cocoa.NSTrackingInVisibleRect
        )

        self.tracking_area = Cocoa.NSTrackingArea.alloc().initWithRect_options_owner_userInfo_(
            self.bounds(),
            tracking_options,
            self,
            None
        )
        self.addTrackingArea_(self.tracking_area)

    def resetCursorRects(self):
        """Set up cursor rectangles for the entire view."""
        objc.super(SecondaryMenuView, self).resetCursorRects()
        self.addCursorRect_cursor_(self.bounds(), Cocoa.NSCursor.pointingHandCursor())

    def setMenuItems_(self, items):
        """
        Set the menu items to display.

        Args:
            items: List of dictionaries with 'title', 'action', and 'target'
        """
        self.menu_items = items
        self.setNeedsDisplay_(True)

    def drawRect_(self, rect):
        """
        Draw the secondary menu as a grid with max 3 columns.

        Args:
            rect: The rectangle to draw in
        """
        if not self.menu_items:
            return

        bounds = self.bounds()
        num_items = len(self.menu_items)

        if num_items == 0:
            return

        # === ADJUSTABLE PARAMETERS ===
        button_spacing = 8              # Space between buttons (horizontal and vertical)
        vertical_button_padding = 6    # Padding inside button (top and bottom)
        icon_text_spacing = 3           # Space between icon and text
        icon_size = 30                  # Icon size
        text_height = 12                # Approximate text height
        # ============================

        # Grid layout: max 3 columns
        max_columns = 3
        num_columns = min(num_items, max_columns)
        num_rows = (num_items + num_columns - 1) // num_columns  # Ceiling division

        # Calculate button height based on content
        button_height = (vertical_button_padding * 2) + icon_size + icon_text_spacing + text_height

        # Calculate total grid dimensions
        total_grid_width = (num_columns * bounds.size.width / max_columns) + ((num_columns - 1) * button_spacing)
        total_grid_height = (num_rows * button_height) + ((num_rows - 1) * button_spacing)

        # Calculate button width to fit evenly
        button_width = (bounds.size.width - (button_spacing * (num_columns + 1))) / num_columns

        # Center the grid vertically and horizontally
        start_x = (bounds.size.width - (num_columns * button_width + (num_columns - 1) * button_spacing)) / 2
        start_y = (bounds.size.height - total_grid_height) / 2

        # Draw each button (reversed rows so top of array = top row)
        for i, item in enumerate(self.menu_items):
            row = (num_rows - 1) - (i // num_columns)
            col = i % num_columns

            x_offset = start_x + col * (button_width + button_spacing)
            y_offset = start_y + row * (button_height + button_spacing)

            button_rect = Cocoa.NSMakeRect(
                x_offset,
                y_offset,
                button_width,
                button_height
            )

            # Create rounded rectangle path
            path = Cocoa.NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
                button_rect,
                5,
                5
            )

            # Fill color - highlight if hovered
            if i == self.hovered_index:
                Cocoa.NSColor.colorWithCalibratedRed_green_blue_alpha_(0.35, 0.35, 0.35, 0.9).setFill()
            else:
                Cocoa.NSColor.colorWithCalibratedRed_green_blue_alpha_(0.25, 0.25, 0.25, 0.85).setFill()

            path.fill()

            # Draw border
            Cocoa.NSColor.colorWithCalibratedWhite_alpha_(0.9, 0.5).setStroke()
            path.setLineWidth_(1.0)
            path.stroke()

            # Draw icon if available
            if 'icon' in item and item['icon']:
                icon = self.loadIcon_(item['icon'])
                if icon:
                    icon_x = x_offset + (button_width - icon_size) / 2
                    icon_y = y_offset + vertical_button_padding + text_height + icon_text_spacing
                    icon_rect = Cocoa.NSMakeRect(
                        icon_x,
                        icon_y,
                        icon_size,
                        icon_size
                    )

                    # Save graphics state
                    Cocoa.NSGraphicsContext.currentContext().saveGraphicsState()

                    # Create rounded rectangle clipping path for icon
                    icon_corner_radius = 4
                    icon_clip_path = Cocoa.NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
                        icon_rect,
                        icon_corner_radius,
                        icon_corner_radius
                    )
                    icon_clip_path.addClip()

                    # Draw the icon
                    icon.drawInRect_fromRect_operation_fraction_(
                        icon_rect,
                        Cocoa.NSZeroRect,
                        Cocoa.NSCompositeSourceOver,
                        1.0
                    )

                    # Restore graphics state
                    Cocoa.NSGraphicsContext.currentContext().restoreGraphicsState()

            # Draw text label with word wrapping
            paragraph_style = Cocoa.NSMutableParagraphStyle.alloc().init()
            paragraph_style.setAlignment_(Cocoa.NSTextAlignmentCenter)
            paragraph_style.setLineBreakMode_(Cocoa.NSLineBreakByWordWrapping)

            attributes = {
                Cocoa.NSFontAttributeName: Cocoa.NSFont.systemFontOfSize_(10),
                Cocoa.NSForegroundColorAttributeName: Cocoa.NSColor.whiteColor(),
                Cocoa.NSParagraphStyleAttributeName: paragraph_style
            }

            title = Cocoa.NSString.stringWithString_(item['title'])
            text_max_width = button_width - 8
            text_rect = Cocoa.NSMakeRect(
                x_offset + 4,
                y_offset + vertical_button_padding,
                text_max_width,
                text_height
            )
            title.drawInRect_withAttributes_(text_rect, attributes)

    def mouseMoved_(self, event):
        """Handle mouse movement for hover effect."""
        point = self.convertPoint_fromView_(event.locationInWindow(), None)
        index = self.getButtonIndexAtPoint_(point)

        # Update cursor based on whether we're over a button
        if index >= 0:
            Cocoa.NSCursor.pointingHandCursor().set()
        else:
            Cocoa.NSCursor.arrowCursor().set()

        self.updateHoveredIndex_(point)

    def mouseDragged_(self, event):
        """Handle left mouse button drag."""
        self.mouseMoved_(event)

    def rightMouseDragged_(self, event):
        """Handle right mouse button drag."""
        self.mouseMoved_(event)

    def otherMouseDragged_(self, event):
        """Handle other mouse button drag (middle button)."""
        self.mouseMoved_(event)

    def mouseDown_(self, event):
        """Handle mouse click to select menu item."""
        point = self.convertPoint_fromView_(event.locationInWindow(), None)
        index = self.getButtonIndexAtPoint_(point)

        if index >= 0 and index < len(self.menu_items):
            item = self.menu_items[index]
            target = item['target']
            action = item['action']

            # Call the action
            if target and action:
                try:
                    # Check if this action needs an app_path parameter
                    if 'app_path' in item:
                        target.performSelector_withObject_(action, {'path': item['app_path']})
                    else:
                        target.performSelector_withObject_(action, None)
                except Exception as e:
                    print(f"Error calling action {action}: {e}")

            # Close the menu by hiding it
            window = self.window()
            if window:
                window.orderOut_(None)

    def updateHoveredIndex_(self, point):
        """Update which button is being hovered."""
        new_index = self.getButtonIndexAtPoint_(point)
        if new_index != self.hovered_index:
            self.hovered_index = new_index
            self.setNeedsDisplay_(True)

    def getButtonIndexAtPoint_(self, point):
        """
        Determine which button contains the point in grid layout.

        Args:
            point: NSPoint to check

        Returns:
            Index of the button, or -1 if not in any button
        """
        bounds = self.bounds()
        num_items = len(self.menu_items)

        if num_items == 0:
            return -1

        # === ADJUSTABLE PARAMETERS (must match drawRect_) ===
        button_spacing = 8
        vertical_button_padding = 8
        icon_text_spacing = 4
        icon_size = 30
        text_height = 12
        # ===================================================

        # Grid layout: max 3 columns
        max_columns = 3
        num_columns = min(num_items, max_columns)
        num_rows = (num_items + num_columns - 1) // num_columns

        # Calculate button height based on content
        button_height = (vertical_button_padding * 2) + icon_size + icon_text_spacing + text_height

        # Calculate total grid dimensions
        total_grid_height = (num_rows * button_height) + ((num_rows - 1) * button_spacing)

        # Calculate button width
        button_width = (bounds.size.width - (button_spacing * (num_columns + 1))) / num_columns

        # Center the grid
        start_x = (bounds.size.width - (num_columns * button_width + (num_columns - 1) * button_spacing)) / 2
        start_y = (bounds.size.height - total_grid_height) / 2

        # Check each button position (reversed rows to match rendering)
        for i in range(num_items):
            row = (num_rows - 1) - (i // num_columns)
            col = i % num_columns

            x_offset = start_x + col * (button_width + button_spacing)
            y_offset = start_y + row * (button_height + button_spacing)

            if (point.x >= x_offset and point.x <= x_offset + button_width and
                point.y >= y_offset and point.y <= y_offset + button_height):
                return i

        return -1

    def loadIcon_(self, icon_path):
        """
        Load an icon from the specified path and cache it.

        Args:
            icon_path: Path to the icon file (PNG, JPEG, WebP)

        Returns:
            NSImage object or None if loading fails
        """
        # Check cache first
        if icon_path in self.icon_cache:
            return self.icon_cache[icon_path]

        # Try to load the icon
        try:
            icon = Cocoa.NSImage.alloc().initWithContentsOfFile_(icon_path)
            if icon:
                # Resize to 18x18 for secondary menu
                icon.setSize_(Cocoa.NSMakeSize(18, 18))
                self.icon_cache[icon_path] = icon
                return icon
        except Exception as e:
            print(f"Error loading icon {icon_path}: {e}")

        return None

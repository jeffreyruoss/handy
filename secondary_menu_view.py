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
            Cocoa.NSTrackingActiveInKeyWindow
        )

        self.tracking_area = Cocoa.NSTrackingArea.alloc().initWithRect_options_owner_userInfo_(
            self.bounds(),
            tracking_options,
            self,
            None
        )
        self.addTrackingArea_(self.tracking_area)

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

        # Grid layout: max 3 columns
        max_columns = 3
        num_columns = min(num_items, max_columns)
        num_rows = (num_items + num_columns - 1) // num_columns  # Ceiling division

        # Calculate button dimensions and spacing
        total_width = bounds.size.width
        total_height = bounds.size.height
        button_spacing = 8

        # Calculate button size
        horizontal_spacing = button_spacing * (num_columns + 1)
        vertical_spacing = button_spacing * (num_rows + 1)
        button_width = (total_width - horizontal_spacing) / num_columns
        button_height = (total_height - vertical_spacing) / num_rows

        # Draw each button
        for i, item in enumerate(self.menu_items):
            row = i // num_columns
            col = i % num_columns

            x_offset = button_spacing + col * (button_width + button_spacing)
            y_offset = button_spacing + row * (button_height + button_spacing)

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
                Cocoa.NSColor.colorWithCalibratedRed_green_blue_alpha_(0.3, 0.5, 0.8, 0.9).setFill()
            else:
                Cocoa.NSColor.colorWithCalibratedRed_green_blue_alpha_(0.25, 0.25, 0.25, 0.85).setFill()

            path.fill()

            # Draw border
            Cocoa.NSColor.colorWithCalibratedWhite_alpha_(0.9, 0.5).setStroke()
            path.setLineWidth_(1.0)
            path.stroke()

            # Draw icon if available
            icon_size = 30
            if 'icon' in item and item['icon']:
                icon = self.loadIcon_(item['icon'])
                if icon:
                    icon_x = x_offset + (button_width - icon_size) / 2
                    icon_y = y_offset + (button_height - icon_size) / 2 + 8
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
            # Add padding to button width for text
            text_max_width = button_width - 8
            # Offset text down more if icon is present
            text_y_offset = -14 if 'icon' in item and item['icon'] else 0
            text_rect = Cocoa.NSMakeRect(
                x_offset + 4,
                y_offset + (button_height - 50) / 2 + text_y_offset,
                text_max_width,
                30  # Max height for wrapped text
            )
            title.drawInRect_withAttributes_(text_rect, attributes)

    def mouseMoved_(self, event):
        """Handle mouse movement for hover effect."""
        point = self.convertPoint_fromView_(event.locationInWindow(), None)
        self.updateHoveredIndex_(point)

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

        # Grid layout: max 3 columns
        max_columns = 3
        num_columns = min(num_items, max_columns)
        num_rows = (num_items + num_columns - 1) // num_columns

        # Calculate button dimensions
        total_width = bounds.size.width
        total_height = bounds.size.height
        button_spacing = 8

        horizontal_spacing = button_spacing * (num_columns + 1)
        vertical_spacing = button_spacing * (num_rows + 1)
        button_width = (total_width - horizontal_spacing) / num_columns
        button_height = (total_height - vertical_spacing) / num_rows

        # Check each button
        for i in range(num_items):
            row = i // num_columns
            col = i % num_columns

            x_offset = button_spacing + col * (button_width + button_spacing)
            y_offset = button_spacing + row * (button_height + button_spacing)

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

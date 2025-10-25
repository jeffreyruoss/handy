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
        Draw the secondary menu as horizontal buttons.

        Args:
            rect: The rectangle to draw in
        """
        if not self.menu_items:
            return

        bounds = self.bounds()
        num_items = len(self.menu_items)

        if num_items == 0:
            return

        # Calculate button width and spacing
        total_width = bounds.size.width
        button_spacing = 8
        total_spacing = button_spacing * (num_items + 1)
        button_width = (total_width - total_spacing) / num_items
        button_height = bounds.size.height - 10
        y_offset = 5

        # Draw each button
        for i, item in enumerate(self.menu_items):
            x_offset = button_spacing + i * (button_width + button_spacing)

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

            # Draw text label
            attributes = {
                Cocoa.NSFontAttributeName: Cocoa.NSFont.systemFontOfSize_(11),
                Cocoa.NSForegroundColorAttributeName: Cocoa.NSColor.whiteColor()
            }

            title = Cocoa.NSString.stringWithString_(item['title'])
            text_size = title.sizeWithAttributes_(attributes)
            text_rect = Cocoa.NSMakeRect(
                x_offset + (button_width - text_size.width) / 2,
                y_offset + (button_height - text_size.height) / 2,
                text_size.width,
                text_size.height
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
        Determine which button contains the point.

        Args:
            point: NSPoint to check

        Returns:
            Index of the button, or -1 if not in any button
        """
        bounds = self.bounds()
        num_items = len(self.menu_items)

        if num_items == 0:
            return -1

        # Calculate button dimensions
        total_width = bounds.size.width
        button_spacing = 8
        total_spacing = button_spacing * (num_items + 1)
        button_width = (total_width - total_spacing) / num_items
        button_height = bounds.size.height - 10
        y_offset = 5

        # Check if point is within vertical bounds
        if point.y < y_offset or point.y > y_offset + button_height:
            return -1

        # Determine which button horizontally
        for i in range(num_items):
            x_offset = button_spacing + i * (button_width + button_spacing)
            if point.x >= x_offset and point.x <= x_offset + button_width:
                return i

        return -1

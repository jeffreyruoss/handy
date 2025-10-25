"""
Pie Menu View Module
Creates a circular pie menu with radial slices for actions.
"""

import objc
import Cocoa
import math


class PieMenuView(Cocoa.NSView):
    """Custom view that draws and handles a circular pie menu."""

    def initWithFrame_(self, frame):
        """Initialize the pie menu view."""
        self = objc.super(PieMenuView, self).initWithFrame_(frame)
        if self is None:
            return None

        self.menu_items = []
        self.hovered_index = -1
        self.radius = 120
        self.center_radius = 30

        # Set up tracking area for mouse hover
        self.tracking_area = None

        return self

    def updateTrackingAreas(self):
        """Set up mouse tracking for hover effects."""
        objc.super(PieMenuView, self).updateTrackingAreas()

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
        Draw the pie menu.
        
        Args:
            rect: The rectangle to draw in
        """
        if not self.menu_items:
            return
        
        # Get the graphics context
        context = Cocoa.NSGraphicsContext.currentContext().CGContext()
        
        # Calculate center point
        bounds = self.bounds()
        center_x = bounds.size.width / 2
        center_y = bounds.size.height / 2
        
        # Number of slices
        num_items = len(self.menu_items)
        angle_per_slice = 2 * math.pi / num_items        # Draw each pie slice
        for i, item in enumerate(self.menu_items):
            start_angle = i * angle_per_slice - math.pi / 2
            end_angle = start_angle + angle_per_slice

            # Create pie slice path
            path = Cocoa.NSBezierPath.bezierPath()
            path.moveToPoint_(Cocoa.NSMakePoint(center_x, center_y))
            path.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_clockwise_(
                Cocoa.NSMakePoint(center_x, center_y),
                self.radius,
                math.degrees(start_angle),
                math.degrees(end_angle),
                False
            )
            path.closePath()

            # Fill color - highlight if hovered
            if i == self.hovered_index:
                Cocoa.NSColor.colorWithCalibratedRed_green_blue_alpha_(0.3, 0.5, 0.8, 0.9).setFill()
            else:
                Cocoa.NSColor.colorWithCalibratedRed_green_blue_alpha_(0.2, 0.2, 0.2, 0.85).setFill()

            path.fill()

            # Draw border
            Cocoa.NSColor.colorWithCalibratedWhite_alpha_(0.9, 0.5).setStroke()
            path.setLineWidth_(1.5)
            path.stroke()

            # Draw text label
            mid_angle = start_angle + angle_per_slice / 2
            text_radius = self.radius * 0.65
            text_x = center_x + text_radius * math.cos(mid_angle)
            text_y = center_y + text_radius * math.sin(mid_angle)

            # Create text attributes
            attributes = {
                Cocoa.NSFontAttributeName: Cocoa.NSFont.systemFontOfSize_(11),
                Cocoa.NSForegroundColorAttributeName: Cocoa.NSColor.whiteColor()
            }

            # Draw the title
            title = Cocoa.NSString.stringWithString_(item['title'])
            text_size = title.sizeWithAttributes_(attributes)
            text_rect = Cocoa.NSMakeRect(
                text_x - text_size.width / 2,
                text_y - text_size.height / 2,
                text_size.width,
                text_size.height
            )
            title.drawInRect_withAttributes_(text_rect, attributes)

        # Draw center circle
        center_path = Cocoa.NSBezierPath.bezierPathWithOvalInRect_(
            Cocoa.NSMakeRect(
                center_x - self.center_radius,
                center_y - self.center_radius,
                self.center_radius * 2,
                self.center_radius * 2
            )
        )
        Cocoa.NSColor.colorWithCalibratedRed_green_blue_alpha_(0.15, 0.15, 0.15, 0.9).setFill()
        center_path.fill()
        Cocoa.NSColor.colorWithCalibratedWhite_alpha_(0.9, 0.5).setStroke()
        center_path.setLineWidth_(1.5)
        center_path.stroke()

    def mouseMoved_(self, event):
        """Handle mouse movement for hover effect."""
        point = self.convertPoint_fromView_(event.locationInWindow(), None)
        self.updateHoveredIndex_(point)

    def mouseDown_(self, event):
        """Handle mouse click to select menu item."""
        point = self.convertPoint_fromView_(event.locationInWindow(), None)
        index = self.getSliceIndexAtPoint_(point)

        if index >= 0 and index < len(self.menu_items):
            item = self.menu_items[index]
            target = item['target']
            action = item['action']

            # Call the action
            if target and action:
                try:
                    # PyObjC automatically handles selector conversion
                    target.performSelector_withObject_(action, None)
                except Exception as e:
                    print(f"Error calling action {action}: {e}")

            # Close the menu by hiding it
            window = self.window()
            if window:
                window.orderOut_(None)

    def updateHoveredIndex_(self, point):
        """Update which slice is being hovered."""
        new_index = self.getSliceIndexAtPoint_(point)
        if new_index != self.hovered_index:
            self.hovered_index = new_index
            self.setNeedsDisplay_(True)

    def getSliceIndexAtPoint_(self, point):
        """
        Determine which pie slice contains the point.

        Args:
            point: NSPoint to check

        Returns:
            Index of the slice, or -1 if not in any slice
        """
        bounds = self.bounds()
        center_x = bounds.size.width / 2
        center_y = bounds.size.height / 2

        # Calculate distance from center
        dx = point.x - center_x
        dy = point.y - center_y
        distance = math.sqrt(dx * dx + dy * dy)

        # Check if outside the menu or in center circle
        if distance > self.radius or distance < self.center_radius:
            return -1

        # Calculate angle
        angle = math.atan2(dy, dx) + math.pi / 2
        if angle < 0:
            angle += 2 * math.pi

        # Determine which slice
        num_items = len(self.menu_items)
        angle_per_slice = 2 * math.pi / num_items
        index = int(angle / angle_per_slice)

        return index if index < num_items else -1

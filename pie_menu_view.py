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
        self.radius = 200  # Increased from 160 to accommodate icons
        self.center_radius = 35
        self.icon_cache = {}  # Cache loaded icons

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

            # Calculate position for icon and text
            mid_angle = start_angle + angle_per_slice / 2
            content_radius = self.radius * 0.65
            content_x = center_x + content_radius * math.cos(mid_angle)
            content_y = center_y + content_radius * math.sin(mid_angle)

            # Draw icon if available
            icon_size = 40
            if 'icon' in item and item['icon']:
                icon = self.loadIcon_(item['icon'])
                if icon:
                    icon_rect = Cocoa.NSMakeRect(
                        content_x - icon_size / 2,
                        content_y - icon_size / 2 + 15,  # Offset up from center
                        icon_size,
                        icon_size
                    )

                    # Save graphics state
                    Cocoa.NSGraphicsContext.currentContext().saveGraphicsState()

                    # Create rounded rectangle clipping path for icon
                    icon_corner_radius = 8  # Adjust this value for more/less rounding
                    icon_clip_path = Cocoa.NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
                        icon_rect,
                        icon_corner_radius,
                        icon_corner_radius
                    )
                    icon_clip_path.addClip()

                    # Draw the icon within the rounded rectangle
                    icon.drawInRect_fromRect_operation_fraction_(
                        icon_rect,
                        Cocoa.NSZeroRect,
                        Cocoa.NSCompositeSourceOver,
                        1.0
                    )

                    # Restore graphics state
                    Cocoa.NSGraphicsContext.currentContext().restoreGraphicsState()

            # Create text attributes
            attributes = {
                Cocoa.NSFontAttributeName: Cocoa.NSFont.systemFontOfSize_(11),
                Cocoa.NSForegroundColorAttributeName: Cocoa.NSColor.whiteColor()
            }

            # Draw the title below the icon
            title = Cocoa.NSString.stringWithString_(item['title'])
            text_size = title.sizeWithAttributes_(attributes)
            text_y_offset = -20 if 'icon' in item and item['icon'] else 0
            text_rect = Cocoa.NSMakeRect(
                content_x - text_size.width / 2,
                content_y - text_size.height / 2 + text_y_offset,
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

        # Draw handy logo in center
        from icon_helper import icon_path
        handy_icon_path = icon_path('handy.png')
        if handy_icon_path:
            handy_icon = self.loadIcon_(handy_icon_path)
            if handy_icon:
                # Make icon fill the center circle
                center_icon_size = self.center_radius * 1.9
                center_icon_rect = Cocoa.NSMakeRect(
                    center_x - center_icon_size / 2,
                    center_y - center_icon_size / 2,
                    center_icon_size,
                    center_icon_size
                )

                # Save graphics state
                Cocoa.NSGraphicsContext.currentContext().saveGraphicsState()

                # Clip to circle for rounded icon
                center_clip_path = Cocoa.NSBezierPath.bezierPathWithOvalInRect_(center_icon_rect)
                center_clip_path.addClip()

                # Draw the icon
                handy_icon.drawInRect_fromRect_operation_fraction_(
                    center_icon_rect,
                    Cocoa.NSZeroRect,
                    Cocoa.NSCompositeSourceOver,
                    1.0
                )

                # Restore graphics state
                Cocoa.NSGraphicsContext.currentContext().restoreGraphicsState()

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
                    # Check if this action needs an app_path parameter
                    if 'app_path' in item:
                        # Pass app path as a dictionary
                        target.performSelector_withObject_(action, {'path': item['app_path']})
                    else:
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
                # Resize to 40x40 if needed
                icon.setSize_(Cocoa.NSMakeSize(40, 40))
                self.icon_cache[icon_path] = icon
                return icon
        except Exception as e:
            print(f"Error loading icon {icon_path}: {e}")

        return None

"""
Left Menu View Module
Creates a vertical menu bar to the left of the pie menu for quick app access.
"""

import objc
import Cocoa


class LeftMenuView(Cocoa.NSView):
    """Custom view that draws a vertical menu bar with clickable buttons."""

    def initWithFrame_(self, frame):
        """Initialize the left menu view."""
        self = objc.super(LeftMenuView, self).initWithFrame_(frame)
        if self is None:
            return None

        self.menu_items = []
        self.hovered_index = -1
        self.tracking_area = None
        self.icon_cache = {}  # Cache loaded icons

        return self

    def updateTrackingAreas(self):
        """Set up mouse tracking for hover effects."""
        objc.super(LeftMenuView, self).updateTrackingAreas()

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
        objc.super(LeftMenuView, self).resetCursorRects()
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
        Draw the left menu as a vertical column.

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
        button_spacing = 6              # Space between buttons
        vertical_button_padding = 8     # Padding inside button (top and bottom)
        icon_text_spacing = 4           # Space between icon and text
        icon_size = 30                  # Icon size
        text_height = 12                # Approximate text height
        # ============================

        # Calculate button height based on content
        button_height = (vertical_button_padding * 2) + icon_size + icon_text_spacing + text_height
        button_width = bounds.size.width

        # Calculate total grid height
        total_grid_height = (num_items * button_height) + ((num_items - 1) * button_spacing)

        # Center the buttons vertically
        start_y = (bounds.size.height - total_grid_height) / 2

        # Draw each button vertically
        for i, item in enumerate(self.menu_items):
            y_offset = start_y + i * (button_height + button_spacing)

            button_rect = Cocoa.NSMakeRect(
                0,
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
                    icon_x = (button_width - icon_size) / 2
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

            # Draw text label below the icon
            paragraph_style = Cocoa.NSMutableParagraphStyle.alloc().init()
            paragraph_style.setAlignment_(Cocoa.NSTextAlignmentCenter)
            paragraph_style.setLineBreakMode_(Cocoa.NSLineBreakByWordWrapping)

            attributes = {
                Cocoa.NSFontAttributeName: Cocoa.NSFont.systemFontOfSize_(text_height),
                Cocoa.NSForegroundColorAttributeName: Cocoa.NSColor.whiteColor(),
                Cocoa.NSParagraphStyleAttributeName: paragraph_style
            }

            title = Cocoa.NSString.stringWithString_(item['title'])
            text_max_width = button_width - 4
            text_rect = Cocoa.NSMakeRect(
                2,
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

        # === Adjustable parameters (must match drawRect_) ===
        button_spacing = 4
        vertical_button_padding = 6
        icon_text_spacing = 4
        icon_size = 30
        text_height = 12
        # === End parameters ===

        # Calculate button dimensions
        total_height = bounds.size.height
        button_width = bounds.size.width
        button_height = (vertical_button_padding * 2) + icon_size + icon_text_spacing + text_height

        # Calculate vertical centering
        total_grid_height = (button_height * num_items) + (button_spacing * (num_items - 1))
        start_y = (bounds.size.height - total_grid_height) / 2

        # Check each button
        for i in range(num_items):
            y_offset = start_y + i * (button_height + button_spacing)

            if (point.x >= 0 and point.x <= button_width and
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
                # Resize to 30x30 for left menu
                icon.setSize_(Cocoa.NSMakeSize(30, 30))
                self.icon_cache[icon_path] = icon
                return icon
        except Exception as e:
            print(f"Error loading icon {icon_path}: {e}")

        return None

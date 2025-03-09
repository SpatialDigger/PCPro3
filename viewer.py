import open3d as o3d
import numpy as np
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon

class Open3DViewer:
    def __init__(self, logger=None, data=None):
        self.vis = o3d.visualization.Visualizer()
        self.window_width = 800
        self.window_height = 600
        # self.vis.create_window(window_name="3D View", width=self.window_width, height=self.window_height, visible=False)
        self.view_control = self.vis.get_view_control()
        self.items = {}
        self.logger = logger
        self.data = data
        self.visible_items = {}  # Track visible point clouds
        # self.render_option = self.vis.get_render_option()
        # self.render_option.background_color = [0.180, 0.180, 0.180]  # Dark gray
        self.axis_visible = False  # Flag to track visibility of the axis
        self.xyz_axis = None  # Will store the XYZ axis geometry
        self.bounding_box_visible = False
        self.bounding_box = None
        self.oriented_bounding_box_visible = False
        self.oriented_bounding_box = None

        self.labels_visible = False
        self.labels = None

    def show_window(self):
        """Shows the Open3D window."""
        self.vis.create_window(window_name="3D View", width=self.window_width, height=self.window_height, visible=True)
        self.render_option = self.vis.get_render_option()
        self.render_option.background_color = [0.180, 0.180, 0.180]  # Dark gray
        # print("Open3D window is now visible.")

    def update_background_color(self, color):
        """Update the background color of the Open3D viewer."""
        if len(color) == 3:
            self.render_option.background_color = color
            print(f"Background color updated to: {color}")
        else:
            print("Invalid background color.")

    def log_message(self, message):
        if self.logger:
            self.logger(message)

    def add_item(self, item, parent_name, child_name):
        """Add geometry to the viewer and track it uniquely."""
        if not self.is_geometry(item):  # Skip invalid geometries
            self.log_message(f"Skipped adding non-geometry '{child_name}' under '{parent_name}'.")
            return

        key = (parent_name, child_name)
        if key not in self.items:
            if self.visible_items.get(key, True):  # Only add if marked visible
                self.vis.add_geometry(item)
                self.items[key] = item
                self.visible_items[key] = True  # Default to visible
        else:
            self.log_message(f"Item '{child_name}' under '{parent_name}' already exists.")

    def remove_item(self, parent_name, child_name=None):
        """Remove an item (or all items under a parent) from the viewer."""
        if child_name is None:
            # Remove all items under the parent
            keys_to_remove = [key for key in self.items if key[0] == parent_name]
        else:
            # Remove specific child item
            keys_to_remove = [(parent_name, child_name)]

        for key in keys_to_remove:
            if key in self.items:
                item = self.items[key]
                if self.visible_items.get(key, False):  # Only remove if visible
                    print(f"Removing {key} from the viewer")  # Debugging line
                    self.vis.remove_geometry(item)
                del self.items[key]
                del self.visible_items[key]
                self.log_message(f"Removed item '{key[1]}' under parent '{key[0]}' from viewer.")
            else:
                self.log_message(f"Item '{key[1]}' under '{key[0]}' not found in viewer.")

        # Refresh the viewer after removal
        self.update_viewer()

    def toggle_item_visibility(self, parent_name, child_name, is_visible):
        """Toggle the visibility of the geometry."""
        key = (parent_name, child_name)

        if key in self.items:
            item = self.items[key]

            if is_visible:
                # Add geometry back if not already visible
                if not self.visible_items.get(key, False):
                    self.vis.add_geometry(item)
            else:
                # Remove geometry if currently visible
                if self.visible_items.get(key, False):
                    self.vis.remove_geometry(item)

            # Update visibility state
            self.visible_items[key] = is_visible
            self.log_message(
                f"Visibility toggled for {child_name} under {parent_name}: {'Visible' if is_visible else 'Hidden'}")

            # Refresh the viewer
            self.update_viewer()
            print(self.visible_items)

    def update_viewer(self):
        """Update the Open3D viewer."""
        self.vis.poll_events()
        self.vis.update_renderer()

    def is_geometry(self, obj):
        """Check if the object is a valid Open3D geometry."""
        return isinstance(obj, (
            o3d.geometry.PointCloud,
            o3d.geometry.TriangleMesh,
            o3d.geometry.LineSet,
            o3d.geometry.AxisAlignedBoundingBox,
            o3d.geometry.OrientedBoundingBox
        ))

    def toggle_xyz_axis_visibility(self):
        """Toggle the visibility of the XYZ axis."""
        if self.items:
            if self.axis_visible:
                # Remove the XYZ axis if it exists
                self.vis.remove_geometry(self.xyz_axis)
            else:
                # Add the XYZ axis in relation to the bounding box of visible items
                self.add_xyz_axis()
            self.axis_visible = not self.axis_visible
            self.update_viewer()
        else:
            pass

    def toggle_bounding_box_visibility(self):
        """Toggle the visibility of the bounding box."""
        if self.bounding_box_visible:
            # Remove the bounding box if it exists
            self.vis.remove_geometry(self.bounding_box)
        else:
            # Add the bounding box in relation to the bounding box of visible items
            self.add_bounding_box()
        self.bounding_box_visible = not self.bounding_box_visible
        self.update_viewer()

    def toggle_oriented_bounding_box_visibility(self):
        """Toggle the visibility of the bounding box."""
        if self.oriented_bounding_box_visible:
            # Remove the bounding box if it exists
            self.vis.remove_geometry(self.oriented_bounding_box)
        else:
            # Add the bounding box in relation to the bounding box of visible items
            self.add_oriented_bounding_box()
        self.oriented_bounding_box_visible = not self.oriented_bounding_box_visible
        self.update_viewer()

    def toggle_labels(self):
        """Toggle the visibility of the bounding box."""
        if self.labels_visible:
            # Remove the bounding box if it exists
            self.vis.remove_geometry(self.labels)
        else:
            # Add the bounding box in relation to the bounding box of visible items
            self.add_labels()
        self.labels_visible = not self.labels_visible
        self.update_viewer()

    def add_xyz_axis(self):
        """Create and add the XYZ axis relative to the bounding box of visible items."""
        # Calculate the bounding box that encompasses all visible items
        bounding_box = self.calculate_bounding_box()

        # If no items are visible, place the axis at the origin
        if bounding_box is None:
            position = [0, 0, 0]  # Default to origin if no geometry
        else:
            # Position the axis at the center of the bounding box
            position = bounding_box.get_center()

        # Colors: Red (X), Green (Y), Blue (Z)
        lines = [
            [0, 1],  # X axis
            [0, 2],  # Y axis
            [0, 3],  # Z axis
        ]
        colors = [
            [1, 0, 0],  # Red
            [0, 1, 0],  # Green
            [0, 0, 1],  # Blue
        ]

        # Create a LineSet for the axes
        axis_lines = o3d.geometry.LineSet()
        axis_lines.points = o3d.utility.Vector3dVector([
            position,  # Position at the center of the bounding box or origin
            [1, 0, 0] + position,  # X
            [0, 1, 0] + position,  # Y
            [0, 0, 1] + position,  # Z
        ])
        axis_lines.lines = o3d.utility.Vector2iVector(lines)
        axis_lines.colors = o3d.utility.Vector3dVector(colors)

        # Add the axis to the viewer
        self.vis.add_geometry(axis_lines)
        self.xyz_axis = axis_lines

    def add_bounding_box(self):
        """Create and add the bounding box around the visible items."""
        # Calculate the bounding box that encompasses all visible items
        bounding_box = self.calculate_bounding_box()

        if bounding_box:
            # Add the bounding box to the viewer
            self.vis.add_geometry(bounding_box)
            self.bounding_box = bounding_box

    def add_oriented_bounding_box(self):
        """Create and add the bounding box around the visible items."""
        # Calculate the bounding box that encompasses all visible items
        oriented_bounding_box = self.calculate_oriented_bounding_box()

        if oriented_bounding_box:
            # Add the bounding box to the viewer
            self.vis.add_geometry(oriented_bounding_box)
            self.oriented_bounding_box = oriented_bounding_box



    # def calculate_bounding_box(self):
    #     """Calculate the bounding box that encompasses all visible items."""
    #     all_bounding_boxes = []
    #
    #     for key, item in self.items.items():
    #         if self.visible_items.get(key, False):  # Only consider visible items
    #             if isinstance(item, o3d.geometry.PointCloud):
    #                 all_bounding_boxes.append(item.get_axis_aligned_bounding_box())
    #             elif isinstance(item, o3d.geometry.TriangleMesh):
    #                 all_bounding_boxes.append(item.get_axis_aligned_bounding_box())
    #             # Add more geometry types if necessary
    #
    #     if not all_bounding_boxes:
    #         return None  # No visible items to calculate a bounding box from
    #
    #     # Combine all the bounding boxes to find the encompassing box
    #     combined_bounding_box = all_bounding_boxes[0]
    #     for bbox in all_bounding_boxes[1:]:
    #         combined_bounding_box = combined_bounding_box.create_union(bbox)
    #
    #     return combined_bounding_box

    import open3d as o3d

    import open3d as o3d
    import numpy as np

    def add_labels(self, step=0.5):
        """
        Adds 3D labels to the bounding box.
        :param step: The step size between the labels
        """
        bounding_box = self.calculate_bounding_box()

        # Get bounding box min and max coordinates
        min_bound = np.array(bounding_box.min_bound)
        max_bound = np.array(bounding_box.max_bound)

        # Create labels (text) for each axis (X, Y, Z)
        tick_labels = []

        # Generate labels for each axis (X, Y, Z)
        for axis in range(3):
            axis_start = min_bound[axis]  # + self.translation[axis]
            axis_end = max_bound[axis]  # + self.translation[axis]

            # Generate labels along this axis (using `step` interval)
            for i in np.arange(axis_start, axis_end, step):
                tick_labels.append(f"{i:.2f}")

        # Add labels to Open3D viewer using Label3D from gui module
        for idx, label_text in enumerate(tick_labels):
            # Calculate the position for each label (just offset slightly on one axis)
            if idx < len(tick_labels) // 3:  # X-axis labels
                position = np.array([float(tick_labels[idx]), 0, 0], dtype=np.float32)
            elif idx < 2 * len(tick_labels) // 3:  # Y-axis labels
                position = np.array([0, float(tick_labels[idx]), 0], dtype=np.float32)
            else:  # Z-axis labels
                position = np.array([0, 0, float(tick_labels[idx])], dtype=np.float32)

            # Create the 3D Label
            label = o3d.visualization.gui.Label3D(label_text, position)

            # Customize the label's properties if needed
            label.color = o3d.visualization.gui.Color(1.0, 1.0, 1.0)  # White color
            label.scale = 1.0  # Scale factor for text size

            # Add the label to the GUI viewer
            self.vis.add_3d_label(label)

    def calculate_bounding_box(self):
        """Calculate the bounding box that encompasses all visible items."""
        all_points = []  # Collect all bounding box corner points

        for key, item in self.items.items():
            if self.visible_items.get(key, False):  # Only consider visible items
                if isinstance(item, (o3d.geometry.PointCloud, o3d.geometry.TriangleMesh)):
                    bbox = item.get_axis_aligned_bounding_box()
                    all_points.append(bbox.get_box_points())

        if not all_points:
            return None  # No visible items to calculate a bounding box from

        # Flatten the list of points
        all_points = np.vstack(all_points)

        # Create a new bounding box that encompasses all points
        combined_bounding_box = o3d.geometry.AxisAlignedBoundingBox.create_from_points(
            o3d.utility.Vector3dVector(all_points)
        )

        return combined_bounding_box

    def calculate_oriented_bounding_box(self):
        """Calculate the Oriented Bounding Box (OBB) that encompasses all visible items."""
        all_points = []  # Collect all geometry points for OBB

        for key, item in self.items.items():
            if self.visible_items.get(key, False):  # Only consider visible items
                if isinstance(item, (o3d.geometry.PointCloud, o3d.geometry.TriangleMesh)):
                    bbox_obb = item.get_oriented_bounding_box()
                    all_points.append(bbox_obb.get_box_points())  # Store corner points for OBB

        if not all_points:
            return None  # No visible items, return None

        # Flatten the list of points
        all_points = np.vstack(all_points)

        # Create OBB: Rotates with objects for a tighter fit
        combined_obb = o3d.geometry.OrientedBoundingBox.create_from_points(
            o3d.utility.Vector3dVector(all_points)
        )
        combined_obb.color = (0, 1, 0)  # Green for OBB

        return combined_obb
    def close(self):
        """Close the Open3D viewer window."""
        self.vis.destroy_window()

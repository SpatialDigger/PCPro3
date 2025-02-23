import open3d as o3d
from pprint import pprint
class Open3DViewer:
    def __init__(self, logger=None, data=None):
        self.vis = o3d.visualization.Visualizer()
        # self.vis = o3d.visualization.VisualizerWithEditing()
        self.window_width = 800
        self.window_height = 600
        self.vis.create_window(width=self.window_width, height=self.window_height)
        self.view_control = self.vis.get_view_control()
        self.items = {}
        self.logger = logger
        self.data = data
        self.visible_items = {}  # Track visible point clouds

        self.render_option = self.vis.get_render_option()


        # Add RGB XYZ axis during initialization
        # axis = self.create_axis(length=1.0)  # Adjust axis length if needed
        # self.add_item(axis, parent_name="Viewer", child_name="XYZ_Axis")


    # def create_axis(self, length=1.0):
    #     """
    #     Create an RGB-colored XYZ axis visualization in Open3D.
    #     Args:
    #         length (float): Length of the axes.
    #     Returns:
    #         o3d.geometry.LineSet: Axis representation as a LineSet.
    #     """
    #     # Points for the origin and the tips of the axes
    #     points = [
    #         [0, 0, 0],  # Origin
    #         [length, 0, 0],  # X-axis tip
    #         [0, length, 0],  # Y-axis tip
    #         [0, 0, length],  # Z-axis tip
    #     ]
    #
    #     # Lines connecting the origin to the tips of the axes
    #     lines = [
    #         [0, 1],  # X-axis
    #         [0, 2],  # Y-axis
    #         [0, 3],  # Z-axis
    #     ]
    #
    #     # RGB colors for the axes
    #     colors = [
    #         [1, 0, 0],  # Red for X-axis
    #         [0, 1, 0],  # Green for Y-axis
    #         [0, 0, 1],  # Blue for Z-axis
    #     ]
    #
    #     # Create the LineSet object
    #     axis = o3d.geometry.LineSet()
    #     axis.points = o3d.utility.Vector3dVector(points)
    #     axis.lines = o3d.utility.Vector2iVector(lines)
    #     axis.colors = o3d.utility.Vector3dVector(colors)
    #
    #     return axis
    #
    # def initialize_axis(self):
    #     """Add the XYZ axis to the viewer after initialization."""
    #     print('Axis selected')
    #     axis = Open3DViewer.create_axis(length=1.0)  # Adjust axis length if needed
    #     self.add_item(axis, parent_name="Viewer", child_name="XYZ_Axis")



    def update_point_cloud_color(self, parent_name, color_rgb):
        if parent_name not in self.data or "Pointcloud" not in self.data[parent_name]:
            self.logger(f"Parent {parent_name} not found or missing 'Pointcloud' key.")
            return

        point_cloud = self.data[parent_name]["Pointcloud"]
        num_points = len(point_cloud.points)

        # Ensure point cloud colors are consistent
        if not hasattr(point_cloud, "colors") or len(point_cloud.colors) != num_points:
            self.logger(f"Point cloud for {parent_name} missing or has invalid 'colors'. Reinitializing colors.")
            point_cloud.colors = o3d.utility.Vector3dVector([color_rgb] * num_points)
        else:
            self.logger(f"Applying new color {color_rgb} to point cloud {parent_name}.")
            point_cloud.colors = o3d.utility.Vector3dVector([color_rgb] * num_points)

        # Attempt to refresh the viewer
        try:
            # self.update_viewer_state()
            self.update_viewer()

            self.logger(f"Successfully refreshed the viewer after color change for {parent_name}.")
        except Exception as e:
            self.logger(f"Error refreshing viewer: {str(e)}")

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
            # added
            pprint(self.visible_items)

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
            o3d.geometry.AxisAlignedBoundingBox,  # Include AABB
            o3d.geometry.OrientedBoundingBox  # Include OBB if necessary
        ))

    def stateupdate_viewer_(self):
        """Ensures the Open3D viewer reflects the current state of self.data,
        using self.visible_items to track visibility."""
        print("Updating viewer state...")  # Debugging line

        # Remove geometries that are no longer visible
        for key, item in self.items.items():
            if self.visible_items.get(key, False) is False:  # Only remove if it's no longer visible
                print(f"Removing {key} from the viewer")  # Debugging line
                self.vis.remove_geometry(item)
                del self.items[key]
                del self.visible_items[key]

        # Add geometries that are visible or newly added
        for (parent_name, child_name), is_visible in self.visible_items.items():
            if not is_visible:
                continue  # Skip non-visible items

            # Fetch the geometry from self.data
            if parent_name in self.data and child_name in self.data[parent_name]:
                geometry = self.data[parent_name][child_name]

                if self.is_geometry(geometry):  # Add only valid geometries
                    self.log_message(
                        f"Attempting to add item of type {type(item).__name__} for '{child_name}' under '{parent_name}'.")
                    self.add_item(geometry, parent_name, child_name)
                else:
                    self.log_message(f"Skipped non-geometry item '{child_name}' under '{parent_name}'.")

        # Refresh the viewer
        self.update_viewer()
        self.log_message("Viewer state updated to reflect current data and visibility.")

    def close(self):
        """Close the Open3D viewer window."""
        self.vis.destroy_window()
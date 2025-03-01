import open3d as o3d
from pprint import pprint

class Open3DViewer:
    def __init__(self, logger=None, data=None):
        self.vis = o3d.visualization.Visualizer()
        # self.vis = o3d.visualization.VisualizerWithEditing()
        self.window_width = 800
        self.window_height = 600
        self.vis.create_window(window_name="3D View", width=self.window_width, height=self.window_height)
        self.view_control = self.vis.get_view_control()
        self.items = {}
        self.logger = logger
        self.data = data
        self.visible_items = {}  # Track visible point clouds

        self.render_option = self.vis.get_render_option()

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

    def update_point_cloud_color(self, parent_name, new_color_rgb):
        """Update the color of a point cloud in the viewer."""
        key = (parent_name, "Pointcloud")

        if key not in self.items:
            self.log_message(f"Point cloud '{parent_name}' not found in viewer.")
            return

        point_cloud = self.items[key]

        # Ensure the number of colors matches the number of points
        num_points = len(point_cloud.points)
        if num_points == 0:
            self.log_message(f"Point cloud '{parent_name}' has no points.")
            return

        point_cloud.colors = o3d.utility.Vector3dVector([new_color_rgb] * num_points)

        # Remove and re-add the geometry to force an update
        self.vis.remove_geometry(point_cloud)
        self.vis.add_geometry(point_cloud)

        # Refresh the viewer
        self.update_viewer()

        self.log_message(f"Updated color of '{parent_name}' to {new_color_rgb}.")

    def close(self):
        """Close the Open3D viewer window."""
        self.vis.destroy_window()
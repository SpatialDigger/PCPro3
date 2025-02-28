import os
import sys
import time
import warnings
import numpy as np
import laspy
import open3d as o3d

from pprint import pformat
from sklearn.cluster import DBSCAN
from shapely.geometry import Point, Polygon, MultiLineString, LineString
from shapely.ops import unary_union
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTreeWidget, QAbstractItemView,
    QApplication, QAction, QMenu,
    QFileDialog, QColorDialog, QTreeWidgetItem, QDialog, QAction
)
from PyQt5.QtCore import Qt, QTimer, QPoint, QUrl
from viewer import Open3DViewer
from dialogs_pyqt5 import (
    LogWindow, PropertiesDialog, TransformationDialog, DBSCANDialog,
)
from PyQt5.QtCore import  QUrl



from tools import (
    convexhull3d, filter_points_by_distance, sampling,
    merge_items, boundingbox3d, poisson_surface_reconstruction,
    substitute_points
)
# from normals import ball_pivoting_triangulation
from normals import(
    compute_normals, invert_normals)

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pointcloud Processor")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Dataset"])

        # Set multi-selection mode
        self.tree.setSelectionMode(QAbstractItemView.MultiSelection)

        self.tree.itemChanged.connect(self.on_item_changed)
        layout.addWidget(self.tree)

        self.data = {}
        self.original_colors = {}

        self.o3d_viewer = Open3DViewer(logger=self.add_log_message, data=self.data)
        self.log_window = LogWindow(self)

        self.create_menu_bar()

        self.viewer_update_timer = QTimer()
        self.viewer_update_timer.timeout.connect(self.o3d_viewer.update_viewer)
        self.viewer_update_timer.start(16)

        self.translation_values = {'x': 0, 'y': 0, 'z': 0}

        # Connect context menu policy for right-click
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

        self.coordinate_frame_visible = False  # Track visibility

        # Meta data storage
        self.metadata = {}
        self.original_colors = {}

    def show_context_menu(self, position: QPoint):
        """Display a context menu at the right-click position with options tailored to the selected item."""
        item = self.tree.itemAt(position)

        if item:
            menu = QMenu(self)
            parent_item = item.parent()

            # Common Option: Remove Item
            action_remove = QAction("Remove", self)
            action_remove.setToolTip("Remove this item from the workspace")
            action_remove.triggered.connect(lambda: self.delete_item(item, is_child=bool(parent_item)))
            menu.addAction(action_remove)

            # Show Properties
            properties_action = QAction("Properties", self)
            properties_action.setToolTip("Show properties of this item")
            properties_action.triggered.connect(lambda: self.show_properties(item))
            menu.addAction(properties_action)

            # Color Management
            change_color_action = QAction("Change Color", self)
            change_color_action.setToolTip("Change the color of this point cloud")
            change_color_action.triggered.connect(lambda: self.change_point_cloud_color(item))
            menu.addAction(change_color_action)

            # Add "Revert to Original Color" only if the color has been changed (stored in self.original_colors)
            # if item.text(0) in self.original_colors:
            revert_color_action = QAction("Revert to Original Color", self)
            revert_color_action.setToolTip("Revert the point cloud to its original color")
            revert_color_action.triggered.connect(lambda: self.revert_point_cloud_color(item))
            menu.addAction(revert_color_action)

            if parent_item:
                action_export = QAction("Export", self)
                action_export.setToolTip("Export this item to a file")
                action_export.triggered.connect(lambda: self.export_item(item))
                menu.addAction(action_export)

            else:  # Parent item-specific options
                action_rename = QAction("Rename", self)
                action_rename.setToolTip("Rename this item")
                action_rename.triggered.connect(lambda: self.start_rename(item))
                menu.addAction(action_rename)

            menu.exec(self.tree.viewport().mapToGlobal(position))

    def export_item(self, item):
        """Export the selected item (child object) to a user-specified format."""
        parent_item = item.parent()
        if not parent_item:
            self.add_log_message("Export is only supported for child items.")
            return

        parent_name = parent_item.text(0)
        child_name = item.text(0)

        if parent_name not in self.data or child_name not in self.data[parent_name]:
            self.add_log_message(f"Export failed: Could not locate data for '{child_name}' under '{parent_name}'.")
            return

        # Get the object to export
        obj = self.data[parent_name][child_name]
        if  isinstance(obj, o3d.geometry.PointCloud):
            # Open file dialog for export
            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setNameFilters([
                "PCD Files (*.pcd)",
                "LAS Files (*.las)",
                "XYZ Files (*.xyz)",
                "PLY Files (*.ply)",
                # "GeoJSON Files (*.geojson)",
            ])
            if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
                export_path = file_dialog.selectedFiles()[0]
                self.perform_export(obj, export_path)
        elif  isinstance(obj, o3d.geometry.TriangleMesh):
            # Open file dialog for export
            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setNameFilters([
                # "PCD Files (*.pcd)",
                # "LAS Files (*.las)",
                # "XYZ Files (*.xyz)",
                "PLY Files (*.ply)",
                # "GeoJSON Files (*.geojson)",
            ])
            if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
                export_path = file_dialog.selectedFiles()[0]
                self.perform_export(obj, export_path)

    def perform_export(self, item, file_path):
        """Perform the export of the Open3D point cloud to the specified file format."""
        file_format = file_path.split('.')[-1].lower()

        try:
            if file_format == "pcd":
                o3d.io.write_point_cloud(file_path, item, write_ascii=True)
            elif file_format == "las":
                self.export_to_las(item, file_path)
            elif file_format == "xyz":
                o3d.io.write_point_cloud(file_path, item, write_ascii=True)
            elif file_format == "ply":
                if isinstance(item, o3d.geometry.PointCloud):
                    o3d.io.write_point_cloud(file_path, item, write_ascii=True)
                    print(f"PointCloud saved to {file_path}")
                elif isinstance(item, o3d.geometry.TriangleMesh):
                    o3d.io.write_triangle_mesh(file_path, item, write_ascii=True)
                    print(f"Mesh saved to {file_path}")
            elif file_format == "geojson":
                self.export_to_geojson(item, file_path)
            else:
                self.add_log_message(f"Unsupported export format: {file_format}")
                return

            self.add_log_message(f"Exported point cloud to {file_path}.")
        except Exception as e:
            self.add_log_message(f"Export failed: {str(e)}")

    def export_to_las(self, point_cloud, file_path):
        """Export an Open3D point cloud to LAS format."""
        points = np.asarray(point_cloud.points)
        colors = np.asarray(point_cloud.colors)

        # Create a LAS file
        header = laspy.LasHeader(point_format=3, version="1.4")
        las = laspy.LasData(header)

        # Assign points
        las.x, las.y, las.z = points[:, 0], points[:, 1], points[:, 2]

        if colors.size > 0:
            # Convert from [0,1] to [0,65535] and cast to uint16
            las.red = (colors[:, 0] * 65535).astype(np.uint16)
            las.green = (colors[:, 1] * 65535).astype(np.uint16)
            las.blue = (colors[:, 2] * 65535).astype(np.uint16)

        las.write(file_path)

    def export_to_geojson(self, point_cloud, file_path):
        """Export an Open3D point cloud to GeoJSON format."""
        import json

        points = np.asarray(point_cloud.points)
        geojson_data = {
            "type": "FeatureCollection",
            "features": []
        }

        for point in points:
            geojson_data["features"].append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": point.tolist()  # GeoJSON expects [longitude, latitude, altitude]
                }
            })

        with open(file_path, 'w') as f:
            json.dump(geojson_data, f, indent=4)

    def change_point_cloud_color(self, item):
        """Change the color of a point cloud."""
        parent_item = item.parent()
        if not parent_item:
            self.add_log_message("No parent item found.")
            return

        parent_name = parent_item.text(0)
        child_name = item.text(0)

        color = QColorDialog.getColor()
        if not color.isValid():
            self.add_log_message("Invalid color selected.")
            return

        # Convert QColor to Open3D format (normalized)
        red, green, blue = color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0
        new_color = [red, green, blue]

        # Retrieve the point cloud
        key = (parent_name, child_name)
        if key in self.o3d_viewer.items:
            point_cloud = self.o3d_viewer.items[key]

            num_points = len(point_cloud.points)
            if num_points == 0:
                self.add_log_message(f"Point cloud '{child_name}' under '{parent_name}' has no points.")
                return

            # **Store the original colors using (parent_name, child_name)**
            if key not in self.original_colors:
                original_colors = np.asarray(point_cloud.colors)  # Convert to NumPy array
                if original_colors.size > 0:
                    self.original_colors[key] = original_colors.copy()  # Store a copy
                else:
                    self.original_colors[key] = np.ones((num_points, 3))  # Default to white

            # Apply new color to all points
            point_cloud.colors = o3d.utility.Vector3dVector(np.tile(new_color, (num_points, 1)))

            # Remove and re-add the geometry to force an update
            self.o3d_viewer.vis.remove_geometry(point_cloud)
            self.o3d_viewer.vis.add_geometry(point_cloud)

            # Refresh viewer
            self.o3d_viewer.update_viewer()
            self.add_log_message(f"Color of '{child_name}' under '{parent_name}' changed to {new_color}.")
        else:
            self.add_log_message(f"Point cloud for '{child_name}' under '{parent_name}' not found.")

    def revert_point_cloud_color(self, item):
        """Revert the point cloud to its original color."""
        self.add_log_message("Revert color action triggered.")

        if not item:
            self.add_log_message("No item selected to revert color.")
            return

        child_name = item.text(0)
        parent_item = item.parent()
        if not parent_item:
            self.add_log_message(f"'{child_name}' does not have a parent item.")
            return

        parent_name = parent_item.text(0)
        key = (parent_name, child_name)  # Ensure we use the correct key

        # Check if original colors exist
        if key not in self.original_colors:
            self.add_log_message(f"No original color found for '{child_name}' under '{parent_name}'.")
            return

        # Retrieve the point cloud
        if key in self.o3d_viewer.items:
            point_cloud = self.o3d_viewer.items[key]

            # Restore original per-point colors
            original_colors = self.original_colors[key]  # Use the correct key
            point_cloud.colors = o3d.utility.Vector3dVector(original_colors)

            # Remove and re-add the geometry to update Open3D viewer
            self.o3d_viewer.vis.remove_geometry(point_cloud)
            self.o3d_viewer.vis.add_geometry(point_cloud)

            # Refresh viewer
            self.o3d_viewer.update_viewer()
            self.add_log_message(f"Color of '{child_name}' under '{parent_name}' reverted to original.")
        else:
            self.add_log_message(f"Point cloud for '{child_name}' under '{parent_name}' not found.")

    def add_pointcloud(self, file_path, transform_settings=None):
        """Handles importing a point cloud and adding it to the tree and data dictionary."""
        try:
            # Import the point cloud data
            data = self.import_pointcloud(file_path, transform_settings)
            file_name = data["file_name"]

            # Add the point cloud as a child under the file name
            self.add_child_to_tree_and_data(
                parent_name=file_name,
                child_name="Pointcloud",
                data=data["Pointcloud"]
            )

            # Store additional metadata in the parent data dictionary
            self.data[file_name].update({
                "transform_settings": self.translation_values,
                "file_path": file_path,
                "file_name": file_name,
            })

            self.add_log_message(f"Point cloud successfully added for file '{file_name}'.")
        except Exception as e:
            self.add_log_message(f"Failed to add point cloud: {str(e)}")

    def create_axis(self, length=1.0):
        """
        Create an RGB-colored XYZ axis visualization in Open3D.
        Args:
            length (float): Length of the axes.
        Returns:
            o3d.geometry.LineSet: Axis representation as a LineSet.
        """
        import numpy as np

        # Points for the origin and the tips of the axes
        points = np.array([
            [0, 0, 0],  # Origin
            [length, 0, 0],  # X-axis tip
            [0, length, 0],  # Y-axis tip
            [0, 0, length],  # Z-axis tip
        ], dtype=np.float64)

        # Lines connecting the origin to the tips of the axes
        lines = np.array([
            [0, 1],  # Line for X-axis
            [0, 2],  # Line for Y-axis
            [0, 3],  # Line for Z-axis
        ], dtype=np.int32)

        # RGB colors for the lines (one per line)
        colors = np.array([
            [1, 0, 0],  # Red for X-axis
            [0, 1, 0],  # Green for Y-axis
            [0, 0, 1],  # Blue for Z-axis
        ], dtype=np.float64)

        # Create the LineSet object
        axis = o3d.geometry.LineSet()
        axis.points = o3d.utility.Vector3dVector(points)
        axis.lines = o3d.utility.Vector2iVector(lines)
        axis.colors = o3d.utility.Vector3dVector(colors)

        return axis

    def add_axis(self, length=1.0):
        """Handles importing a point cloud and adding it to the tree and data dictionary."""
        try:
            axis = self.create_axis()

            # Add the point cloud as a child under the file name
            self.add_child_to_tree_and_data(
                parent_name="Display",
                child_name="xyz-axis",
                data=axis
            )

            self.add_log_message(f"Axis added to display.")
        except Exception as e:
            self.add_log_message(f"Failed to add point cloud: {str(e)}")


    def show_properties(self, item):
        """
        Display a properties dialog for the given item, showing either its specific data
        or a list of its children if the item is a parent.
        """
        item_text = item.text(0)  # Get the text of the right-clicked item
        parent_item = item.parent()

        if parent_item:
            # If the item is a child, get the parent and child data
            parent_name = parent_item.text(0)
            child_name = item_text

            if parent_name in self.data and child_name in self.data[parent_name]:
                data = {
                    'item': self.data[parent_name][child_name],  # Show child data
                    'filename': self.data[parent_name]['file_name'],
                    'filepath': self.data[parent_name]['file_path'],
                    'transform_settings': self.translation_values,
                }
            else:
                self.add_log_message(f"No data found for child item '{child_name}' under parent '{parent_name}'.")
                return
        else:
            # If the item is a parent, get its data
            parent_name = item_text

            if parent_name in self.data:
                data = self.data[parent_name]  # Show parent data
            else:
                self.add_log_message(f"No data found for parent item '{parent_name}'.")
                return

        # Show properties dialog for the selected data (either parent or child)
        properties_dialog = PropertiesDialog(data, self)
        properties_dialog.exec()

    def selected_items(self):
        """
        Returns selected items from the tree, sorted by depth (children first).
        Filters out invalid or redundant items.
        """
        selected_items = self.tree.selectedItems()
        if not selected_items:
            self.add_log_message("No items selected for filtering.")
            return []

        def get_depth(item):
            """Helper function to calculate the depth of a tree item."""
            depth = 0
            while item.parent():
                item = item.parent()
                depth += 1
            return depth

        # Sort selected items by depth (children processed before parents)
        sorted_items = sorted(selected_items, key=get_depth, reverse=True)

        # Filter out invalid items (items not present in self.data)
        valid_items = []
        for item in sorted_items:
            parent_item = item.parent()
            if parent_item:
                parent_name = parent_item.text(0)
                child_name = item.text(0)
                if parent_name in self.data and child_name in self.data[parent_name]:
                    valid_items.append(item)
                else:
                    self.add_log_message(
                        f"Skipping invalid child item '{child_name}' under parent '{parent_name}'."
                    )
            else:
                parent_name = item.text(0)
                if parent_name in self.data:
                    valid_items.append(item)
                else:
                    self.add_log_message(f"Skipping invalid parent item '{parent_name}'.")

        return valid_items

    def remove_selected_items(self):
        """Removes selected items from the tree, data dictionary, and Open3D viewer."""
        selected_items = self.selected_items()
        if not selected_items:
            self.add_log_message("No items selected for removal.")
            return

        # Process selected items
        processed_parents = set()
        for item in selected_items:
            parent_item = item.parent()
            if parent_item:
                # Handle child item
                parent_name = parent_item.text(0)
                child_name = item.text(0)

                self.add_log_message(f"Removing child '{child_name}' under parent '{parent_name}'.")
                self.remove_from_tree_and_data(parent_name, child_name)

            else:
                # Handle parent item
                parent_name = item.text(0)
                if parent_name not in processed_parents:
                    self.add_log_message(f"Removing parent '{parent_name}' and all its children.")
                    self.remove_from_tree_and_data(parent_name)
                    processed_parents.add(parent_name)

    def add_child_to_tree_and_data(self, parent_name, child_name, data):
        """Handles adding both parent and child items to the tree and updating the data dictionary."""
        # Check if the parent item exists in the tree; create it if not
        parent_item = self._find_tree_item(parent_name)
        if not parent_item:
            # Create the parent item
            parent_item = QTreeWidgetItem([parent_name])
            parent_item.setFlags(parent_item.flags() | Qt.ItemIsUserCheckable)
            parent_item.setCheckState(0, Qt.Checked)  # Changed to Qt.Checked for PyQt5
            self.tree.addTopLevelItem(parent_item)
            self.tree.expandItem(parent_item)

            self.add_log_message(f"add_child_to_tree_and_data: Created new parent item '{parent_name}' in tree.")

        # Check if the parent exists in the data dictionary; create it if not
        if parent_name not in self.data:
            self.data[parent_name] = {}
            self.add_log_message(f"add_child_to_tree_and_data: Created new parent '{parent_name}' in data dictionary.")

        # Add the child item to the parent in the tree
        child_item = QTreeWidgetItem([child_name])
        child_item.setCheckState(0, Qt.Checked)  # Initialize checkbox as checked
        child_item.setFlags(child_item.flags() | Qt.ItemIsUserCheckable)
        parent_item.addChild(child_item)
        self.tree.expandItem(parent_item)

        self.add_log_message(
            f"add_child_to_tree_and_data: Adding child '{child_name}' under parent '{parent_name}' in tree.")

        # Add the child data to the dictionary under the parent
        self.data[parent_name][child_name] = data

        # Ensure the point cloud is added to the Open3D viewer
        self.o3d_viewer.add_item(data, parent_name, child_name)
        self.add_log_message(f"add_child_to_tree_and_data: '{child_name}' added to Open3D viewer.")

    def remove_from_tree_and_data(self, parent_name, child_name=None):
        if parent_name not in self.data:
            self.add_log_message(f"Parent '{parent_name}' not found in data.")
            return

        if child_name is None:
            # Remove parent and all its children
            del self.data[parent_name]
            parent_item = self._find_tree_item(parent_name)
            if parent_item:
                index = self.tree.indexOfTopLevelItem(parent_item)
                if index != -1:
                    self.tree.takeTopLevelItem(index)
            self.o3d_viewer.remove_item(parent_name)
            self.add_log_message(f"Removed parent '{parent_name}' and its children.")
        else:
            # Remove only the child
            if child_name in self.data[parent_name]:
                del self.data[parent_name][child_name]
                parent_item = self._find_tree_item(parent_name)
                if parent_item:
                    for i in range(parent_item.childCount()):
                        child_item = parent_item.child(i)
                        if child_item.text(0) == child_name:
                            parent_item.removeChild(child_item)
                            break
                self.o3d_viewer.remove_item(parent_name, child_name)
                self.add_log_message(f"Removed child '{child_name}' under parent '{parent_name}'.")

            # Remove the parent if it has no more children
            if not self.data[parent_name]:
                del self.data[parent_name]
                parent_item = self._find_tree_item(parent_name)
                if parent_item:
                    index = self.tree.indexOfTopLevelItem(parent_item)
                    if index != -1:
                        self.tree.takeTopLevelItem(index)
                self.o3d_viewer.remove_item(parent_name)
                self.add_log_message(f"Removed parent '{parent_name}' as it had no more children.")

    def _find_tree_item(self, file_name):
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.text(0) == file_name:
                return item
        return None

    def delete_item(self, item, is_child):
        """
        Delete the selected item from the tree and data.
        If is_child is True, deletes only the child.
        Otherwise, deletes the parent and all its children.
        """
        if is_child:
            parent_item = item.parent()
            parent_name = parent_item.text(0)
            child_name = item.text(0)
            self.remove_from_tree_and_data(parent_name, child_name)
            self.add_log_message(f"Deleted child '{child_name}' under parent '{parent_name}'.")
        else:
            parent_name = item.text(0)
            self.remove_from_tree_and_data(parent_name)
            self.add_log_message(f"Deleted parent '{parent_name}' and all its children.")

    def open_file_dialog(self, dialog_type):
        """Open file dialog to select files based on the type of addition (pointcloud or mesh)."""
        if dialog_type == "Pointcloud":
            file_paths, _ = QFileDialog.getOpenFileNames(
                self, "Select Pointcloud Files", "",
                "Pointclouds (*.pcd *.las *.ply *.xyz *.xyzn *.xyzrgb *.pts)"
            )
            if file_paths:
                for file_path in file_paths:
                    self.add_pointcloud(file_path)
        elif dialog_type == "Mesh":
            file_paths, _ = QFileDialog.getOpenFileNames(
                self, "Select Mesh Files", "",
                "Meshes (*.ply *.obj *.stl *.glb *.fbx *.3mf *.off)"
            )
            if file_paths:
                for file_path in file_paths:
                    self.add_mesh(file_path, transform_settings={})

    def on_item_changed(self, item):
        is_checked = item.checkState(0) == Qt.CheckState.Checked
        # Prevent infinite loops
        self.tree.blockSignals(True)
        try:
            # Parent-level changes
            if not item.parent():
                parent_name = item.text(0)
                for i in range(item.childCount()):
                    child_item = item.child(i)
                    child_item.setCheckState(0, Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
                    child_name = child_item.text(0)
                    # Toggle visibility in the viewer
                    self.o3d_viewer.toggle_item_visibility(parent_name, child_name, is_checked)
            else:  # Child-level changes
                parent_name = item.parent().text(0)
                child_name = item.text(0)
                # Toggle visibility in the viewer
                self.o3d_viewer.toggle_item_visibility(parent_name, child_name, is_checked)
        finally:
            self.tree.blockSignals(False)

    def apply_spatial_transformation(self):
        """Applies spatial transformation to selected point clouds."""
        selected_items = self.selected_items()

        # Collect selected point clouds
        selected_point_clouds = []
        for item in selected_items:
            parent_name = item.parent().text(0) if item.parent() else None
            child_name = item.text(0)
            key = (parent_name, child_name)

            if key in self.o3d_viewer.items:
                o3d_item = self.o3d_viewer.items[key]
                if isinstance(o3d_item, o3d.geometry.PointCloud):
                    selected_point_clouds.append((key, o3d_item))

        if not selected_point_clouds:
            self.add_log_message("No point clouds selected for transformation.")
            return

        # Show the transformation dialog
        dialog = TransformationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            translation, rotation, mirroring = dialog.get_transformation_parameters()

            for (key, point_cloud) in selected_point_clouds:
                try:
                    # Validate point cloud
                    if not hasattr(point_cloud, 'points') or len(point_cloud.points) == 0:
                        self.add_log_message(f"Point cloud '{key[1]}' is empty or invalid. Skipping transformation.")
                        continue

                    self.add_log_message(f"Attempting to translate point cloud with translation: {translation}")
                    if not isinstance(translation, (list, tuple)) or len(translation) != 3:
                        self.add_log_message(f"Invalid translation vector: {translation}. Skipping translation.")
                        continue

                    # Apply transformations manually
                    if any(value != 0 for value in translation):
                        self.add_log_message(f"Applying manual translation {translation} to point cloud '{key[1]}'.")
                        try:
                            # Convert points to a NumPy array, apply translation, and assign back
                            points = np.asarray(point_cloud.points)  # Convert to NumPy array
                            points += np.array(translation)  # Apply translation
                            point_cloud.points = o3d.utility.Vector3dVector(points)  # Assign back
                        except Exception as e:
                            self.add_log_message(f"Failed to apply manual translation to '{key[1]}': {e}")
                            continue

                    if any(rotation):
                        self.add_log_message(f"Applying rotation {rotation} to point cloud '{key[1]}'.")
                        rotation_radians = [np.radians(angle) for angle in rotation]
                        rotation_matrix = o3d.geometry.get_rotation_matrix_from_xyz(rotation_radians)
                        point_cloud.rotate(rotation_matrix, center=point_cloud.get_center())

                    if any(mirroring):
                        self.add_log_message(f"Applying mirroring {mirroring} to point cloud '{key[1]}'.")
                        mirror_matrix = np.eye(4)
                        mirror_matrix[0, 0] = -1 if mirroring[0] else 1
                        mirror_matrix[1, 1] = -1 if mirroring[1] else 1
                        mirror_matrix[2, 2] = -1 if mirroring[2] else 1
                        point_cloud.transform(mirror_matrix)

                    # Remove and re-add the point cloud to refresh the viewer
                    parent_name, child_name = key
                    self.add_log_message(f"Removing point cloud '{child_name}' from viewer.")
                    try:
                        self.o3d_viewer.remove_item(parent_name, child_name)
                        time.sleep(0.1)  # Add delay to allow viewer to process removal
                        self.add_log_message(f"Re-adding point cloud '{child_name}' to viewer.")
                        self.o3d_viewer.add_item(point_cloud, parent_name, child_name)
                        time.sleep(0.1)  # Add delay to allow viewer to process re-addition
                    except Exception as e:
                        self.add_log_message(f"Failed to update viewer for '{child_name}': {e}")
                        continue

                    # Add log message
                    self.add_log_message(f"Transformed point cloud '{key[1]}' under '{key[0]}'.")

                except Exception as e:
                    self.add_log_message(f"Failed to transform point cloud '{key[1]}': {e}")

            # Refresh the Open3D viewer
            self.o3d_viewer.update_viewer()


    # Define a function to open the URL
    @staticmethod
    def open_user_guide():
        QDesktopServices.openUrl(QUrl("https://github.com/SpatialDigger/PCPro3/tree/main/docs"))

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")

        add_pointcloud_action = QAction("Add Pointcloud", self)
        add_pointcloud_action.setToolTip("Load a pointcloud from a file")
        add_pointcloud_action.setEnabled(True)
        add_pointcloud_action.triggered.connect(lambda: self.open_file_dialog("Pointcloud"))
        file_menu.addAction(add_pointcloud_action)

        add_mesh_action = QAction("Add Mesh", self)
        add_mesh_action.setToolTip("Feature not yet implemented")
        add_mesh_action.setEnabled(True)
        add_mesh_action.triggered.connect(lambda: self.open_file_dialog("Mesh"))
        file_menu.addAction(add_mesh_action)

        add_line_action = QAction("Add Line", self)
        add_line_action.setToolTip("Feature not yet implemented")
        add_line_action.setEnabled(False)  # Not implemented yet
        file_menu.addAction(add_line_action)

        save_project_action = QAction("Save Project", self)
        save_project_action.setToolTip("Feature not yet implemented")
        save_project_action.setEnabled(False)  # Not implemented yet
        file_menu.addAction(save_project_action)

        open_project_action = QAction("Open Project", self)
        open_project_action.setToolTip("Feature not yet implemented")
        open_project_action.setEnabled(False)  # Not implemented yet
        file_menu.addAction(open_project_action)

        recent_files_menu = file_menu.addMenu("Recent Files")
        recent_files_menu.setToolTip("Feature not yet implemented")
        recent_files_menu.setEnabled(False)  # Not implemented yet

        export_action = QAction("Export", self)
        export_action.setToolTip("Feature not yet implemented")
        export_action.setEnabled(False)  # Not implemented yet
        file_menu.addAction(export_action)

        exit_action = QAction("Exit", self)
        exit_action.setToolTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menu_bar.addMenu("Edit")

        # Normals Submenu
        normals_menu = edit_menu.addMenu("Normals")

        calculate_normals_action = QAction("Calculate Normals", self)
        calculate_normals_action.setToolTip("Calculate Normals")
        calculate_normals_action.setEnabled(True)
        calculate_normals_action.triggered.connect(lambda: compute_normals(self, self.selected_items()))
        normals_menu.addAction(calculate_normals_action)

        invert_normals_action = QAction("Invert Normals", self)
        invert_normals_action.setToolTip("Filter points based on a hull footprint")
        invert_normals_action.setEnabled(True)
        invert_normals_action.triggered.connect(lambda: invert_normals(self, self.selected_items()))
        normals_menu.addAction(invert_normals_action)

        merge_action = QAction("Merge", self)
        merge_action.setToolTip("Merge selected pointclouds")
        merge_action.setEnabled(True)
        merge_action.triggered.connect(lambda: merge_items(self, self.selected_items()))
        edit_menu.addAction(merge_action)

        convert_action = QAction("Convert", self)
        convert_action.setToolTip("Open the log window to view application logs")
        convert_action.setEnabled(False)
        convert_action.triggered.connect(self.convert)
        edit_menu.addAction(convert_action)

        spatial_transformation_action = QAction("Spatial Transformation", self)
        spatial_transformation_action.setToolTip("Spatial Transformation")
        spatial_transformation_action.setEnabled(True)
        spatial_transformation_action.triggered.connect(self.apply_spatial_transformation)
        edit_menu.addAction(spatial_transformation_action)

        # View Menu
        view_menu = menu_bar.addMenu("View")

        view_log_action = QAction("View Log", self)
        view_log_action.setToolTip("Open the log window to view application logs")
        view_log_action.setEnabled(True)
        view_log_action.triggered.connect(self.log_window.show)
        view_menu.addAction(view_log_action)

        axis_action = QAction("Display Axis", self)
        axis_action.setToolTip("Sample the pointcloud data")
        axis_action.setEnabled(False)
        axis_action.triggered.connect(lambda: self.add_axis())
        view_menu.addAction(axis_action)

        # Add "Toggle XYZ Axis" action
        # view_xyz_axis_action = QAction("Toggle XYZ Axis", self)
        # view_xyz_axis_action.setCheckable(True)  # Allows toggling
        # view_xyz_axis_action.setChecked(False)  # Default state is off
        # view_xyz_axis_action.triggered.connect(self.toggle_view_bounding_box)
        # view_menu.addAction(view_xyz_axis_action)

        # reset_view_action = QAction("Reset View", self)
        # reset_view_action.setToolTip("Feature not yet implemented")
        # reset_view_action.setEnabled(False)  # Not implemented yet
        # view_menu.addAction(reset_view_action)
        #
        # toggle_grid_action = QAction("Toggle Grid", self)
        # toggle_grid_action.setToolTip("Feature not yet implemented")
        # toggle_grid_action.setEnabled(False)  # Not implemented yet
        # view_menu.addAction(toggle_grid_action)

        # toggle_bounding_box_action = QAction("Toggle Bounding Box", self)
        # toggle_bounding_box_action.setToolTip("Feature not yet implemented")
        # toggle_bounding_box_action.setEnabled(False)  # Not implemented yet
        # view_menu.addAction(toggle_bounding_box_action)
        #
        # orthographic_view_action = QAction("Orthographic View", self)
        # orthographic_view_action.setToolTip("Feature not yet implemented")
        # orthographic_view_action.setEnabled(False)  # Not implemented yet
        # view_menu.addAction(orthographic_view_action)

        # Tools Menu
        tools_menu = menu_bar.addMenu("Tools")

        filters_menu = tools_menu.addMenu("Filters")
        filters_menu.setToolTip("Apply various filters to your data")

        sample_action = QAction("Sample", self)
        sample_action.setToolTip("Sample the pointcloud data")
        sample_action.setEnabled(True)
        sample_action.triggered.connect(lambda: sampling(self, self.selected_items()))
        filters_menu.addAction(sample_action)

        convexhull_action = QAction("Convexhull 3D", self)
        convexhull_action.setToolTip("Compute the 3D convex hull of the pointcloud")
        convexhull_action.setEnabled(True)
        convexhull_action.triggered.connect(lambda: convexhull3d(self, self.selected_items()))
        filters_menu.addAction(convexhull_action)

        substitute_points_action = QAction("Substitute", self)
        substitute_points_action.setToolTip("Substitute Points")
        substitute_points_action.setEnabled(False)
        substitute_points_action.triggered.connect(lambda: substitute_points(self, self.selected_items()))
        filters_menu.addAction(substitute_points_action)

        fill_holes_action = QAction("delaunay3d", self)
        fill_holes_action.setToolTip("Substitute Points")
        fill_holes_action.setEnabled(False)
        # fill_holes_action.triggered.connect(lambda: ball_pivoting_triangulation(self, self.selected_items()))
        filters_menu.addAction(fill_holes_action)

        add_bounding_box_action = QAction("Bounding Box", self)
        add_bounding_box_action.setToolTip("Merge selected pointclouds")
        add_bounding_box_action.setEnabled(False)
        add_bounding_box_action.triggered.connect(lambda: boundingbox3d(self, self.selected_items()))
        view_menu.addAction(add_bounding_box_action)

        filter_points_by_hull_footprint_action = QAction("Hull Footprint", self)
        filter_points_by_hull_footprint_action.setToolTip("Filter points based on a hull footprint")
        filter_points_by_hull_footprint_action.setEnabled(True)
        filter_points_by_hull_footprint_action.triggered.connect(self.filter_points_by_hull_footprint)
        filters_menu.addAction(filter_points_by_hull_footprint_action)

        between_distance_action = QAction("Between Distance", self)
        between_distance_action.setToolTip("Filter points based on their distances")
        between_distance_action.setEnabled(True)
        between_distance_action.triggered.connect(lambda: filter_points_by_distance(self, self.selected_items()))
        filters_menu.addAction(between_distance_action)

        # noise_removal_action = QAction("Noise Removal", self)
        # noise_removal_action.setToolTip("Feature not yet implemented")
        # noise_removal_action.setEnabled(False)  # Not implemented yet
        # filters_menu.addAction(noise_removal_action)
        #
        # segmentation_action = QAction("Segmentation", self)
        # segmentation_action.setToolTip("Feature not yet implemented")
        # segmentation_action.setEnabled(False)  # Not implemented yet
        # filters_menu.addAction(segmentation_action)
        #
        # color_mapping_action = QAction("Color Mapping", self)
        # color_mapping_action.setToolTip("Feature not yet implemented")
        # color_mapping_action.setEnabled(False)  # Not implemented yet
        # filters_menu.addAction(color_mapping_action)

        # calculate_action = QAction("Calculate", self)
        # calculate_action.setToolTip("Sample the pointcloud data")
        # calculate_action.triggered.connect(self.calculate_stats)
        # # add_bounding_box_action.triggered.connect(lambda: boundingbox3d(self, self.selected_items()))
        # tools_menu.addAction(calculate_action)

        remove_items_action = QAction("Remove Items", self)
        remove_items_action.setToolTip("Remove selected items from the workspace")
        remove_items_action.setEnabled(True)
        remove_items_action.triggered.connect(self.remove_selected_items)
        tools_menu.addAction(remove_items_action)


        # Analysis Menu
        analysis_menu = menu_bar.addMenu("Analysis")

        dbscan_action = QAction("DBSCAN Clustering", self)
        dbscan_action.setToolTip("Perform DBSCAN clustering on the pointcloud")
        dbscan_action.setEnabled(True)
        dbscan_action.triggered.connect(self.open_dbscan_dialog)
        analysis_menu.addAction(dbscan_action)

        poisson_surface_reconstruction_action = QAction("Poisson Surface Reconstruction", self)
        poisson_surface_reconstruction_action.setToolTip("Compute the 3D convex hull of the pointcloud")
        poisson_surface_reconstruction_action.setEnabled(True)
        poisson_surface_reconstruction_action.triggered.connect(lambda: poisson_surface_reconstruction(self, self.selected_items()))
        analysis_menu.addAction(poisson_surface_reconstruction_action)

        # pca_action = QAction("Principal Component Analysis (PCA)", self)
        # pca_action.setToolTip("Feature not yet implemented")
        # pca_action.setEnabled(False)  # Not implemented yet
        # analysis_menu.addAction(pca_action)
        #
        # histogram_analysis_action = QAction("Histogram Analysis", self)
        # histogram_analysis_action.setToolTip("Feature not yet implemented")
        # histogram_analysis_action.setEnabled(False)  # Not implemented yet
        # analysis_menu.addAction(histogram_analysis_action)
        #
        # height_map_action = QAction("Height Map Generation", self)
        # height_map_action.setToolTip("Feature not yet implemented")
        # height_map_action.setEnabled(False)  # Not implemented yet
        # analysis_menu.addAction(height_map_action)
        #
        # line_analysis_menu = analysis_menu.addMenu("Line Analysis")
        # line_analysis_menu.setToolTip("Perform analyses on line data")
        # line_analysis_menu.setEnabled(False)  # Not implemented yet
        #
        # mesh_analysis_menu = analysis_menu.addMenu("Mesh Analysis")
        # mesh_analysis_menu.setToolTip("Perform analyses on mesh data")
        # mesh_analysis_menu.setEnabled(False)  # Not implemented yet

        # Help Menu
        help_menu = menu_bar.addMenu("Help")

        user_guide_action = QAction("User Guide", self)
        user_guide_action.setToolTip("Opens the User Guide")
        user_guide_action.setEnabled(True)  # Make it enabled now
        user_guide_action.triggered.connect(self.open_user_guide)
        help_menu.addAction(user_guide_action)

        keyboard_shortcuts_action = QAction("Keyboard Shortcuts", self)
        keyboard_shortcuts_action.setToolTip("Feature not yet implemented")
        keyboard_shortcuts_action.setEnabled(False)  # Not implemented yet
        help_menu.addAction(keyboard_shortcuts_action)

        about_action = QAction("About", self)
        about_action.setToolTip("Feature not yet implemented")
        about_action.setEnabled(False)  # Not implemented yet
        help_menu.addAction(about_action)

        # Debug menu

        debug_menu = menu_bar.addMenu("Debug")


        debug_action = QAction("self data", self)
        debug_action.setToolTip("Feature not yet implemented")
        debug_action.setEnabled(True)  # Not implemented yet
        debug_action.triggered.connect(lambda: self.debug())
        debug_menu.addAction(debug_action)

    def convert(self):
        pass

    def debug(self):
        # Assuming self.data is a dictionary
        self.add_log_message(f"Debug: Current data structure:\n{pformat(self.data)}")


    def add_mesh(self, file_path, transform_settings=None):
        """Handles importing a mesh and adding it to the tree and data dictionary."""
        try:
            # Import the mesh data
            data = self.import_mesh(file_path, transform_settings)
            file_name = data["file_name"]

            # Add the mesh as a child under the file name
            self.add_child_to_tree_and_data(
                parent_name=file_name,
                child_name="Mesh",
                data=data["Mesh"]
            )

            # Store additional metadata in the parent data dictionary
            self.data[file_name].update({
                "transform_settings": self.translation_values,
                "file_path": file_path,
                "file_name": file_name,
            })

            self.add_log_message(f"Mesh successfully added for file '{file_name}'.")
        except Exception as e:
            self.add_log_message(f"Failed to add mesh: {str(e)}")

    def import_mesh(self, file_path, transform_settings):
        """Load and process a 3D mesh."""
        self.add_log_message(f"Importing mesh: {file_path}...")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        mesh = None

        # Check file format and load accordingly
        if file_path.endswith(".ply"):
            mesh = o3d.io.read_triangle_mesh(file_path)
        elif file_path.endswith(".obj"):
            mesh = o3d.io.read_triangle_mesh(file_path, enable_post_processing=True)

            # Automatically load textures if they exist
            material_file = file_path.replace('.obj', '.mtl')
            if os.path.exists(material_file):
                self.add_log_message("Associated material file found. Textures should load automatically.")
        else:
            # Attempt to load other popular formats
            mesh = o3d.io.read_triangle_mesh(file_path)

        # Verify mesh
        if not mesh or not mesh.has_vertices() or not mesh.has_triangles():
            raise ValueError("Imported mesh is empty or invalid.")

        # Enable vertex colors if available
        if mesh.has_vertex_colors():
            self.add_log_message("Mesh has vertex colors. They will be displayed.")
        else:
            self.add_log_message("Mesh does not have vertex colors.")

        # Enable textures if available
        if mesh.has_textures():
            self.add_log_message("Mesh has textures. They will be displayed.")
        else:
            self.add_log_message("Mesh does not have textures.")

        # Apply transformations if needed
        if transform_settings:
            self.apply_transformations(mesh, transform_settings)

        file_name = os.path.basename(file_path)
        return {
            "Mesh": mesh,
            "transform_settings": self.translation_values,
            "file_path": file_path,
            "file_name": file_name,
        }

    def apply_transformations(self, mesh, transform_settings):
        """Apply transformations to the mesh based on settings."""
        self.add_log_message("Applying transformations...")
        if "scale" in transform_settings:
            scale_factor = transform_settings["scale"]
            mesh.scale(scale_factor, center=mesh.get_center())
        if "rotation" in transform_settings:
            rotation_matrix = transform_settings["rotation"]  # Should be a 3x3 matrix
            mesh.rotate(rotation_matrix, center=mesh.get_center())
        if "translation" in transform_settings:
            translation_vector = transform_settings["translation"]
            mesh.translate(translation_vector)

    def import_pointcloud(self, file_path, transform_settings):
        """Load and process a point cloud."""
        self.add_log_message(f"Importing point cloud: {file_path}...")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.endswith(".las"):
            pointcloud = self.load_las_to_open3d_chunked(file_path, transform_settings)
        else:
            try:
                pointcloud = o3d.io.read_point_cloud(file_path)
                if pointcloud.is_empty():
                    raise ValueError("Point cloud file is empty or not in a compatible format.")
            except Exception as e:
                raise ValueError(f"Error loading point cloud: {e}")

        file_name = os.path.basename(file_path)
        return {
            "Pointcloud": pointcloud,
            "transform_settings": self.translation_values,
            "file_path": file_path,
            "file_name": file_name,
        }

    def load_las_to_open3d_chunked(self, file_path, transform_settings, max_points=1_000_000):
        """Load .las file and convert to Open3D point cloud in chunks."""

        with laspy.open(file_path) as las_file:
            header = las_file.header
            points_count = header.point_count

            points = []
            colors = []

            pointcloud = las_file.read()

            sample_x = pointcloud.x[0] if len(pointcloud.x) > 0 else 0
            sample_y = pointcloud.y[0] if len(pointcloud.y) > 0 else 0

            translate_x = (int(sample_x) // 1000) * 1000
            translate_y = (int(sample_y) // 1000) * 1000

            if hasattr(self, 'translation_values'):
                self.translation_values.update({"x": translate_x, "y": translate_y})
            else:
                self.translation_values = {"x": translate_x, "y": translate_y}

            self.add_log_message(
                f"Automatically determined translation values: translate_x={translate_x}, translate_y={translate_y}")

            for start in range(0, points_count, max_points):
                end = min(start + max_points, points_count)
                chunk = pointcloud[start:end]

                x, y, z = np.array(chunk.x), np.array(chunk.y), np.array(chunk.z)

                x = x - translate_x
                y = y - translate_y

                points.append(np.column_stack((x, y, z)))

                if 'red' in chunk.point_format.dimension_names:
                    r = chunk.red / 65535.0
                    g = chunk.green / 65535.0
                    b = chunk.blue / 65535.0
                    colors.append(np.column_stack((r, g, b)))
                else:
                    colors.append(np.zeros((len(x), 3)))

            points = np.vstack(points)
            colors = np.vstack(colors)

        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        pcd.colors = o3d.utility.Vector3dVector(colors)
        return pcd

    def open_dbscan_dialog(self):

        # Retrieve selected items from the tree
        selected_items = self.selected_items()

        for item in selected_items:
            # Determine the file name and check hierarchy
            if item.parent():  # If it's a child item
                parent_name = item.parent().text(0)  # Parent holds the file name
                child_name = item.text(0)  # Child text represents the cloud type
            else:  # If it's a top-level (parent) item
                self.add_log_message("Top-level items cannot be clustered directly.")
                continue

            # Retrieve the point cloud data
            data = self.data.get(parent_name)
            if not data:
                self.add_log_message(f"No valid point cloud found for {parent_name}. Skipping.")
                continue
            point_cloud = data[child_name]

            # Open the dialog to configure DBSCAN parameters
            dialog = DBSCANDialog(self)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                self.add_log_message("DBSCAN dialog canceled.")
                continue

            # Retrieve DBSCAN parameters from the dialog
            eps = dialog.get_eps()
            min_points = dialog.get_min_points()

            # Perform DBSCAN clustering
            def perform_dbscan(point_cloud, eps, min_points):
                # Convert point cloud to NumPy array
                points = np.asarray(point_cloud.points)

                # Perform DBSCAN
                labels = np.array(o3d.geometry.PointCloud.cluster_dbscan(
                    point_cloud, eps=eps, min_points=min_points, print_progress=True
                ))

                return labels

            labels = perform_dbscan(point_cloud, eps, min_points)

            # Check if DBSCAN was successful
            if labels is None or len(labels) == 0:
                self.add_log_message(f"DBSCAN failed for {parent_name}.")
                continue

            max_label = labels.max()
            self.add_log_message(f"DBSCAN found {max_label + 1} clusters for {child_name}.")

            # Loop through each cluster (label)
            for label in range(max_label + 1):
                # Select the points belonging to the current cluster
                cluster_indices = np.where(labels == label)[0]
                cluster_points = point_cloud.select_by_index(cluster_indices)

                # Name the cluster with a suffix based on the cluster label
                cluster_name = f"{child_name}_Cluster_{label}"

                # Retain the original colors of the cluster points
                original_colors = np.asarray(point_cloud.colors)[cluster_indices]  # Extract original RGB colors
                cluster_points.colors = o3d.utility.Vector3dVector(original_colors)  # Assign original colors

                # Add the cluster to the data dictionary
                self.data[parent_name][cluster_name] = cluster_points

                # Add the cluster to the tree and viewer
                self.add_child_to_tree_and_data(parent_name, cluster_name, cluster_points)

                # Add the cluster to the viewer
                self.o3d_viewer.add_item(cluster_points, parent_name, cluster_name)
                self.add_log_message(f"Cluster {label} added: {cluster_name}")

            # Update the viewer
            self.o3d_viewer.update_viewer()
            self.add_log_message("Viewer updated with DBSCAN clusters.")

    def filter_points_by_hull_footprint(self):
        """Filters points from a selected Open3D point cloud that fall within the footprint of a selected line set (3D convex hull)."""
        selected_items = self.selected_items()

        # Separate selected point clouds and line sets
        selected_point_clouds = []
        selected_line_sets = []
        for item in selected_items:
            parent_name = item.parent().text(0) if item.parent() else None
            child_name = item.text(0)
            key = (parent_name, child_name)

            if key in self.o3d_viewer.items:
                o3d_item = self.o3d_viewer.items[key]
                if isinstance(o3d_item, o3d.geometry.PointCloud):
                    selected_point_clouds.append(o3d_item)
                elif isinstance(o3d_item, o3d.geometry.LineSet):
                    selected_line_sets.append(o3d_item)

        if not selected_point_clouds or not selected_line_sets:
            self.add_log_message("At least one point cloud and one line set must be selected.")
            return

        # Iterate through selected point clouds and line sets
        for point_cloud in selected_point_clouds:
            for line_set in selected_line_sets:
                # Flatten the point cloud (remove z-coordinate)
                points = np.asarray(point_cloud.points)
                colors = np.asarray(point_cloud.colors)  # Get RGB values
                points_2d = points[:, :2]

                # Extract edges from the line set
                lines = np.asarray(line_set.lines)
                vertices = np.asarray(line_set.points)
                vertices_2d = vertices[:, :2]

                # Ensure the line set forms a closed loop (by appending the first vertex at the end if necessary)
                if not np.array_equal(vertices_2d[0], vertices_2d[-1]):
                    vertices_2d = np.vstack([vertices_2d, vertices_2d[0]])

                # Create LineString objects for each edge (i.e., face of the convex hull in 2D)
                edges = []
                for i in range(len(vertices_2d) - 1):
                    edge = LineString([vertices_2d[i], vertices_2d[i + 1]])
                    edges.append(edge)

                # Merge all line segments into a single polygon
                merged_polygon = unary_union(edges)
                if isinstance(merged_polygon, Polygon):
                    polygon = merged_polygon
                else:
                    # If we get multiple separate polygons, merge them into one (using convex hull if needed)
                    polygon = merged_polygon.convex_hull

                # Filter points inside the polygon (keep the 3D structure)
                filtered_points = []
                filtered_colors = []
                for i, point in enumerate(points_2d):
                    if polygon.contains(Point(point)):
                        # Append the original 3D point and corresponding color (RGB)
                        filtered_points.append(points[i])
                        filtered_colors.append(colors[i])

                if not filtered_points:
                    self.add_log_message("No points found inside the polygon.")
                    continue

                # Create a new point cloud from filtered points, restoring Z-coordinate
                new_point_cloud = o3d.geometry.PointCloud()
                new_point_cloud.points = o3d.utility.Vector3dVector(np.array(filtered_points))
                new_point_cloud.colors = o3d.utility.Vector3dVector(np.array(filtered_colors))  # Add RGB values

                # Generate the child name for the new point cloud
                base_child_name = "pointcloud_in_3dhull"
                child_name = base_child_name

                # Check if a point cloud with this name already exists under the parent
                parent_name = None
                for item in selected_items:
                    # if item.text(0) == point_cloud.name:
                    if item.text(0) == child_name:
                        parent_name = item.parent().text(0) if item.parent() else None
                        break

                # If parent_name is None (which should not happen in this case), fallback to the first point cloud's parent
                if parent_name is None:
                    parent_name = selected_items[0].parent().text(0) if selected_items[
                        0].parent() else "Filtered Point Clouds"

                # Ensure unique child name by checking if it exists under the parent
                existing_children = self.data.get(parent_name, {}).keys()
                counter = 1
                while child_name in existing_children:
                    child_name = f"{base_child_name}_{counter}"
                    counter += 1

                # Add the new point cloud to the tree and data using add_child_to_tree_and_data
                self.add_child_to_tree_and_data(parent_name, child_name, new_point_cloud)

                self.add_log_message(f"Added filtered point cloud '{child_name}' under '{parent_name}'.")

    def add_log_message(self, message):
        self.log_window.add_message(message)

    def closeEvent(self, event):
        """Handle the close event to ensure Open3D viewer is closed."""
        self.o3d_viewer.close()
        super().closeEvent(event)




# used for checking, remove from production
def visualize_pointcloud(pointcloud):
    """
    Visualize a given Open3D point cloud.
    :param pointcloud: An instance of o3d.geometry.PointCloud
    """
    # if not isinstance(pointcloud, o3d.geometry.PointCloud):
    #     print("Provided object is not a valid Open3D point cloud.")
    #     return

    # Create a visualization window
    o3d.visualization.draw_geometries(
        [pointcloud],
        window_name="Pointcloud Processor",
        width=800,
        height=600,
        left=50,
        top=50,
        point_show_normal=False
    )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())

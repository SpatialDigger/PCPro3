import os
import sys
import time
import warnings
import numpy as np
import laspy
import open3d as o3d
import webbrowser

from pprint import pformat
from sklearn.cluster import DBSCAN
from shapely.geometry import Point, Polygon, MultiLineString, LineString
from shapely.ops import unary_union
from PyQt5.QtGui import QDesktopServices, QPixmap
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTreeWidget, QAbstractItemView,
    QApplication, QAction, QMenu,
    QFileDialog, QColorDialog, QTreeWidgetItem, QDialog, QAction, QMessageBox,
    QLabel, QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QPoint, QUrl
from viewer import Open3DViewer
from dialogs_pyqt5 import (
    LogWindow, PropertiesDialog, DBSCANDialog, AboutDialog, KeyboardShortcutsDialog
)
from PyQt5.QtCore import  QUrl

from read_funcs import (
    open_file_dialog
)

from write_funcs import (
    export_item
)

from tools import (
    convexhull3d, filter_points_by_distance, sampling,
    merge_items, boundingbox3d, poisson_surface_reconstruction,
    substitute_points, apply_spatial_transformation, dbscan_analysis,
    filter_points_by_hull_footprint
)
# from normals import ball_pivoting_triangulation
from normals import(
    compute_normals, invert_normals)

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QHBoxLayout

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices


from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget,
    QAbstractItemView, QLabel, QSizePolicy, QSplitter
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap

from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTreeWidget, QAbstractItemView, QLabel, QSizePolicy

class AdPanel(QWidget):
    """A simple panel to display an AdMob banner ad."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a web view to display the ad
        self.web_view = QWebEngineView()

        # Load the local HTML file containing the AdMob script
        ad_url = QUrl.fromLocalFile(r"C:\Users\garyn\PycharmProjects\PCPro3\adverts\banner_ad.html")
        self.web_view.setUrl(ad_url)

        # Set a fixed height for the banner
        self.web_view.setFixedHeight(100)

        layout.addWidget(self.web_view)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pointcloud Processor 0.1.2")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # Create the top panel widget (for your tree view)
        self.top_panel = QWidget()
        top_layout = QVBoxLayout()
        self.top_panel.setLayout(top_layout)

        # Tree widget for datasets
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Contents"])
        self.tree.setSelectionMode(QAbstractItemView.MultiSelection)
        self.tree.itemChanged.connect(self.on_item_changed)
        top_layout.addWidget(self.tree)

        layout.addWidget(self.top_panel)

        # Add the AdMob banner panel at the bottom
        self.ad_panel = AdPanel()
        layout.addWidget(self.ad_panel, stretch=0)  # No stretch to keep it at a fixed height

        # Initialize other variables and setups
        self.data = {}
        self.original_colors = {}

        self.o3d_viewer = Open3DViewer(logger=self.add_log_message, data=self.data)
        self.log_window = LogWindow(self)

        self.create_menu_bar()

        self.viewer_update_timer = QTimer()
        self.viewer_update_timer.timeout.connect(self.o3d_viewer.update_viewer)
        self.viewer_update_timer.start(16)

        self.translation_values = {'x': 0, 'y': 0, 'z': 0}

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_right_click_menu)

        self.coordinate_frame_visible = False
        self.metadata = {}
        self.original_colors = {}



    #####
    # Menus
    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")

        add_pointcloud_action = QAction("Add Pointcloud", self)
        add_pointcloud_action.setToolTip("Load a pointcloud from a file")
        add_pointcloud_action.setEnabled(True)
        add_pointcloud_action.triggered.connect(lambda: open_file_dialog(self, "Pointcloud"))
        file_menu.addAction(add_pointcloud_action)

        add_mesh_action = QAction("Add Mesh", self)
        add_mesh_action.setToolTip("Feature not yet implemented")
        add_mesh_action.setEnabled(True)
        add_mesh_action.triggered.connect(lambda: open_file_dialog(self, "Mesh"))
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
        spatial_transformation_action.triggered.connect(lambda: apply_spatial_transformation(self, self.selected_items()))
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
        substitute_points_action.setEnabled(True)
        substitute_points_action.triggered.connect(lambda: substitute_points(self))
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
        filter_points_by_hull_footprint_action.triggered.connect(lambda: filter_points_by_hull_footprint(self, self.selected_items()))
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
        dbscan_action.triggered.connect(lambda: dbscan_analysis(self, self.selected_items()))
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
        keyboard_shortcuts_action.setEnabled(True)
        keyboard_shortcuts_action.triggered.connect(lambda: self.show_keyboard_dialog())
        help_menu.addAction(keyboard_shortcuts_action)

        about_action = QAction("About", self)
        about_action.setToolTip("Feature not yet implemented")
        about_action.setEnabled(True)
        about_action.triggered.connect(lambda: self.show_about_dialog())
        help_menu.addAction(about_action)

        # Debug menu

        debug_menu = menu_bar.addMenu("Debug")


        debug_action = QAction("self data", self)
        debug_action.setToolTip("Feature not yet implemented")
        debug_action.setEnabled(True)  # Not implemented yet
        debug_action.triggered.connect(lambda: self.debug())
        debug_menu.addAction(debug_action)

    def show_right_click_menu(self, position: QPoint):
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
                action_export.triggered.connect(lambda: export_item(self, self.selected_items()))  # Passing `self` and the selected item
                menu.addAction(action_export)

            else:  # Parent item-specific options
                action_rename = QAction("Rename", self)
                action_rename.setToolTip("Rename this item")
                action_rename.triggered.connect(lambda: self.start_rename(item))
                menu.addAction(action_rename)

            menu.exec(self.tree.viewport().mapToGlobal(position))

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

    def debug(self):
        # Assuming self.data is a dictionary
        self.add_log_message(f"Debug: Current data structure:\n{pformat(self.data)}")

    #####
    @staticmethod
    def show_about_dialog():
        dialog = AboutDialog()
        dialog.exec_()

    @staticmethod
    def open_user_guide():
        QDesktopServices.openUrl(QUrl("https://github.com/SpatialDigger/PCPro3/tree/main/docs"))

    @staticmethod
    def show_keyboard_dialog():
        dialog = KeyboardShortcutsDialog()
        dialog.exec_()

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

    def add_log_message(self, message):
        self.log_window.add_message(message)

    def closeEvent(self, event):
        """Handle the close event to ensure Open3D viewer is closed."""
        self.o3d_viewer.close()
        super().closeEvent(event)


    #####
    # To be moved to

    # Tools







    # Visualisation

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



    #####
    # Experimental
    def convert(self):
        pass





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
    window.resize(400, 800)
    window.show()
    sys.exit(app.exec())

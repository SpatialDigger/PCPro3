import os
import sys
import time
import warnings
import numpy as np
import laspy
import open3d as o3d
import webbrowser
from pathlib import Path
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication

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
from PyQt5.QtGui import QIcon
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

from splash import SplashScreen

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QHBoxLayout

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices


from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget,
    QAbstractItemView, QLabel, QSizePolicy, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QPixmap

from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTreeWidget, QAbstractItemView, QLabel, QSizePolicy

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QErrorMessage
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QImage
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import QByteArray, QBuffer
import sys


import json
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QColor



import json
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QColorDialog, QErrorMessage

# CONFIG_FILE = "themes/config.json"
# CONFIG_DEFAULTS_FILE = "themes/config_defaults.json"  # File containing default settings

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.theme_label = QLabel("Select Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
                                    "modern_light", "modern_dark",
                                    "obsidian_flame_dark", "obsidian_flame_light",
                                    "nord_dark", "nord_light",
                                    "forest_retreat_dark", "forest_retreat_light",
                                   ])

        # Load current theme from config
        self.load_preferences()

        # Background color picker
        self.color_label = QLabel("Select Background Color:")
        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self.select_color)

        # Load current background color and convert from float (0-1) to integer (0-255)
        try:
            with open(MainWindow.fetch_config(), "r") as f:
                config = json.load(f)
                current_color = config.get("background_color", [0.180, 0.180, 0.180])  # Default dark gray
            self.current_color = QColor(int(current_color[0] * 255), int(current_color[1] * 255), int(current_color[2] * 255))
        except Exception as e:
            print(f"Error loading background color from config: {e}")
            self.current_color = QColor(0.180 * 255, 0.180 * 255, 0.180 * 255)  # Fallback to default dark gray

        # Set initial color
        self.color_button.setStyleSheet(f"background-color: {self.current_color.name()};")

        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_preferences)

        # Revert to defaults button
        self.revert_button = QPushButton("Revert to Defaults")
        self.revert_button.clicked.connect(self.revert_to_defaults)

        layout.addWidget(self.theme_label)
        layout.addWidget(self.theme_combo)
        layout.addWidget(self.color_label)
        layout.addWidget(self.color_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.revert_button)

    def load_preferences(self):
        """Load preferences from config or defaults."""
        try:
            with open(MainWindow.fetch_config(), "r") as f:
                config = json.load(f)
                current_theme = config.get("theme", "none")
            if current_theme == "none":
                self.theme_combo.setCurrentText("None")
            else:
                self.theme_combo.setCurrentText(current_theme)
        except Exception as e:
            print(f"Error loading theme from config: {e}")
            self.show_error("Error loading preferences from config.")

    def select_color(self):
        """Open a color dialog and set the selected color."""
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color
            self.color_button.setStyleSheet(f"background-color: {self.current_color.name()};")

    def save_preferences(self):
        """Save the selected theme and background color to config."""
        try:
            selected_theme = self.theme_combo.currentText()
            theme_value = "none" if selected_theme == "None" else selected_theme

            # Convert the QColor to RGB float values (0.0 to 1.0 range)
            r, g, b = self.current_color.redF(), self.current_color.greenF(), self.current_color.blueF()
            print(f"Saving theme: {theme_value}, background color: ({r}, {g}, {b})")  # Debugging log

            with open(MainWindow.fetch_config(), "w") as f:
                json.dump({
                    "theme": theme_value,
                    "background_color": [r, g, b]
                }, f)

            # Apply the theme to the parent (Open3DViewer)
            self.parent().apply_theme(theme_value)

            # Update Open3DViewer background color
            background_color = [self.current_color.redF(), self.current_color.greenF(), self.current_color.blueF()]
            self.parent().o3d_viewer.update_background_color(background_color)

            self.close()

        except Exception as e:
            print(f"Error saving preferences: {e}")
            self.show_error("Error saving preferences.")

    def revert_to_defaults(self):
        """Revert to default theme and background color."""
        try:
            with open(MainWindow.fetch_default_config(), "r") as f:
                default_config = json.load(f)

            # Load default theme and background color
            default_theme = default_config.get("theme", "light")
            default_background_color = default_config.get("background_color", [0.180, 0.180, 0.180])

            # Set theme and background color to defaults
            self.theme_combo.setCurrentText(default_theme)
            self.current_color = QColor(int(default_background_color[0] * 255),
                                         int(default_background_color[1] * 255),
                                         int(default_background_color[2] * 255))
            self.color_button.setStyleSheet(f"background-color: {self.current_color.name()};")

            print(f"Reverted to defaults: theme = {default_theme}, background color = {default_background_color}")

        except Exception as e:
            print(f"Error reverting to defaults: {e}")
            self.show_error("Error reverting to defaults.")

    def show_error(self, message):
        """Show an error dialog."""
        error_dialog = QErrorMessage(self)
        error_dialog.showMessage(message)
        error_dialog.exec_()


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


from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QAbstractItemView
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QApplication
from PyQt5.QtCore import Qt, QMimeData, QByteArray
from PyQt5.QtGui import QDrag


from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt, QMimeData, QByteArray
from PyQt5.QtGui import QDrag

from tracking import report

class CustomTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QTreeWidget.MultiSelection)
        self.setHeaderLabels(["Contents"])
        self.setDragDropMode(QTreeWidget.InternalMove)  # Internal movement
        self.setDragEnabled(True)  # Enable dragging
        self.setAcceptDrops(True)  # Enable dropping
        self.setDefaultDropAction(Qt.MoveAction)
        self.last_selected_item = None  # Store last selected item for Shift + Click
        self.dragged_items = []  # Store dragged items

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())

        if event.modifiers() == Qt.ShiftModifier and self.last_selected_item:
            self.select_range(self.last_selected_item, item)
        elif not item:
            self.clearSelection()
        else:
            self.last_selected_item = item

        super().mousePressEvent(event)

    def select_range(self, start_item, end_item):
        start_row = self.indexOfTopLevelItem(start_item)
        end_row = self.indexOfTopLevelItem(end_item)

        if start_row == -1 or end_row == -1:
            return

        if start_row > end_row:
            start_row, end_row = end_row, start_row

        for row in range(start_row, end_row + 1):
            item = self.topLevelItem(row)
            self.select_item_and_children(item)

    def select_item_and_children(self, item):
        if item is None:
            return
        item.setSelected(True)
        for i in range(item.childCount()):
            item.child(i).setSelected(True)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_A:
            self.select_all_items()
        else:
            super().keyPressEvent(event)

    def select_all_items(self):
        for row in range(self.topLevelItemCount()):
            item = self.topLevelItem(row)
            self.select_item_and_children(item)

    def startDrag(self, supportedActions):
        """Handles the drag event"""
        self.dragged_items = self.selectedItems()
        if not self.dragged_items:
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setData("application/x-qtreewidgetitem", QByteArray())
        drag.setMimeData(mime_data)

        drag.exec_(Qt.MoveAction)  # Execute the drag operation

    def dragEnterEvent(self, event):
        """Accepts drag enter event"""
        if event.mimeData().hasFormat("application/x-qtreewidgetitem"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        """Restricts dragging to the same hierarchy level"""
        target_item = self.itemAt(event.pos())

        if not target_item:
            # Prevent moving children to the top level
            if any(item.parent() for item in self.dragged_items):
                event.ignore()
            else:
                event.acceptProposedAction()
            return

        # Prevent dropping onto itself
        if any(item is target_item for item in self.dragged_items):
            event.ignore()
            return

        parent = self.dragged_items[0].parent()
        target_parent = target_item.parent()

        # Prevent moving children to a higher level (top level)
        if parent and not target_parent:
            event.ignore()
            return

        # Ensure items stay within the same hierarchy level
        if parent != target_parent:
            event.ignore()
            return

        event.acceptProposedAction()

    def dropEvent(self, event):
        """Handles the drop event ensuring items do not disappear"""
        target_item = self.itemAt(event.pos())

        if not self.dragged_items:
            return

        parent = self.dragged_items[0].parent()
        target_parent = target_item.parent() if target_item else None

        # Prevent children from moving to the top level
        if parent and not target_parent:
            event.ignore()
            return

        # Ensure items stay within the same hierarchy level
        if parent != target_parent:
            event.ignore()
            return

        # Move items to the correct position
        for item in self.dragged_items:
            if item == target_item:
                continue  # Avoid dropping onto itself

            if parent:
                parent.removeChild(item)
                index = parent.indexOfChild(target_item) + 1
                parent.insertChild(index, item)
            else:
                self.takeTopLevelItem(self.indexOfTopLevelItem(item))
                index = self.indexOfTopLevelItem(target_item) + 1
                self.insertTopLevelItem(index, item)

        event.acceptProposedAction()









class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pointcloud Processor 3")
        self.version = '1.0.0'

        # Set the window icon
        self.setWindowIcon(QIcon("icons/icon.ico"))


        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # Create the top panel widget (for your tree view)
        self.top_panel = QWidget()
        top_layout = QVBoxLayout()
        self.top_panel.setLayout(top_layout)

        # Tree widget for datasets
        self.tree = CustomTreeWidget()
        self.tree.setHeaderLabels(["Contents"])
        self.tree.setSelectionMode(QAbstractItemView.MultiSelection)  # Multi-selection mode
        self.tree.itemChanged.connect(self.on_item_changed)

        top_layout.addWidget(self.tree)

        layout.addWidget(self.top_panel)

        # Add the AdMob banner panel at the bottom
        self.ad_panel = AdPanel()
        layout.addWidget(self.ad_panel, stretch=0)  # No stretch to keep it at a fixed height

        # Initialize other variables and setups
        self.data = {}
        self.original_colors = {}

        # Create Open3DViewer instance
        self.o3d_viewer = Open3DViewer(logger=self.add_log_message, data=self.data)

        # Create the log window
        self.log_window = LogWindow(self)

        # Create menu bar
        self.create_menu_bar()

        # Set up the timer to update the viewer
        self.viewer_update_timer = QTimer()
        self.viewer_update_timer.timeout.connect(self.o3d_viewer.update_viewer)
        self.viewer_update_timer.start(16)

        self.translation_values = {'x': 0, 'y': 0, 'z': 0}

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_right_click_menu)

        self.axis_visible = False
        # self.xyz_axis = None

        self.bbox_visible = False
        self. obbox_visible = False
        self.labels3d = False

        self.coordinate_frame_visible = False
        self.metadata = {}
        self.original_colors = {}
        self.logging = {}

        # Load theme from config
        # self.CONFIG_FILE = "themes/config.json"
        # self.CONFIG_DEFAULTS_FILE = "themes/config_defaults.json"
        self.load_theme(self.fetch_config())  # Calling static method correctly

        # Pass self (MainWindow) as the parent
        self.preferences_dialog = PreferencesDialog(self)  # Pass MainWindow instance as the parent

    @staticmethod
    def fetch_config():
        return "themes/config.json"

    @staticmethod
    def fetch_default_config():
        return "themes/config_defaults.json"



    def load_theme(self, CONFIG_FILE):
        """Load theme from config file."""
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            theme = config.get("theme", "none")  # Default to no theme
            self.apply_theme(theme)
        except FileNotFoundError:
            print("Config file not found. Using no theme.")

    def apply_theme(self, theme):
        """Apply the selected theme by loading all QSS files from the theme folder."""
        if theme == "none":
            self.setStyleSheet("")  # Clear stylesheet
            return

        theme_path = Path(f"themes/{theme}")
        if not theme_path.exists():
            print(f"Theme '{theme}' not found. Using no theme.")
            return

        styles = []
        for qss_file in ["main.qss", "splash.qss", "custom.qss"]:
            file_path = theme_path / qss_file
            if file_path.exists():
                styles.append(file_path.read_text())
            else:
                print(f"Warning: {qss_file} not found in '{theme}' theme.")

        self.setStyleSheet("\n".join(styles))  # Apply combined styles

    @staticmethod
    def colorize_svg(svg_path, color):
        pixmap = QPixmap(svg_path)
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor(color))
        painter.end()
        return QIcon(pixmap)

    # Menus
    def create_menu_bar(self):
        icon_colour = "#ffa02f"
        
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")

        add_pointcloud_action = QAction(self.colorize_svg("icons/min/icons_add_pointcloud.svg", icon_colour), "Add Pointcloud", self)
        add_pointcloud_action.setToolTip("Load a pointcloud from a file")
        add_pointcloud_action.setEnabled(True)
        add_pointcloud_action.triggered.connect(lambda: open_file_dialog(self, "Pointcloud"))
        file_menu.addAction(add_pointcloud_action)







        # add_mesh_action = QAction(self.colorize_svg("icons/min/icons_add_mesh.svg", icon_colour), "Add Mesh", self)
        add_mesh_action = QAction(self.colorize_svg("icons/min/icons_add_mesh.svg", icon_colour), "Add Mesh", self)
        add_mesh_action.setToolTip("Feature not yet implemented")
        add_mesh_action.setEnabled(True)
        add_mesh_action.triggered.connect(lambda: open_file_dialog(self, "Mesh"))
        file_menu.addAction(add_mesh_action)

        add_line_action = QAction(self.colorize_svg("icons/min/icons_add_line.svg", icon_colour), "Add Line", self)
        add_line_action.setToolTip("Feature not yet implemented")
        add_line_action.setEnabled(False)  # Not implemented yet
        file_menu.addAction(add_line_action)

        save_project_action = QAction(self.colorize_svg("icons/min/icons_save_project.svg", icon_colour), "Save Project", self)
        save_project_action.setToolTip("Feature not yet implemented")
        save_project_action.setEnabled(False)  # Not implemented yet
        file_menu.addAction(save_project_action)

        open_project_action = QAction(self.colorize_svg("icons/min/icons_open_project.svg", icon_colour), "Open Project", self)
        open_project_action.setToolTip("Feature not yet implemented")
        open_project_action.setEnabled(False)  # Not implemented yet
        file_menu.addAction(open_project_action)


        # recent_files_menu = QAction(self.colorize_svg("icons/min/icons_recent_files.svg", icon_colour), "Open Project", self)
        recent_files_menu = file_menu.addMenu("Recent Files")
        recent_files_menu.setToolTip("Feature not yet implemented")
        recent_files_menu.setEnabled(False)  # Not implemented yet

        export_action = QAction(self.colorize_svg("icons/min/icons_export.svg", icon_colour), "Export", self)
        export_action.setToolTip("Feature not yet implemented")
        export_action.setEnabled(False)  # Not implemented yet
        file_menu.addAction(export_action)

        exit_action = QAction(self.colorize_svg("icons/min/icons_exit.svg", icon_colour), "Exit", self)
        exit_action.setToolTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menu_bar.addMenu("Edit")

        # Normals Submenu
        normals_menu = edit_menu.addMenu("Normals")

        calculate_normals_action = QAction(self.colorize_svg("icons/min/icons_calculate_normals.svg", icon_colour), "Calculate Normals", self)
        calculate_normals_action.setToolTip("Calculate Normals")
        calculate_normals_action.setEnabled(True)
        calculate_normals_action.triggered.connect(lambda: compute_normals(self, self.selected_items()))
        normals_menu.addAction(calculate_normals_action)

        invert_normals_action = QAction(self.colorize_svg("icons/min/icons_invert_normals.svg", icon_colour), "Invert Normals", self)
        invert_normals_action.setToolTip("Filter points based on a hull footprint")
        invert_normals_action.setEnabled(True)
        invert_normals_action.triggered.connect(lambda: invert_normals(self, self.selected_items()))
        normals_menu.addAction(invert_normals_action)

        merge_action = QAction(self.colorize_svg("icons/min/icons_merge.svg", icon_colour), "Merge", self)
        merge_action.setToolTip("Merge selected pointclouds")
        merge_action.setEnabled(True)
        merge_action.triggered.connect(lambda: merge_items(self, self.selected_items()))
        edit_menu.addAction(merge_action)

        convert_action = QAction(self.colorize_svg("icons/min/icons_convert.svg", icon_colour), "Convert", self)
        convert_action.setToolTip("Open the log window to view application logs")
        convert_action.setEnabled(False)
        convert_action.triggered.connect(self.convert)
        edit_menu.addAction(convert_action)

        spatial_transformation_action = QAction(self.colorize_svg("icons/min/icons_spatial_transformation.svg", icon_colour), "Spatial Transformation", self)
        spatial_transformation_action.setToolTip("Spatial Transformation")
        spatial_transformation_action.setEnabled(True)
        spatial_transformation_action.triggered.connect(lambda: apply_spatial_transformation(self, self.selected_items()))
        edit_menu.addAction(spatial_transformation_action)

        preferences_action = QAction(self.colorize_svg("icons/min/.svg", icon_colour), "Preferences", self)
        preferences_action.setToolTip("Edit preperences")
        preferences_action.setEnabled(False)
        preferences_action = QAction("Preferences", self)
        preferences_action.triggered.connect(self.open_preferences)
        edit_menu.addAction(preferences_action)



        # View Menu
        view_menu = menu_bar.addMenu("View")

        view_log_action = QAction(self.colorize_svg("icons/min/icons_self_log.svg", icon_colour), "View Log", self)
        view_log_action.setToolTip("Open the log window to view application logs")
        view_log_action.setEnabled(True)
        view_log_action.triggered.connect(self.log_window.show)
        view_menu.addAction(view_log_action)

        add_bounding_box_action = QAction(self.colorize_svg("icons/min/icons_bounding_box.svg", icon_colour), "Bounding Box", self)
        add_bounding_box_action.setToolTip("Merge selected pointclouds")
        add_bounding_box_action.setEnabled(True)
        add_bounding_box_action.triggered.connect(lambda: self.toggle_bbox())
        view_menu.addAction(add_bounding_box_action)

        add_oriented_bounding_box_action = QAction(self.colorize_svg("icons/min/icons_bounding_box.svg", icon_colour), "Oriented Bounding Box", self)
        add_oriented_bounding_box_action.setToolTip("Merge selected pointclouds")
        add_oriented_bounding_box_action.setEnabled(True)
        add_oriented_bounding_box_action.triggered.connect(lambda: self.toggle_obbox())
        view_menu.addAction(add_oriented_bounding_box_action)

        add_oriented_bounding_box_action = QAction(self.colorize_svg("icons/min/icons_bounding_box.svg", icon_colour), "Tick Marks", self)
        add_oriented_bounding_box_action.setToolTip("Merge selected pointclouds")
        add_oriented_bounding_box_action.setEnabled(False)
        add_oriented_bounding_box_action.triggered.connect(lambda: self.toggle_labels3d())
        view_menu.addAction(add_oriented_bounding_box_action)

        axis_action = QAction(self.colorize_svg("icons/min/hexagon.svg", icon_colour), "Display Axis", self)
        axis_action.setToolTip("Display XYZ Axis")
        axis_action.setEnabled(True)
        axis_action.triggered.connect(lambda: self.toggle_axis())
        view_menu.addAction(axis_action)

        # Add "Toggle XYZ Axis" action
        # view_xyz_axis_action = QAction(self.colorize_svg("icons/min/hexagon.svg", icon_colour), "Toggle XYZ Axis", self)
        # view_xyz_axis_action.setCheckable(True)  # Allows toggling
        # view_xyz_axis_action.setChecked(False)  # Default state is off
        # view_xyz_axis_action.triggered.connect(self.toggle_view_bounding_box)
        # view_menu.addAction(view_xyz_axis_action)

        # reset_view_action = QAction(self.colorize_svg("icons/min/hexagon.svg", icon_colour), "Reset View", self)
        # reset_view_action.setToolTip("Feature not yet implemented")
        # reset_view_action.setEnabled(False)  # Not implemented yet
        # view_menu.addAction(reset_view_action)
        #
        # toggle_grid_action = QAction(self.colorize_svg("icons/min/hexagon.svg", icon_colour), "Toggle Grid", self)
        # toggle_grid_action.setToolTip("Feature not yet implemented")
        # toggle_grid_action.setEnabled(False)  # Not implemented yet
        # view_menu.addAction(toggle_grid_action)

        # toggle_bounding_box_action = QAction(self.colorize_svg("icons/min/hexagon.svg", icon_colour), "Toggle Bounding Box", self)
        # toggle_bounding_box_action.setToolTip("Feature not yet implemented")
        # toggle_bounding_box_action.setEnabled(False)  # Not implemented yet
        # view_menu.addAction(toggle_bounding_box_action)
        #
        # orthographic_view_action = QAction(self.colorize_svg("icons/min/hexagon.svg", icon_colour), "Orthographic View", self)
        # orthographic_view_action.setToolTip("Feature not yet implemented")
        # orthographic_view_action.setEnabled(False)  # Not implemented yet
        # view_menu.addAction(orthographic_view_action)

        # Tools Menu
        tools_menu = menu_bar.addMenu("Tools")

        filters_menu = tools_menu.addMenu("Filters")
        filters_menu.setToolTip("Apply various filters to your data")

        sample_action = QAction(self.colorize_svg("icons/min/icons_sample.svg", icon_colour), "Sample", self)
        sample_action.setToolTip("Sample the pointcloud data")
        sample_action.setEnabled(True)
        sample_action.triggered.connect(lambda: sampling(self, self.selected_items()))
        filters_menu.addAction(sample_action)

        convexhull_action = QAction(self.colorize_svg("icons/min/icons_convexhull_3d.svg", icon_colour), "Convexhull 3D", self)
        convexhull_action.setToolTip("Compute the 3D convex hull of the pointcloud")
        convexhull_action.setEnabled(True)
        convexhull_action.triggered.connect(lambda: convexhull3d(self, self.selected_items()))
        filters_menu.addAction(convexhull_action)

        substitute_points_action = QAction(self.colorize_svg("icons/min/icons_substitute.svg", icon_colour), "Substitute", self)
        substitute_points_action.setToolTip("Substitute Points")
        substitute_points_action.setEnabled(True)
        substitute_points_action.triggered.connect(lambda: substitute_points(self))
        filters_menu.addAction(substitute_points_action)

        fill_holes_action = QAction(self.colorize_svg("icons/min/hexagon.svg", icon_colour), "delaunay3d", self)
        fill_holes_action.setToolTip("Substitute Points")
        fill_holes_action.setEnabled(False)
        # fill_holes_action.triggered.connect(lambda: ball_pivoting_triangulation(self, self.selected_items()))
        filters_menu.addAction(fill_holes_action)



        filter_points_by_hull_footprint_action = QAction(self.colorize_svg("icons/min/icons_hull_footprint.svg", icon_colour), "Hull Footprint", self)
        filter_points_by_hull_footprint_action.setToolTip("Filter points based on a hull footprint")
        filter_points_by_hull_footprint_action.setEnabled(True)
        filter_points_by_hull_footprint_action.triggered.connect(lambda: filter_points_by_hull_footprint(self, self.selected_items()))
        filters_menu.addAction(filter_points_by_hull_footprint_action)

        between_distance_action = QAction(self.colorize_svg("icons/min/icons_between_distance.svg", icon_colour), "Between Distance", self)
        between_distance_action.setToolTip("Filter points based on their distances")
        between_distance_action.setEnabled(True)
        between_distance_action.triggered.connect(lambda: filter_points_by_distance(self, self.selected_items()))
        filters_menu.addAction(between_distance_action)

        # noise_removal_action = QAction(self.colorize_svg("icons/min/hexagon.svg", icon_colour), "Noise Removal", self)
        # noise_removal_action.setToolTip("Feature not yet implemented")
        # noise_removal_action.setEnabled(False)  # Not implemented yet
        # filters_menu.addAction(noise_removal_action)
        #
        # segmentation_action = QAction(self.colorize_svg("icons/min/hexagon.svg", icon_colour), "Segmentation", self)
        # segmentation_action.setToolTip("Feature not yet implemented")
        # segmentation_action.setEnabled(False)  # Not implemented yet
        # filters_menu.addAction(segmentation_action)
        #
        # color_mapping_action = QAction(self.colorize_svg("icons/min/hexagon.svg", icon_colour), "Color Mapping", self)
        # color_mapping_action.setToolTip("Feature not yet implemented")
        # color_mapping_action.setEnabled(False)  # Not implemented yet
        # filters_menu.addAction(color_mapping_action)

        # calculate_action = QAction(self.colorize_svg("icons/min/hexagon.svg", icon_colour), "Calculate", self)
        # calculate_action.setToolTip("Sample the pointcloud data")
        # calculate_action.triggered.connect(self.calculate_stats)
        # # add_bounding_box_action.triggered.connect(lambda: boundingbox3d(self, self.selected_items()))
        # tools_menu.addAction(calculate_action)

        remove_items_action = QAction(self.colorize_svg("icons/min/icons_remove_items.svg", icon_colour), "Remove Items", self)
        remove_items_action.setToolTip("Remove selected items from the workspace")
        remove_items_action.setEnabled(True)
        remove_items_action.triggered.connect(self.remove_selected_items)
        tools_menu.addAction(remove_items_action)

        # Analysis Menu
        analysis_menu = menu_bar.addMenu("Analysis")

        segmentation_menu = analysis_menu.addMenu("Segmentation")

        dbscan_action = QAction(self.colorize_svg("icons/min/icons_dbscan_clustering.svg", icon_colour), "DBSCAN Clustering", self)
        dbscan_action.setToolTip("Perform DBSCAN clustering on the pointcloud")
        dbscan_action.setEnabled(True)
        dbscan_action.triggered.connect(lambda: dbscan_analysis(self, self.selected_items()))
        segmentation_menu.addAction(dbscan_action)

        poisson_surface_reconstruction_action = QAction(self.colorize_svg("icons/min/icons_poisson_surface_reconstruction.svg", icon_colour), "Poisson Surface Reconstruction", self)
        poisson_surface_reconstruction_action.setToolTip("Compute the 3D convex hull of the pointcloud")
        poisson_surface_reconstruction_action.setEnabled(True)
        poisson_surface_reconstruction_action.triggered.connect(lambda: poisson_surface_reconstruction(self, self.selected_items()))
        analysis_menu.addAction(poisson_surface_reconstruction_action)

        # pca_action = QAction(self.colorize_svg("icons/min/hexagon.svg", icon_colour), "Principal Component Analysis (PCA)", self)
        # pca_action.setToolTip("Feature not yet implemented")
        # pca_action.setEnabled(False)  # Not implemented yet
        # analysis_menu.addAction(pca_action)
        #
        # histogram_analysis_action = QAction(self.colorize_svg("icons/min/hexagon.svg", icon_colour), "Histogram Analysis", self)
        # histogram_analysis_action.setToolTip("Feature not yet implemented")
        # histogram_analysis_action.setEnabled(False)  # Not implemented yet
        # analysis_menu.addAction(histogram_analysis_action)
        #
        # height_map_action = QAction(self.colorize_svg("icons/min/hexagon.svg", icon_colour), "Height Map Generation", self)
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

        user_guide_action = QAction(self.colorize_svg("icons/min/icons_user_guide.svg", icon_colour), "User Guide", self)
        user_guide_action.setToolTip("Opens the User Guide")
        user_guide_action.setEnabled(True)  # Make it enabled now
        user_guide_action.triggered.connect(self.open_user_guide)
        help_menu.addAction(user_guide_action)

        keyboard_shortcuts_action = QAction(self.colorize_svg("icons/min/icons_keyboard_shortcuts.svg", icon_colour), "Keyboard Shortcuts", self)
        keyboard_shortcuts_action.setToolTip("Feature not yet implemented")
        keyboard_shortcuts_action.setEnabled(True)
        keyboard_shortcuts_action.triggered.connect(lambda: self.show_keyboard_dialog())
        help_menu.addAction(keyboard_shortcuts_action)

        about_action = QAction(self.colorize_svg("icons/min/icons_about.svg", icon_colour), "About", self)
        about_action.setToolTip("Feature not yet implemented")
        about_action.setEnabled(True)
        about_action.triggered.connect(lambda: self.show_about_dialog())
        help_menu.addAction(about_action)

        # Debug menu

        debug_menu = menu_bar.addMenu("Debug")


        debug_action = QAction(self.colorize_svg("icons/min/icons_self_data.svg", icon_colour), "self data", self)
        debug_action.setToolTip("Feature not yet implemented")
        debug_action.setEnabled(True)  # Not implemented yet
        debug_action.triggered.connect(lambda: self.debug())
        debug_menu.addAction(debug_action)

        log_action = QAction(self.colorize_svg("icons/min/icons_self_log.svg", icon_colour), "self log", self)
        log_action.setToolTip("Feature not yet implemented")
        log_action.setEnabled(True)  # Not implemented yet
        log_action.triggered.connect(lambda: self.log_output())
        debug_menu.addAction(log_action)

    def open_preferences(self):
        dialog = PreferencesDialog(self)
        dialog.exec_()

    def log_output(self):
        # Assuming self.data is a dictionary
        self.add_log_message(f"Debug: Current logging:\n{pformat(self.logging)}")
        # self.add_action_to_log(f"Log: Current logging:\n{pformat(self.logging)}")

    def add_action_to_log(self, action):
        if isinstance(action, dict):
            self.logging.update(action)
        else:
            raise ValueError("Action must be a dictionary")

    # def add_action_to_log(self, action):
    #     if isinstance(action, dict):
    #         for word, data in action.items():
    #             # Iterate over each key in the dictionary (e.g., "Translation", "Definition", etc.)
    #             for key, value in data.items():
    #                 # If the key exists in the word's entry, append the value
    #                 if key in self.logging.get(word, {}):
    #                     # If the value is already a list, append to it; otherwise, make it a list
    #                     if isinstance(self.logging[word][key], list):
    #                         self.logging[word][key].append(value)
    #                     else:
    #                         self.logging[word][key] = [self.logging[word][key], value]
    #                 else:
    #                     # If the key doesn't exist, create it and assign the value as a list
    #                     self.logging[word] = {key: [value]}
    #     else:
    #         raise ValueError("Action must be a dictionary")

    def show_right_click_menu(self, position: QPoint):
        """Display a context menu at the right-click position with options tailored to the selected item."""
        icon_colour = "#ffa02f"

        item = self.tree.itemAt(position)

        if item:
            menu = QMenu(self)
            parent_item = item.parent()

            # Common Option: Remove Item
            action_remove = QAction(self.colorize_svg("icons/min/icons_remove_items.svg", icon_colour), "Remove", self)
            action_remove.setToolTip("Remove this item from the workspace")
            action_remove.triggered.connect(lambda: self.delete_item(item, is_child=bool(parent_item)))
            menu.addAction(action_remove)

            # Show Properties
            properties_action = QAction(self.colorize_svg("icons/min/icons_properties.svg", icon_colour), "Properties", self)
            properties_action.setToolTip("Show properties of this item")
            properties_action.triggered.connect(lambda: self.show_properties(item))
            menu.addAction(properties_action)

            # Color Management
            change_color_action = QAction(self.colorize_svg("icons/min/icons_change_colour.svg", icon_colour), "Change Color", self)
            change_color_action.setToolTip("Change the color of this point cloud")
            change_color_action.triggered.connect(lambda: self.change_point_cloud_color(item))
            menu.addAction(change_color_action)

            # Add "Revert to Original Color" only if the color has been changed (stored in self.original_colors)
            # if item.text(0) in self.original_colors:
            revert_color_action = QAction(self.colorize_svg("icons/min/icons_revert_colour.svg", icon_colour), "Revert to Original Color", self)
            revert_color_action.setToolTip("Revert the point cloud to its original color")
            revert_color_action.triggered.connect(lambda: self.revert_point_cloud_color(item))
            menu.addAction(revert_color_action)

            if parent_item:
                action_export = QAction(self.colorize_svg("icons/min/icons_export.svg", icon_colour), "Export", self)
                action_export.setToolTip("Export this item to a file")
                action_export.triggered.connect(lambda: export_item(self, self.selected_items()))  # Passing `self` and the selected item
                menu.addAction(action_export)

            else:  # Parent item-specific options
                action_rename = QAction(self.colorize_svg("icons/min/hexagon.svg", icon_colour), "Rename", self)
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

            # self.add_log_message(f"add_child_to_tree_and_data: Created new parent item '{parent_name}' in tree.")

        # Check if the parent exists in the data dictionary; create it if not
        if parent_name not in self.data:
            self.data[parent_name] = {}
            # self.add_log_message(f"add_child_to_tree_and_data: Created new parent '{parent_name}' in data dictionary.")

        # Add the child item to the parent in the tree
        child_item = QTreeWidgetItem([child_name])
        child_item.setCheckState(0, Qt.Checked)  # Initialize checkbox as checked
        child_item.setFlags(child_item.flags() | Qt.ItemIsUserCheckable)
        parent_item.addChild(child_item)
        self.tree.expandItem(parent_item)

        # self.add_log_message(
        #     f"add_child_to_tree_and_data: Adding child '{child_name}' under parent '{parent_name}' in tree.")

        # Add the child data to the dictionary under the parent
        self.data[parent_name][child_name] = data

        # Ensure the point cloud is added to the Open3D viewer
        self.o3d_viewer.add_item(data, parent_name, child_name)
        # self.add_log_message(f"add_child_to_tree_and_data: '{child_name}' added to Open3D viewer.")

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

    # def add_axis(self, length=1.0):
    #     """Handles importing a point cloud and adding it to the tree and data dictionary."""
    #     try:
    #         axis = self.create_axis()
    #
    #         # Add the point cloud as a child under the file name
    #         self.add_child_to_tree_and_data(
    #             parent_name="Display",
    #             child_name="xyz-axis",
    #             data=axis
    #         )
    #
    #         self.add_log_message(f"Axis added to display.")
    #     except Exception as e:
    #         self.add_log_message(f"Failed to add point cloud: {str(e)}")

    def toggle_axis(self):
        """Toggles the visibility of the XYZ axis in the Open3D viewer."""
        self.axis_visible = not self.axis_visible
        self.o3d_viewer.toggle_xyz_axis_visibility()  # Call the viewer method to toggle the axis
        self.log_window.add_message(f"XYZ Axis is now {'visible' if self.axis_visible else 'hidden'}.")
        # print(f"XYZ Axis is now {'visible' if self.axis_visible else 'hidden'}.")


    def toggle_bbox(self):
        self.bbox_visible = not self.bbox_visible
        self.o3d_viewer.toggle_bounding_box_visibility()  # Call the viewer method to toggle the axis
        self.log_window.add_message(f"Bounding Box is now {'visible' if self.bbox_visible else 'hidden'}.")

    def toggle_obbox(self):
        self.obbox_visible = not self.obbox_visible
        self.o3d_viewer.toggle_oriented_bounding_box_visibility()  # Call the viewer method to toggle the axis
        self.log_window.add_message(f"Oriented Bounding Box is now {'visible' if self.obbox_visible else 'hidden'}.")

    def toggle_labels3d(self):
        self.labels3d = not self.labels3d
        self.o3d_viewer.toggle_labels3d()  # Call the viewer method to toggle the axis
        self.log_window.add_message(f"Tick Marks are now {'visible' if self.labels3d else 'hidden'}.")



    #####
    # Experimental
    def convert(self):
        pass

    import json
    from pathlib import Path

    def get_theme(self):
        # Default behavior: don't show splash screen unless theme is valid
        config_path = self.fetch_config()

        # Load theme from config if available
        if Path(config_path).exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    theme = config.get("theme", "none")

                    if theme and theme.lower() != "none":
                        # Construct the path for the theme directory
                        theme_dir = Path(f"themes/{theme.lower()}")  # Adjust for lowercase theme names

                        # Check if the theme directory exists
                        if theme_dir.exists() and theme_dir.is_dir():
                            # Prepare paths for the 3 QSS files
                            splash_qss = theme_dir / "splash.qss"
                            main_qss = theme_dir / "main.qss"
                            custom_qss = theme_dir / "custom.qss"

                            # Initialize a string to hold all QSS content
                            full_stylesheet = ""

                            # Check and read each QSS file if it exists
                            for file in [main_qss, splash_qss, custom_qss]:
                                if file.exists():
                                    print(f"Reading {file}")  # Debugging: which file is being read
                                    full_stylesheet += file.read_text(encoding="utf-8") + "\n"  # Add file content
                                else:
                                    print(f"{file} not found.")  # Debugging: file not found

                            # Check if any QSS file was successfully read
                            if full_stylesheet:
                                print(
                                    f"Combined stylesheet length: {len(full_stylesheet)}")  # Debugging: stylesheet length
                                return full_stylesheet  # Return the combined stylesheet

                            else:
                                print("Error: No valid QSS files found in theme folder.")
                        else:
                            print(f"Theme directory '{theme}' not found or is not a directory. No theme applied.")
                    else:
                        print("No theme specified or 'none' theme selected. No theme applied.")
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in config file. No theme applied.")
        else:
            print("Config file not found. No theme applied.")

        # return None  # Return None if no theme or files are found


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

    try:
        report(version='PointCloud Processing Pro 3 1.0.0')
    except IOError:
        print('export log failed')

    show_splash = True
    window = MainWindow()
    theme = window.get_theme()
    app.setStyleSheet(theme)
    splash = SplashScreen()
    splash.exec_()  # This blocks until the splash screen is closed

    # Proceed with launching MainWindow
    window.resize(400, 800)
    window.o3d_viewer.show_window()
    window.show()



    sys.exit(app.exec_())

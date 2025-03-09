import numpy as np
import open3d as o3d
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton,
    QHBoxLayout, QDialogButtonBox, QDoubleSpinBox, QSpinBox, QLineEdit,
    QTextEdit, QSlider, QApplication, QFormLayout, QFileDialog, QMessageBox
)

from PyQt5.QtSvg import QSvgWidget

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QDialog, QDialogButtonBox, QPushButton
from PyQt5.QtCore import Qt


class KeyboardShortcutsDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Set up the dialog window
        self.setWindowTitle("Keyboard Shortcuts")
        self.setModal(True)

        # Layout for the dialog content
        layout = QVBoxLayout()

        # Label with keyboard shortcuts info
        shortcuts_text = """
        <h3>[Open3D] -- Mouse view control --</h3>
        <ul>
            <li><b>Left button + drag</b>: Rotate.</li>
            <li><b>Ctrl + left button + drag</b>: Translate.</li>
            <li><b>Wheel button + drag</b>: Translate.</li>
            <li><b>Shift + left button + drag</b>: Roll.</li>
            <li><b>Wheel</b>: Zoom in/out.</li>
        </ul>

        <h3>[Open3D] -- Keyboard view control --</h3>
        <ul>
            <li><b>/</b>: Increase/decrease field of view.</li>
            <li><b>R</b>: Reset view point.</li>
            <li><b>Ctrl/Cmd + C</b>: Copy current view status into clipboard.</li>
            <li><b>Ctrl/Cmd + V</b>: Paste view status from clipboard.</li>
        </ul>

        <h3>[Open3D] -- General control --</h3>
        <ul>
            <li><b>Q, Esc</b>: Exit window.</li>
            <li><b>H</b>: Print help message.</li>
            <li><b>P, PrtScn</b>: Take a screen capture.</li>
            <li><b>D</b>: Take a depth capture.</li>
            <li><b>O</b>: Take a capture of current rendering settings.</li>
            <li><b>Alt + Enter</b>: Toggle between full screen and windowed mode.</li>
        </ul>

        <h3>[Open3D] -- Render mode control --</h3>
        <ul>
            <li><b>L</b>: Turn on/off lighting.</li>
            <li><b>+/-</b>: Increase/decrease point size.</li>
            <li><b>Ctrl + +/-</b>: Increase/decrease width of geometry::LineSet.</li>
            <li><b>N</b>: Turn on/off point cloud normal rendering.</li>
            <li><b>S</b>: Toggle between mesh flat shading and smooth shading.</li>
            <li><b>W</b>: Turn on/off mesh wireframe.</li>
            <li><b>B</b>: Turn on/off back face rendering.</li>
            <li><b>I</b>: Turn on/off image zoom in interpolation.</li>
            <li><b>T</b>: Toggle among image render (no stretch / keep ratio / freely stretch).</li>
        </ul>

        <h3>[Open3D INFO] -- Color control --</h3>
        <ul>
            <li><b>0..4,9</b>: Set point cloud color option.
                <ul>
                    <li><b>0</b>: Default behavior, renders the point cloud in its original colors.</li>
                    <li><b>1</b>: Render the point cloud using the actual point color (if available).</li>
                    <li><b>2</b>: Color points based on the <i>x</i> coordinate value (mapping the x-coordinate to a color scale).</li>
                    <li><b>3</b>: Color points based on the <i>y</i> coordinate value (mapping the y-coordinate to a color scale).</li>
                    <li><b>4</b>: Color points based on the <i>z</i> coordinate value (mapping the z-coordinate to a color scale).</li>
                    <li><b>9</b>: Color points based on their normals, where the normal vector is mapped to colors (usually with red, green, and blue representing the different axes of the vector).</li>
                </ul>
            </li>
            <li><b>Ctrl + 0..4,9</b>: Set mesh color option.
                <ul>
                    <li><b>0</b>: Default behavior for meshes, rendering them in a uniform gray color.</li>
                    <li><b>1</b>: Render mesh with the same color as the point cloud (if point cloud color exists).</li>
                    <li><b>2</b>: Color the mesh based on the <i>x</i> coordinate value (mapping the x-coordinate to a color scale).</li>
                    <li><b>3</b>: Color the mesh based on the <i>y</i> coordinate value (mapping the y-coordinate to a color scale).</li>
                    <li><b>4</b>: Color the mesh based on the <i>z</i> coordinate value (mapping the z-coordinate to a color scale).</li>
                    <li><b>9</b>: Color the mesh based on normals, similar to point cloud coloring, using the normal vector.</li>
                </ul>
            </li>
            <li><b>Shift + 0..4</b>: Color map options for rendering.
                <ul>
                    <li><b>0</b>: Use a grayscale color map for the point cloud or mesh, where color intensity reflects depth or coordinate values.</li>
                    <li><b>1</b>: Apply a <b>JET</b> color map, a spectrum of colors from blue to red, often used for heatmaps or scientific data visualization.</li>
                    <li><b>2</b>: Use the <b>SUMMER</b> color map, which has a gradient from green to yellow, commonly used for terrain mapping.</li>
                    <li><b>3</b>: Use the <b>WINTER</b> color map, which is a gradient from blue to green, giving a cool color palette.</li>
                    <li><b>4</b>: Use the <b>HOT</b> color map, a spectrum from black through red, orange, yellow, and white, typically used for heatmaps.</li>
                </ul>
            </li>
        </ul>
        """




        # Create the label for displaying the shortcuts
        shortcuts_label = QLabel(shortcuts_text)
        shortcuts_label.setTextFormat(Qt.RichText)  # Set text format to rich text
        shortcuts_label.setOpenExternalLinks(True)  # Enable clickable links
        shortcuts_label.setAlignment(Qt.AlignTop)

        # Add the label to the layout
        layout.addWidget(shortcuts_label)

        # Add a Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)

        # Set the layout for the dialog
        self.setLayout(layout)


from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtSvg import QSvgWidget

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("About")
        self.setFixedSize(350, 200)

        layout = QVBoxLayout()

        # App info
        about_label = QLabel(
            "<h2>PCPro 3</h2>"
            "<p><b>Version:</b> 2025 1.0.0</p>"
            "<p><b>Author:</b> Gary Nobles</p>"
            "<p><b>Description:</b> A Pointcloud-focused application designed to <br/> enhance productivity and streamline workflows.</p>"
            "<p><b>License:</b> GNU GENERAL PUBLIC LICENSE</p>"
        )
        about_label.setOpenExternalLinks(True)
        about_label.setAlignment(Qt.AlignCenter)

        # GitHub Icon & Link Layout
        github_layout = QHBoxLayout()

        # GitHub SVG Icon (color set to white)
        self.github_icon = QSvgWidget()
        self.github_icon.load(b'''<svg xmlns="http://www.w3.org/2000/svg" height="30" fill="white" viewBox="0 0 512 512">
        <path d="M256,32C132.3,32,32,132.3,32,256c0,99.9,64.8,184.6,154.7,214.7c11.3,2.1,15.5-4.9,15.5-11V421
        c-62.9,13.7-76.2-30.4-76.2-30.4c-10.3-26.2-25.2-33.2-25.2-33.2c-20.6-14.1,1.6-13.8,1.6-13.8c22.8,1.6,34.8,23.4,34.8,23.4
        c20.2,34.6,53,24.6,65.9,18.8c2.1-14.6,7.9-24.6,14.4-30.3c-50.2-5.7-103-25.1-103-111.8c0-24.7,8.8-44.9,23.2-60.7
        c-2.3-5.7-10.1-28.5,2.2-59.4c0,0,19-6.1,62.3,23.2c18-5,37.3-7.5,56.5-7.6c19.2,0.1,38.5,2.6,56.5,7.6
        c43.3-29.3,62.3-23.2,62.3-23.2c12.3,30.9,4.5,53.7,2.2,59.4c14.4,15.8,23.2,36,23.2,60.7c0,86.9-52.9,106-103.2,111.6
        c8.1,7,15.5,20.9,15.5,42.2v62.6c0,6.2,4.2,13.2,15.6,11C415.2,440.6,480,355.9,480,256C480,132.3,379.7,32,256,32z"/>
        </svg>''')
        self.github_icon.setFixedSize(30, 30)

        # GitHub Link Label
        github_label = QLabel('<a href="https://github.com/SpatialDigger/PCPro3">GitHub Repository</a>')
        github_label.setOpenExternalLinks(True)
        github_label.setAlignment(Qt.AlignCenter)

        # Apply custom styling to the hyperlink
        github_label.setStyleSheet("""
            a {
                color: #1f77b4; /* Set color to a blue shade */
                text-decoration: none; /* Remove underline */
                font-weight: bold; /* Make the text bold */
            }
            a:hover {
                color: #ff6347; /* Change color to a red-orange when hovered */
                text-decoration: underline; /* Add underline on hover */
            }
        """)

        # Clickable icon - open GitHub on click
        self.github_icon.mousePressEvent = self.open_github

        github_layout.addWidget(self.github_icon)
        github_layout.addWidget(github_label)
        github_layout.setAlignment(Qt.AlignCenter)

        # Add widgets to layout
        layout.addWidget(about_label)
        layout.addLayout(github_layout)

        self.setLayout(layout)

    def open_github(self, event):
        QDesktopServices.openUrl(QUrl("https://github.com/SpatialDigger/PCPro3"))


class ImportPointCloudDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Point Cloud")

        self.layout = QVBoxLayout()

        # File path input
        file_path_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Enter or browse file path...")
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        file_path_layout.addWidget(self.file_path_edit)
        file_path_layout.addWidget(self.browse_button)
        self.layout.addLayout(file_path_layout)

        # Spatial transformation options
        self.spatial_layout = QFormLayout()

        self.layout.addLayout(self.spatial_layout)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def browse_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Point Cloud Files (*.ply *.pcd *.xyz *.xyzrgb *.pts *.las)")
        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            self.file_path_edit.setText(selected_file)
            self.parent().add_log_message(f"Selected file: {selected_file}")
        else:
            self.parent().add_log_message("File selection canceled.")

    def get_settings(self):
        return {
            "file_path": self.file_path_edit.text(),
            # "localize_x": self.localize_x_checkbox.isChecked(),
            # "x_digits": self.x_digits_spinbox.value(),
            # "localize_y": self.localize_y_checkbox.isChecked(),
            # "y_digits": self.y_digits_spinbox.value(),
            # "localize_z": self.localize_z_checkbox.isChecked(),
        }

class PoissonSurfaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Poisson Surface Reconstruction Parameters")

        # Layout for dialog
        layout = QVBoxLayout(self)

        # Depth parameter input
        self.depth_input = QLineEdit("9")  # Default depth of 9
        layout.addWidget(QLabel("Depth (higher = more details):"))
        layout.addWidget(self.depth_input)

        # Width parameter input (optional for user)
        self.width_input = QLineEdit("0")  # Optional width parameter
        layout.addWidget(QLabel("Width (optional, 0 for default):"))
        layout.addWidget(self.width_input)

        # Scale parameter input (optional for user)
        self.scale_input = QLineEdit("1.0")  # Optional scale parameter
        layout.addWidget(QLabel("Scale (optional, default is 1.0):"))
        layout.addWidget(self.scale_input)

        # Buttons for OK and Cancel
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Apply")
        self.cancel_button = QPushButton("Cancel")

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def get_parameters(self):
        """Retrieve parameters from the dialog"""
        depth = int(self.depth_input.text())
        width = int(self.width_input.text()) if self.width_input.text() else 0
        scale = float(self.scale_input.text())
        return depth, width, scale

class DistanceFilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Distance Filter Settings")
        self.setModal(True)

        layout = QVBoxLayout()

        # Minimum distance input field
        self.min_distance_label = QLabel("Minimum Distance:")
        self.min_distance_input = QDoubleSpinBox()
        self.min_distance_input.setRange(0.0, 1000.0)
        self.min_distance_input.setValue(0.05)  # Default value

        # Comparison type selection dropdown
        self.comparison_type_label = QLabel("Comparison Type:")
        self.comparison_type_combo = QComboBox()
        self.comparison_type_combo.addItems([
            "Greater Than", "Greater Than or Equal To",
            "Less Than", "Less Than or Equal To",
            "Equal To", "Not Equal To"
        ])

        # Add inputs to the form layout
        form_layout = QFormLayout()
        form_layout.addRow(self.min_distance_label, self.min_distance_input)
        form_layout.addRow(self.comparison_type_label, self.comparison_type_combo)

        layout.addLayout(form_layout)

        # Dialog buttons: Ok and Cancel
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        # Set the dialog's layout
        self.setLayout(layout)

    def get_min_distance(self):
        """Returns the entered minimum distance."""
        return self.min_distance_input.value()

    def get_comparison_type(self):
        """Returns the selected comparison type."""
        return self.comparison_type_combo.currentText()

class SampleDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sample Pointcloud")

        layout = QVBoxLayout(self)

        # Sample type input (dropdown)
        self.sample_type_label = QLabel("Sample Type:", self)
        layout.addWidget(self.sample_type_label)

        self.sample_type_combobox = QComboBox(self)
        self.sample_type_combobox.addItems(["Random Sample", "Regular Sample", "Voxel Downsample"])
        self.sample_type_combobox.currentTextChanged.connect(self.update_visibility)
        layout.addWidget(self.sample_type_combobox)

        # Percentage input
        self.percentage_label = QLabel("Sample Percentage (%):", self)
        layout.addWidget(self.percentage_label)

        self.percentage_spinbox = QDoubleSpinBox(self)
        self.percentage_spinbox.setRange(0.01, 100.0)
        self.percentage_spinbox.setDecimals(2)  # Allow precision up to 2 decimal places
        self.percentage_spinbox.setValue(10)  # Default value
        layout.addWidget(self.percentage_spinbox)

        # Voxel size input
        self.voxel_size_label = QLabel("Voxel Size:", self)
        layout.addWidget(self.voxel_size_label)

        self.voxel_size_spinbox = QDoubleSpinBox(self)
        self.voxel_size_spinbox.setRange(0.01, 10.0)  # Adjust range as needed
        self.voxel_size_spinbox.setDecimals(2)  # Allow precision up to 2 decimal places
        self.voxel_size_spinbox.setValue(0.1)  # Default value
        layout.addWidget(self.voxel_size_spinbox)

        # Dialog buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            self
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        # Set initial visibility
        self.update_visibility()

    def update_visibility(self):
        """Toggle visibility of input fields based on the selected sampling type."""
        sample_type = self.sample_type_combobox.currentText()
        if sample_type == "Voxel Downsample":
            self.percentage_label.hide()
            self.percentage_spinbox.hide()
            self.voxel_size_label.show()
            self.voxel_size_spinbox.show()
        else:  # "Random Sample" or "Regular Sample"
            self.percentage_label.show()
            self.percentage_spinbox.show()
            self.voxel_size_label.hide()
            self.voxel_size_spinbox.hide()

    def get_percentage(self):
        """Retrieve the percentage input."""
        return self.percentage_spinbox.value()

    def get_sample_type(self):
        """Retrieve the selected sampling type."""
        return self.sample_type_combobox.currentText()

    def get_voxel_size(self):
        """Retrieve the voxel size input."""
        return self.voxel_size_spinbox.value()


class PropertiesDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Properties")
        self.layout = QVBoxLayout()

        # Initialize text area
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.layout.addWidget(self.text_area)

        # Add OK button
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.accept)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

        # Fill the properties dialog with data
        self.display_properties(data)

    @staticmethod
    def compute_mesh_volume(mesh):
        vertices = np.asarray(mesh.vertices)
        triangles = np.asarray(mesh.triangles)

        volume = 0.0
        for tri in triangles:
            v0, v1, v2 = vertices[tri[0]], vertices[tri[1]], vertices[tri[2]]
            volume += np.dot(v0, np.cross(v1, v2)) / 6.0  # Signed volume of tetrahedron

        return abs(volume)

    def display_dict_properties(self, data):
        children_info = []
        for key, value in data.items():
            if isinstance(value, o3d.geometry.Geometry):
                type_name = type(value).__name__
                children_info.append(f"{key}: {type_name}")
            else:
                children_info.append(f"{key}: {value}")
        self.text_area.setText("\n".join(children_info))

    def display_properties(self, data):
        # Get metadata
        file_path = data.get('filepath', 'unknown')
        file_name = data.get('filename', 'unknown')
        item = data.get('item', None)
        object_type = 'unknown'
        point_count = 'unknown'
        min_bound = max_bound = ('unknown', 'unknown', 'unknown')
        transform = data.get('transform_settings', 'unknown')
        extra_info = ""

        if isinstance(item, o3d.geometry.PointCloud):
            object_type = "Point Cloud"
            bbox = item.get_axis_aligned_bounding_box()
            min_bound = bbox.min_bound
            max_bound = bbox.max_bound
            point_count = len(np.asarray(item.points))
            has_normals = item.has_normals()
            has_colors = item.has_colors()
            density = point_count / bbox.volume() if bbox.volume() > 0 else 'unknown'

            extra_info = (
                f"Has Normals: {'Yes' if has_normals else 'No'}\n"
                f"Has Colors: {'Yes' if has_colors else 'No'}\n"
                f"Estimated Density: {density:.2f} points per unit³\n"
            )

        elif isinstance(item, o3d.geometry.TriangleMesh):
            object_type = "Mesh"
            bbox = item.get_axis_aligned_bounding_box()
            min_bound = bbox.min_bound
            max_bound = bbox.max_bound
            vertex_count = len(np.asarray(item.vertices))
            face_count = len(np.asarray(item.triangles))
            edges_count = self.calculate_actual_edges(item)
            non_manifold_edges = len(item.get_non_manifold_edges())  # Approximate edge count
            volume = self.compute_mesh_volume(item)

            extra_info = (
                f"Vertex Count: {vertex_count}\n"
                f"Face Count: {face_count}\n"
                f"Edge Count: {edges_count}\n"
                f"Non Manifold Edges Count: {non_manifold_edges}\n"
                f"Volume: {volume} units³\n"
            )

        elif isinstance(item, o3d.geometry.LineSet):
            object_type = "Line Set"
            bbox = item.get_axis_aligned_bounding_box()
            min_bound = bbox.min_bound
            max_bound = bbox.max_bound
            line_count = len(item.lines)
            has_colors = item.has_colors()
            total_length = sum(
                np.linalg.norm(np.asarray(item.points)[l[1]] - np.asarray(item.points)[l[0]])
                for l in item.lines
            )

            extra_info = (
                f"Line Count: {line_count}\n"
                f"Has Colors: {'Yes' if has_colors else 'No'}\n"
                f"Total Line Length: {total_length:.2f}\n"
            )

        # Display information
        info = (
            f"Object Type: {object_type}\n"
            f"File Name: {file_name}\n"
            f"File Path: {file_path}\n"
            f"Point Count: {point_count}\n"
            f"{extra_info}"
            f"Bounding Box Extents:\n"
            f"  Min Bound: X: {min_bound[0]:.2f}, Y: {min_bound[1]:.2f}, Z: {min_bound[2]:.2f}\n"
            f"  Max Bound: X: {max_bound[0]:.2f}, Y: {max_bound[1]:.2f}, Z: {max_bound[2]:.2f}\n"
            f"Translation: {transform}\n"
        )

        self.text_area.setText(info)

    def calculate_actual_edges(self, geometry_data):
        # Get the triangles and vertices
        triangles = np.asarray(geometry_data.triangles)

        # Initialize a set to store unique edges (as sorted tuples)
        edges = set()

        for tri in triangles:
            # Each triangle has 3 edges, and we want each edge represented as a sorted tuple
            for i in range(3):
                edge = tuple(sorted([tri[i], tri[(i + 1) % 3]]))  # Create a sorted edge pair
                edges.add(edge)  # Add the edge to the set

        # Return the number of unique edges
        return len(edges)


class LogWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Event Log")
        self.setFixedSize(600, 400)

        # Get screen geometry to position the dialog on the right
        screen_geometry = QApplication.desktop().availableGeometry()  # Gets the screen size
        screen_width = screen_geometry.width()
        self.move(screen_width - self.width(), 200)  # Position dialog at the right

        # Set layout and widgets
        self.layout = QVBoxLayout()

        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.layout.addWidget(self.log_text_edit)

        self.clear_button = QPushButton("Clear Log")
        self.clear_button.clicked.connect(self.clear_log)
        self.layout.addWidget(self.clear_button)

        self.setLayout(self.layout)

    def add_message(self, message):
        self.log_text_edit.append(message)

    def clear_log(self):
        self.log_text_edit.clear()


class HullFilterDialog(QDialog):
    def __init__(self, point_clouds, hulls, parent_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Points by Hull Footprint")

        self.point_clouds = point_clouds
        self.hulls = hulls
        self.parent_names = parent_names

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Select PointCloud:"))
        self.pointcloud_combobox = QComboBox()
        self.pointcloud_combobox.addItems(parent_names)
        layout.addWidget(self.pointcloud_combobox)

        layout.addWidget(QLabel("Select Hull3D(s):"))
        self.hull_combobox = QComboBox()
        self.hull_combobox.addItems([hull.name for hull in hulls])
        layout.addWidget(self.hull_combobox)

        layout.addWidget(QLabel("Select Parent Name for Filtered Data:"))
        self.parent_name_combobox = QComboBox()
        self.parent_name_combobox.addItems(parent_names)
        layout.addWidget(self.parent_name_combobox)

        self.overlap_checkbox = QCheckBox("Filter by Hull Overlap (If multiple hulls are selected)")
        layout.addWidget(self.overlap_checkbox)

        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.reset_button = QPushButton("Reset")
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.reset_button)
        layout.addLayout(button_layout)

        self.apply_button.clicked.connect(self.accept)
        self.reset_button.clicked.connect(self.reset_dialog)

    def reset_dialog(self):
        self.pointcloud_combobox.setCurrentIndex(0)
        self.hull_combobox.setCurrentIndex(0)
        self.parent_name_combobox.setCurrentIndex(0)
        self.overlap_checkbox.setChecked(False)


class DBSCANDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DBSCAN Parameters")

        layout = QVBoxLayout()

        self.eps_label = QLabel("Epsilon (eps):")
        self.eps_input = QDoubleSpinBox()
        self.eps_input.setRange(0.01, 10.0)
        self.eps_input.setValue(0.02)
        layout.addWidget(self.eps_label)
        layout.addWidget(self.eps_input)

        self.min_points_label = QLabel("Minimum Points:")
        self.min_points_input = QSpinBox()
        self.min_points_input.setRange(1, 100)
        self.min_points_input.setValue(5)
        layout.addWidget(self.min_points_label)
        layout.addWidget(self.min_points_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

    def get_eps(self):
        return self.eps_input.value()

    def get_min_points(self):
        return self.min_points_input.value()


class TransformationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Apply Spatial Transformation")

        layout = QVBoxLayout(self)

        self.tx_input = QLineEdit("0")
        self.ty_input = QLineEdit("0")
        self.tz_input = QLineEdit("0")
        layout.addWidget(QLabel("Translation (x, y, z):"))
        layout.addWidget(self.tx_input)
        layout.addWidget(self.ty_input)
        layout.addWidget(self.tz_input)

        self.rx_input = QLineEdit("0")
        self.ry_input = QLineEdit("0")
        self.rz_input = QLineEdit("0")
        layout.addWidget(QLabel("Rotation (degrees around x, y, z):"))
        layout.addWidget(self.rx_input)
        layout.addWidget(self.ry_input)
        layout.addWidget(self.rz_input)

        self.mirror_x = QCheckBox("Mirror along X-axis")
        self.mirror_y = QCheckBox("Mirror along Y-axis")
        self.mirror_z = QCheckBox("Mirror along Z-axis")

        layout.addWidget(QLabel("Mirroring:"))
        layout.addWidget(self.mirror_x)
        layout.addWidget(self.mirror_y)
        layout.addWidget(self.mirror_z)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Apply")
        self.cancel_button = QPushButton("Cancel")

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)


    def get_transformation_parameters(self):
        """Retrieves user input for transformation parameters."""
        try:
            # Convert input to floats
            translation = [
                float(self.tx_input.text()),
                float(self.ty_input.text()),
                float(self.tz_input.text()),
            ]

            rotation = [
                float(self.rx_input.text()),
                float(self.ry_input.text()),
                float(self.rz_input.text()),
            ]

            mirroring = [
                self.mirror_x.isChecked(),
                self.mirror_y.isChecked(),
                self.mirror_z.isChecked(),
            ]

            return translation, rotation, mirroring
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please enter valid numerical values for translation and rotation.")
            return [0, 0, 0], [0, 0, 0], [False, False, False]


class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        self.some_setting_label = QLabel("Some Setting:")
        self.some_setting_input = QLineEdit()
        layout.addWidget(self.some_setting_label)
        layout.addWidget(self.some_setting_input)

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.save_button.clicked.connect(self.save_preferences)
        self.cancel_button.clicked.connect(self.reject)

    def save_preferences(self):
        print(f"Saved setting: {self.some_setting_input.text()}")
        self.accept()


class ScaleFactorDialog(QDialog):
    def __init__(self, parent=None, initial_scale=0.5):
        super().__init__(parent)
        self.setWindowTitle("Select Scale Factor")

        layout = QVBoxLayout()

        self.label = QLabel(f"Scale Factor: {initial_scale}")
        layout.addWidget(self.label)

        self.scale_slider = QSlider()
        self.scale_slider.setMinimum(0)
        self.scale_slider.setMaximum(200)
        self.scale_slider.setValue(int(initial_scale * 100))
        self.scale_slider.valueChanged.connect(self.update_label)
        layout.addWidget(self.scale_slider)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def update_label(self):
        scale_value = self.scale_slider.value() / 100.0
        self.label.setText(f"Scale Factor: {scale_value:.2f}")

    def get_scale_factor(self):
        return self.scale_slider.value() / 100.0


class NormalEstimationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Normal Estimation Settings")
        self.setModal(True)

        layout = QVBoxLayout()

        # Method selection
        self.method_label = QLabel("Method:")
        self.method_combo = QComboBox()
        self.method_combo.addItems(["knn", "alpha_shape"])
        self.method_combo.currentTextChanged.connect(self.toggle_fields)

        # k-NN neighbors selection
        self.k_label = QLabel("k (Nearest Neighbors):")
        self.k_spinbox = QSpinBox()
        self.k_spinbox.setRange(1, 100)
        self.k_spinbox.setValue(12)

        # Alpha value selection
        self.alpha_label = QLabel("Alpha (Triangulation Parameter):")
        self.alpha_spinbox = QDoubleSpinBox()
        self.alpha_spinbox.setRange(0.001, 1.0)
        self.alpha_spinbox.setSingleStep(0.01)
        self.alpha_spinbox.setValue(0.03)

        # Form layout
        form_layout = QFormLayout()
        form_layout.addRow(self.method_label, self.method_combo)
        form_layout.addRow(self.k_label, self.k_spinbox)
        form_layout.addRow(self.alpha_label, self.alpha_spinbox)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

        # Initialize field visibility
        self.toggle_fields(self.method_combo.currentText())

    def toggle_fields(self, method):
        """Show/hide fields based on selected method."""
        is_knn = method == "knn"
        self.k_label.setVisible(is_knn)
        self.k_spinbox.setVisible(is_knn)
        self.alpha_label.setVisible(not is_knn)
        self.alpha_spinbox.setVisible(not is_knn)

    def get_parameters(self):
        """Returns selected parameters."""
        return {
            "method": self.method_combo.currentText(),
            "k": self.k_spinbox.value(),
            "alpha": self.alpha_spinbox.value()
        }

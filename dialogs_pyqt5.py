import numpy as np
import open3d as o3d
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton,
    QHBoxLayout, QDialogButtonBox, QDoubleSpinBox, QSpinBox, QLineEdit,
    QTextEdit, QSlider, QApplication, QFormLayout, QFileDialog
)

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

# class NormalsDialog(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Normals Parameters")
#
#         layout = QVBoxLayout()
#
#         self.eps_label = QLabel("Epsilon (eps):")
#         self.eps_input = QDoubleSpinBox()
#         self.eps_input.setRange(0.01, 10.0)
#         self.eps_input.setValue(0.02)
#         layout.addWidget(self.eps_label)
#         layout.addWidget(self.eps_input)
#
#         self.min_points_label = QLabel("Minimum Points:")
#         self.min_points_input = QSpinBox()
#         self.min_points_input.setRange(1, 100)
#         self.min_points_input.setValue(5)
#         layout.addWidget(self.min_points_label)
#         layout.addWidget(self.min_points_input)
#
#         self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
#         self.buttons.accepted.connect(self.accept)
#         self.buttons.rejected.connect(self.reject)
#         layout.addWidget(self.buttons)
#
#         self.setLayout(layout)
#
#     def get_eps(self):
#         return self.eps_input.value()
#
#     def get_min_points(self):
#         return self.min_points_input.value()





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
        self.k_spinbox.setValue(6)

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

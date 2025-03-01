import os
import numpy as np
import open3d as o3d
import laspy

from PyQt5.QtWidgets import QFileDialog

def import_mesh(parent, file_path, transform_settings):
    transform_settings={}
    """Load and process a 3D mesh."""
    add_log_message(parent, f"Importing mesh: {file_path}...")

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
            add_log_message(parent, "Associated material file found. Textures should load automatically.")
    else:
        # Attempt to load other popular formats
        mesh = o3d.io.read_triangle_mesh(file_path)

    # Verify mesh
    if not mesh or not mesh.has_vertices() or not mesh.has_triangles():
        raise ValueError("Imported mesh is empty or invalid.")

    # Enable vertex colors if available
    if mesh.has_vertex_colors():
        add_log_message(parent, "Mesh has vertex colors. They will be displayed.")
    else:
        add_log_message(parent, "Mesh does not have vertex colors.")

    # Enable textures if available
    if mesh.has_textures():
        add_log_message(parent, "Mesh has textures. They will be displayed.")
    else:
        add_log_message(parent, "Mesh does not have textures.")

    # Apply transformations if needed
    if transform_settings:
        apply_transformations(parent, mesh, transform_settings)

    file_name = os.path.basename(file_path)
    return {
        "Mesh": mesh,
        "transform_settings": parent.translation_values,
        "file_path": file_path,
        "file_name": file_name,
    }

def add_mesh(parent, file_path, transform_settings=None):
    """Handles importing a mesh and adding it to the tree and data dictionary."""
    try:
        # Import the mesh data
        data = import_mesh(parent, file_path, transform_settings)
        file_name = data["file_name"]

        # Add the mesh as a child under the file name
        parent.add_child_to_tree_and_data(
            parent_name=file_name,
            child_name="Mesh",
            data=data["Mesh"]
        )

        # Store additional metadata in the parent data dictionary
        parent.data[file_name].update({
            "transform_settings": parent.translation_values,
            "file_path": file_path,
            "file_name": file_name,
        })

        add_log_message(parent, f"Mesh successfully added for file '{file_name}'.")
    except Exception as e:
        add_log_message(parent, f"Failed to add mesh: {str(e)}")




def add_pointcloud(parent, file_path, transform_settings=None):
    """Handles importing a point cloud and adding it to the tree and data dictionary."""
    try:
        # Import the point cloud data
        data = import_pointcloud(parent, file_path, transform_settings)
        file_name = data["file_name"]

        # Add the point cloud as a child under the file name
        parent.add_child_to_tree_and_data(
            parent_name=file_name,
            child_name="Pointcloud",
            data=data["Pointcloud"]
        )

        # Store additional metadata in the parent data dictionary
        parent.data[file_name].update({
            "transform_settings": parent.translation_values,
            "file_path": file_path,
            "file_name": file_name,
        })

        add_log_message(parent, f"Point cloud successfully added for file '{file_name}'.")
    except Exception as e:
        add_log_message(parent, f"Failed to add point cloud: {str(e)}")

def import_pointcloud(parent, file_path, transform_settings):
    """Load and process a point cloud."""
    add_log_message(parent, f"Importing point cloud: {file_path}...")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.endswith(".las"):
        pointcloud = load_las_to_open3d_chunked(parent, file_path, transform_settings)
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
        "transform_settings": parent.translation_values,
        "file_path": file_path,
        "file_name": file_name,
    }


def load_las_to_open3d_chunked(parent, file_path, transform_settings, max_points=1_000_000):
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

        if hasattr(parent, 'translation_values'):
            parent.translation_values.update({"x": translate_x, "y": translate_y})
        else:
            parent.translation_values = {"x": translate_x, "y": translate_y}

        add_log_message(
            parent, f"Automatically determined translation values: translate_x={translate_x}, translate_y={translate_y}")

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


def apply_transformations(parent, mesh, transform_settings):
    """Apply transformations to the mesh based on settings."""
    add_log_message(parent, "Applying transformations...")
    if "scale" in transform_settings:
        scale_factor = transform_settings["scale"]
        mesh.scale(scale_factor, center=mesh.get_center())
    if "rotation" in transform_settings:
        rotation_matrix = transform_settings["rotation"]  # Should be a 3x3 matrix
        mesh.rotate(rotation_matrix, center=mesh.get_center())
    if "translation" in transform_settings:
        translation_vector = transform_settings["translation"]
        mesh.translate(translation_vector)


def add_log_message(parent, message):
    """Logs messages for the user."""
    if parent:
        parent.add_log_message(message)  # Assuming `add_log_message` is a method in your parent class (main window)
    else:
        print(message)  # Fallback to print if no parent is available


def open_file_dialog(parent, dialog_type):
    """Open file dialog to select files based on the type of addition (pointcloud or mesh)."""
    if dialog_type == "Pointcloud":
        file_paths, _ = QFileDialog.getOpenFileNames(
            parent, "Select Pointcloud Files", "",
            "Pointclouds (*.pcd *.las *.ply *.xyz *.xyzn *.xyzrgb *.pts)"
        )
        if file_paths:
            for file_path in file_paths:
                add_pointcloud(parent, file_path, transform_settings={})
    elif dialog_type == "Mesh":
        file_paths, _ = QFileDialog.getOpenFileNames(
            parent, "Select Mesh Files", "",
            "Meshes (*.ply *.obj *.stl *.glb *.fbx *.3mf *.off)"
        )
        if file_paths:
            for file_path in file_paths:
                add_mesh(parent, file_path, transform_settings={})
import os
import open3d as o3d
import numpy as np
import laspy
import json
from PyQt5.QtWidgets import QFileDialog

def export_item(parent, selected_items):
    if len(selected_items) != 1:
        return  # Return if the number of selected items is not exactly 1

    item = selected_items[0]  # Get the single item
    parent_item = item.parent()

    if not parent_item:
        add_log_message(parent, "Export is only supported for child items.")
        return

    parent_name = parent_item.text(0)
    child_name = item.text(0)

    if parent_name not in parent.data or child_name not in parent.data[parent_name]:
        add_log_message(parent, f"Export failed: Could not locate data for '{child_name}' under '{parent_name}'.")
        return

    obj = parent.data[parent_name][child_name]
    if isinstance(obj, o3d.geometry.PointCloud) or isinstance(obj, o3d.geometry.TriangleMesh):
        file_path = get_export_path(parent)
        if file_path:
            perform_export(parent, obj, file_path)

def get_export_path(parent):
    """Helper function to open a file dialog and get the export path."""
    file_dialog = QFileDialog(parent)
    file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    file_dialog.setNameFilters(get_export_filters())

    if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
        return file_dialog.selectedFiles()[0]
    return None

def get_export_filters():
    """Returns the available filters for export file formats."""
    return [
        "PCD Files (*.pcd)",
        "LAS Files (*.las)",
        "XYZ Files (*.xyz)",
        "PLY Files (*.ply)",
        "GeoJSON Files (*.geojson)",
    ]

def perform_export(parent, item, file_path):
    """Perform the export based on file format."""
    file_format = file_path.split('.')[-1].lower()

    action = {"Export": f"Exported {file_format} to {file_path}"}

    try:
        if file_format == "pcd":
            export_to_pcd(item, file_path)
            parent.add_to_log(action)
        elif file_format == "las":
            export_to_las(item, file_path)
            parent.add_to_log(action)
        elif file_format == "xyz":
            export_to_xyz(item, file_path)
            parent.add_to_log(action)
        elif file_format == "ply":
            export_to_ply(item, file_path)
            parent.add_to_log(action)
        elif file_format == "geojson":
            export_to_geojson(item, file_path)
            parent.add_to_log(action)
        else:
            add_log_message(parent, f"Unsupported export format: {file_format}")
            return

        add_log_message(parent, f"Exported {file_format.upper()} to {file_path}.")
        

    except Exception as e:
        add_log_message(parent, f"Export failed: {str(e)}")

def export_to_pcd(item, file_path):
    """Export point cloud to PCD format."""
    o3d.io.write_point_cloud(file_path, item, write_ascii=True)
    add_log_message(None, f"PointCloud saved to {file_path}")  # Here None is passed as the parent
    export_log(file_path)

def export_to_xyz(item, file_path):
    """Export point cloud to XYZ format."""
    o3d.io.write_point_cloud(file_path, item, write_ascii=True)
    add_log_message(None, f"PointCloud saved to {file_path}")
    export_log(file_path)

def export_to_ply(item, file_path):
    """Export to PLY format."""
    if isinstance(item, o3d.geometry.PointCloud):
        o3d.io.write_point_cloud(file_path, item, write_ascii=True)
    elif isinstance(item, o3d.geometry.TriangleMesh):
        o3d.io.write_triangle_mesh(file_path, item, write_ascii=True)
    add_log_message(None, f"Saved to {file_path}")
    export_log(file_path)

def export_to_las(point_cloud, file_path):
    """Export Open3D point cloud to LAS format."""
    points = np.asarray(point_cloud.points)
    colors = np.asarray(point_cloud.colors)
    header = laspy.LasHeader(point_format=3, version="1.4")
    las = laspy.LasData(header)
    las.x, las.y, las.z = points[:, 0], points[:, 1], points[:, 2]

    if colors.size > 0:
        las.red = (colors[:, 0] * 65535).astype(np.uint16)
        las.green = (colors[:, 1] * 65535).astype(np.uint16)
        las.blue = (colors[:, 2] * 65535).astype(np.uint16)

    las.write(file_path)
    add_log_message(None, f"LAS File saved to {file_path}")
    export_log(file_path)

def export_to_geojson(point_cloud, file_path):
    """Export Open3D point cloud to GeoJSON format."""
    points = np.asarray(point_cloud.points)
    geojson_data = {
        "type": "FeatureCollection",
        "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": point.tolist()}} for point in
                     points]
    }

    with open(file_path, 'w') as f:
        json.dump(geojson_data, f, indent=4)
    add_log_message(None, f"GeoJSON saved to {file_path}")
    export_log(file_path)

def add_log_message(parent, message):
    """Logs messages for the user."""
    if parent:
        parent.add_log_message(message)  # Assuming `add_log_message` is a method in your parent class (main window)
    else:
        print(message)  # Fallback to print if no parent is available

def export_log(parent, filepath):
    # Remove the existing extension and add .txt
    base_name = os.path.splitext(filepath)[0]
    txt_filepath = f"{base_name}.txt"

    # Write the log dictionary to the .txt file
    with open(txt_filepath, "w") as file:
        for key, value in parent.log.items():
            file.write(f"{key}: {value}\n")

    print(f"Log exported to {txt_filepath}")

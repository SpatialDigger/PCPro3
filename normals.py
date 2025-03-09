import open3d as o3d
import numpy as np

from PyQt5.QtWidgets import (
    QDialog
)

from dialogs_pyqt5 import (NormalEstimationDialog)

def compute_normals(self, selected_items):
    """Computes normals for selected point clouds using k-NN or Alpha Shape triangulation."""

    # Open the Normal Estimation Dialog
    dialog = NormalEstimationDialog(self)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        params = dialog.get_parameters()
        method = params["method"]
        k = params["k"]
        alpha = params["alpha"]
    else:
        self.add_log_message("Normal estimation was canceled.")
        return

    # Separate selected point clouds along with their parents
    selected_point_clouds = []
    parent_child_mapping = {}  # Maps point clouds to their respective parents

    for item in selected_items:
        parent_name = item.parent().text(0) if item.parent() else None
        child_name = item.text(0)
        key = (parent_name, child_name)

        if key in self.o3d_viewer.items:
            o3d_item = self.o3d_viewer.items[key]
            if isinstance(o3d_item, o3d.geometry.PointCloud):
                selected_point_clouds.append(o3d_item)
                parent_child_mapping[o3d_item] = parent_name

    if not selected_point_clouds:
        self.add_log_message("No valid point clouds selected.")
        return

    # Process each selected point cloud
    processed_clouds = []
    for pcd in selected_point_clouds:
        if method == "knn":
            pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamKNN(knn=k))
            pcd.orient_normals_consistent_tangent_plane(k)
            self.add_log_message(f"Computed normals for '{parent_child_mapping[pcd]}' using k-NN.")
            processed_clouds.append(pcd)

        elif method == "alpha_shape":
            mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, alpha)
            mesh.compute_vertex_normals()
            self.add_log_message(f"Computed normals for '{parent_child_mapping[pcd]}' using Alpha Shape.")
            processed_clouds.append(mesh)

        else:
            self.add_log_message("Invalid method. Use 'knn' or 'alpha_shape'.")
            return

    # Add the processed point clouds/meshes back to their respective parents
    base_child_name = "computed_normals"

    def generate_unique_name(base_name, existing_children):
        counter = 1
        unique_name = base_name
        while unique_name in existing_children:
            unique_name = f"{base_name}_{counter}"
            counter += 1
        return unique_name

    for processed_pc, original_pc in zip(processed_clouds, selected_point_clouds):
        parent_name = parent_child_mapping.get(original_pc, "Processed Point Clouds")
        existing_children = self.data.get(parent_name, {}).keys()

        child_name = generate_unique_name(base_child_name, existing_children)

        # Add the new point cloud/mesh to the tree and data
        # self.add_child_to_tree_and_data(parent_name, child_name, processed_pc)

        self.add_log_message(f"Computed normals '{child_name}' under '{parent_name}'.")



def invert_normals(self, selected_items):
    """Inverts the normals of selected point clouds."""

    # Separate selected point clouds along with their parents
    selected_point_clouds = []
    parent_child_mapping = {}

    for item in selected_items:
        parent_name = item.parent().text(0) if item.parent() else None
        child_name = item.text(0)
        key = (parent_name, child_name)

        if key in self.o3d_viewer.items:
            o3d_item = self.o3d_viewer.items[key]
            if isinstance(o3d_item, o3d.geometry.PointCloud):
                if o3d_item.has_normals():
                    selected_point_clouds.append(o3d_item)
                    parent_child_mapping[o3d_item] = parent_name
                else:
                    self.add_log_message(f"Point cloud '{child_name}' has no normals to invert.")

    if not selected_point_clouds:
        self.add_log_message("No valid point clouds with normals selected.")
        return

    # Invert normals for each selected point cloud
    inverted_clouds = []
    for pcd in selected_point_clouds:
        pcd.normals = o3d.utility.Vector3dVector(-np.asarray(pcd.normals))
        self.add_log_message(f"Inverted normals for '{parent_child_mapping[pcd]}'.")
        inverted_clouds.append(pcd)

    # Add the inverted point clouds back to their respective parents
    base_child_name = "inverted_normals"

    def generate_unique_name(base_name, existing_children):
        counter = 1
        unique_name = base_name
        while unique_name in existing_children:
            unique_name = f"{base_name}_{counter}"
            counter += 1
        return unique_name

    for inverted_pc, original_pc in zip(inverted_clouds, selected_point_clouds):
        parent_name = parent_child_mapping.get(original_pc, "Processed Point Clouds")
        existing_children = self.data.get(parent_name, {}).keys()

        child_name = generate_unique_name(base_child_name, existing_children)

        # Add the new point cloud to the tree and data
        # self.add_child_to_tree_and_data(parent_name, child_name, inverted_pc)

        self.add_log_message(f"Inverted normals '{child_name}' under '{parent_name}'.")

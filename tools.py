import open3d as o3d
import numpy as np
import random
import time
from dialogs_pyqt5 import (
    DistanceFilterDialog, SampleDialog, PoissonSurfaceDialog, TransformationDialog, DBSCANDialog
                     )
from shapely.geometry import Point, Polygon, MultiLineString, LineString
from shapely.ops import unary_union
from sklearn.cluster import DBSCAN
import scipy.spatial
import trimesh
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel, QDialogButtonBox, QLineEdit, QHBoxLayout

def apply_spatial_transformation(self, selected_items):
    """Applies spatial transformation to selected point clouds."""
    # selected_items = self.selected_items()

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

                        self.add_action_to_log(action={f"{self.data[key[0]]}": {"Translation": translation}})

                    except Exception as e:
                        self.add_log_message(f"Failed to apply manual translation to '{key[1]}': {e}")
                        continue

                if any(rotation):
                    self.add_log_message(f"Applying rotation {rotation} to point cloud '{key[1]}'.")
                    rotation_radians = [np.radians(angle) for angle in rotation]
                    rotation_matrix = o3d.geometry.get_rotation_matrix_from_xyz(rotation_radians)
                    point_cloud.rotate(rotation_matrix, center=point_cloud.get_center())

                    self.add_action_to_log(action={f"{self.data[key[0]]}": {"Rotation": rotation}})

                if any(mirroring):
                    self.add_log_message(f"Applying mirroring {mirroring} to point cloud '{key[1]}'.")
                    mirror_matrix = np.eye(4)
                    mirror_matrix[0, 0] = -1 if mirroring[0] else 1
                    mirror_matrix[1, 1] = -1 if mirroring[1] else 1
                    mirror_matrix[2, 2] = -1 if mirroring[2] else 1
                    point_cloud.transform(mirror_matrix)

                    self.add_action_to_log(action={f"{self.data[key[0]]}": {"Mirroring": mirroring}})

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

def convexhull3d(self, selected_items):
    # Retrieve selected items from the tree
    # selected_items = self.selected_items()

    print("Not opening ConvexHull dialog...")  # Debugging
    for item in selected_items:
        # Determine the file name and check hierarchy
        if item.parent():  # If it's a child item
            parent_name = item.parent().text(0)  # Parent holds the file name
            child_name = item.text(0)  # Child text represents the cloud type
        else:  # If it's a top-level (parent) item
            self.add_log_message("Top-level items cannot be sampled directly.")
            continue

        # Retrieve the point cloud data
        data = self.data.get(parent_name)
        if not data:
            self.add_log_message(f"No valid point cloud found for {parent_name}. Skipping.")
            continue
        point_dataset = data[child_name]

        # Perform convexhull
        def hull3d(point_cloud):
            # Compute the convex hull of the point cloud
            hull, _ = point_cloud.compute_convex_hull()

            # Create a LineSet from the convex hull
            hull_ls = o3d.geometry.LineSet.create_from_triangle_mesh(hull)
            return hull_ls

        hull_tri = hull3d(point_dataset)

        if not hull_tri:
            self.add_log_message(f"Sampling failed for {parent_name}.")
            continue

        # Name and store the sampled point cloud
        # sampled_file_name = "Hull3D"
        self.data[parent_name]["Hull3D"] = hull_tri

        # Add the sampled point cloud to the tree and viewer
        self.add_child_to_tree_and_data(parent_name, "Hull3D", hull_tri)

        # Add Hull to the viewer
        self.o3d_viewer.add_item(hull_tri, parent_name, "Hull3D")
        self.add_log_message(f"Sampled pointcloud added: Hull3D")

    # Update the viewer
    self.o3d_viewer.update_viewer()
    self.add_log_message("Viewer updated with ConvexHull.")

def poisson_surface_reconstruction(self, selected_items):
    # Show dialog to get parameters (depth, width, scale)
    dialog = PoissonSurfaceDialog(self)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        depth, width, scale = dialog.get_parameters()
    else:
        self.add_log_message("Poisson surface reconstruction cancelled.")
        return

    # Retrieve selected items from the tree
    print("Not opening Poisson Surface Reconstruction dialog...")  # Debugging
    for item in selected_items:
        # Determine the file name and check hierarchy
        if item.parent():  # If it's a child item
            parent_name = item.parent().text(0)  # Parent holds the file name
            child_name = item.text(0)  # Child text represents the cloud type
        else:  # If it's a top-level (parent) item
            self.add_log_message("Top-level items cannot be processed directly.")
            continue

        # Retrieve the point cloud data
        data = self.data.get(parent_name)
        if not data:
            self.add_log_message(f"No valid point cloud found for {parent_name}. Skipping.")
            continue
        point_dataset = data[child_name]

        # Perform Poisson surface reconstruction
        def reconstruct_surface(point_cloud, depth, width, scale):
            # Step 1: Estimate normals only if they have not been calculated already
            if not point_cloud.has_normals():
                print("Estimating normals...")  # Debugging
                point_cloud.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

            # Step 2: Perform Poisson surface reconstruction (depth controls the level of detail)
            mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(point_cloud, depth, width=width, scale=scale)

            return mesh

        reconstructed_mesh = reconstruct_surface(point_dataset, depth, width, scale)

        if not reconstructed_mesh:
            self.add_log_message(f"Poisson surface reconstruction failed for {parent_name}.")
            continue

        # Name and store the reconstructed mesh
        self.data[parent_name]["PoissonSurface"] = reconstructed_mesh

        # Add the reconstructed mesh to the tree and viewer
        self.add_child_to_tree_and_data(parent_name, "PoissonSurface", reconstructed_mesh)

        # Add the mesh to the viewer
        self.o3d_viewer.add_item(reconstructed_mesh, parent_name, "PoissonSurface")
        self.add_log_message(f"Poisson surface reconstructed and added for: {parent_name}")

    # Update the viewer
    self.o3d_viewer.update_viewer()
    self.add_log_message("Viewer updated with Poisson surface reconstruction.")

    self.add_action_to_log(action={f"{self.data[parent_name]}": {"Poisson Surface Reconstruction": {"depth": depth, "width":width, "scale": scale}}})

def filter_points_by_distance(self, selected_items):
    """Filters points from two selected point clouds based on the minimum distance between them."""

    # Retrieve selected items from the GUI or context
    # selected_items = self.selected_items()

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

    if len(selected_point_clouds) != 2:
        self.add_log_message("Exactly two point clouds must be selected.")
        return

    # Extract the two point clouds
    pc1, pc2 = selected_point_clouds

    # Show the distance filter dialog to get the parameters
    dialog = DistanceFilterDialog(self)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        min_distance = dialog.get_min_distance()
        comparison_type = dialog.get_comparison_type()

        # Compute the filtered point clouds based on distance
        filtered_pc1, filtered_pc2 = filter_points_by_distance_logic(pc1, pc2, min_distance, comparison_type)

        if filtered_pc1 is None or filtered_pc2 is None:
            self.add_log_message("No points met the distance criteria.")
            return

        # Generate the child names for the new point clouds
        base_child_name = "filtered_pointcloud_by_distance"

        def generate_unique_name(base_name, existing_children):
            counter = 1
            unique_name = base_name
            while unique_name in existing_children:
                unique_name = f"{base_name}_{counter}"
                counter += 1
            return unique_name

        # Add the filtered point clouds to their respective parents
        for filtered_pc, original_pc in zip([filtered_pc1, filtered_pc2], [pc1, pc2]):
            parent_name = parent_child_mapping.get(original_pc, "Filtered Point Clouds")
            existing_children = self.data.get(parent_name, {}).keys()

            child_name = generate_unique_name(base_child_name, existing_children)

            # Add the new point cloud to the tree and data
            self.add_child_to_tree_and_data(parent_name, child_name, filtered_pc)

            self.add_log_message(f"Added filtered point cloud '{child_name}' under '{parent_name}'.")
            self.add_action_to_log(action={f"{self.data[parent_name]}": {"Distance filter": {"min_distance": min_distance, "comparison_type": comparison_type}}})

def filter_points_by_distance_logic(pc1, pc2, min_distance, comparison_type):
    """Performs the distance filtering logic between two point clouds and retains RGB values."""

    # Extract points and colors from the point clouds
    points1 = np.asarray(pc1.points)
    colors1 = np.asarray(pc1.colors) if pc1.has_colors() else None

    points2 = np.asarray(pc2.points)
    colors2 = np.asarray(pc2.colors) if pc2.has_colors() else None

    # Compute distances from each point in pc1 to the nearest point in pc2
    distances = np.asarray(o3d.geometry.PointCloud.compute_point_cloud_distance(pc1, pc2))

    # Apply the distance filter based on comparison_type
    if comparison_type == "Greater Than":
        filter_mask = distances > min_distance
    elif comparison_type == "Greater Than or Equal To":
        filter_mask = distances >= min_distance
    elif comparison_type == "Less Than":
        filter_mask = distances < min_distance
    elif comparison_type == "Less Than or Equal To":
        filter_mask = distances <= min_distance
    elif comparison_type == "Equal To":
        filter_mask = np.isclose(distances, min_distance)  # Using np.isclose for floating point equality
    elif comparison_type == "Not Equal To":
        filter_mask = ~np.isclose(distances, min_distance)
    else:
        raise ValueError(f"Unknown comparison type: {comparison_type}")

    # Apply the filter mask to pc1's points and colors
    filtered_points1 = points1[filter_mask]
    filtered_colors1 = colors1[filter_mask] if colors1 is not None else None

    # Repeat for the second point cloud, comparing distances from points in pc2 to pc1
    distances_reverse = np.asarray(o3d.geometry.PointCloud.compute_point_cloud_distance(pc2, pc1))

    if comparison_type == "Greater Than":
        filter_mask2 = distances_reverse > min_distance
    elif comparison_type == "Greater Than or Equal To":
        filter_mask2 = distances_reverse >= min_distance
    elif comparison_type == "Less Than":
        filter_mask2 = distances_reverse < min_distance
    elif comparison_type == "Less Than or Equal To":
        filter_mask2 = distances_reverse <= min_distance
    elif comparison_type == "Equal To":
        filter_mask2 = np.isclose(distances_reverse, min_distance)
    elif comparison_type == "Not Equal To":
        filter_mask2 = ~np.isclose(distances_reverse, min_distance)

    filtered_points2 = points2[filter_mask2]
    filtered_colors2 = colors2[filter_mask2] if colors2 is not None else None

    if not filtered_points1.any() or not filtered_points2.any():
        return None, None  # No points passed the filter

    # Create new point clouds from the filtered points and colors
    filtered_pc1 = o3d.geometry.PointCloud()
    filtered_pc1.points = o3d.utility.Vector3dVector(filtered_points1)
    if filtered_colors1 is not None:
        filtered_pc1.colors = o3d.utility.Vector3dVector(filtered_colors1)

    filtered_pc2 = o3d.geometry.PointCloud()
    filtered_pc2.points = o3d.utility.Vector3dVector(filtered_points2)
    if filtered_colors2 is not None:
        filtered_pc2.colors = o3d.utility.Vector3dVector(filtered_colors2)

    return filtered_pc1, filtered_pc2

def sampling(self, selected_items):
    # selected_items = self.selected_items()

    print("Opening sample dialog...")  # Debugging

    # Define sampling methods as nested functions

    def sample_pointcloud_random(pointcloud, percentage):
        """Randomly sample the given point cloud based on percentage, retaining colors."""
        if not pointcloud or not pointcloud.has_points():
            print("No point cloud provided for random sampling.")
            return None

        points = np.asarray(pointcloud.points)  # Convert points to NumPy array
        colors = np.asarray(pointcloud.colors)  # Convert colors to NumPy array (if available)
        num_points = len(points)
        sample_size = int(num_points * (percentage / 100))

        if sample_size <= 0:
            print("Sample size is too small. Adjust the percentage.")
            return None

        # Randomly sample indices
        indices = random.sample(range(num_points), sample_size)
        sampled_points = points[indices]  # Sample points using the indices
        sampled_colors = colors[indices] if colors.size else None  # Sample colors (if present)

        # Create a new point cloud with sampled points and colors
        sampled_pc = o3d.geometry.PointCloud()
        sampled_pc.points = o3d.utility.Vector3dVector(sampled_points)
        if sampled_colors is not None:
            sampled_pc.colors = o3d.utility.Vector3dVector(sampled_colors)

        return sampled_pc

    def sample_pointcloud_regular(pointcloud, percentage):
        """Regularly sample the given point cloud based on percentage, retaining colors."""
        if not pointcloud or not pointcloud.has_points():
            print("No point cloud provided for regular sampling.")
            return None

        points = np.asarray(pointcloud.points)  # Convert points to a NumPy array
        colors = np.asarray(pointcloud.colors)  # Convert colors to a NumPy array (if available)
        num_points = len(points)
        sample_size = int(num_points * (percentage / 100))

        if sample_size <= 0:
            print("Sample size is too small. Adjust the percentage.")
            return None

        # Regular sampling: take every nth point
        step = max(1, num_points // sample_size)  # Ensure step is at least 1
        indices = list(range(0, num_points, step))[:sample_size]
        sampled_points = points[indices]  # Sample points using indices
        sampled_colors = colors[indices] if colors.size else None  # Sample colors (if present)

        # Create a new point cloud with sampled points and colors
        sampled_pc = o3d.geometry.PointCloud()
        sampled_pc.points = o3d.utility.Vector3dVector(sampled_points)
        if sampled_colors is not None:
            sampled_pc.colors = o3d.utility.Vector3dVector(sampled_colors)

        return sampled_pc

    def sample_pointcloud_voxel(pointcloud, voxel_size):
        """Voxel downsample the given point cloud based on voxel size."""
        if not pointcloud:
            self.add_log_message("No point cloud provided for voxel sampling.")
            return None

        if voxel_size <= 0:
            self.add_log_message("Invalid voxel size. Must be greater than zero.")
            return None

        sampled_pc = pointcloud.voxel_down_sample(voxel_size)
        return sampled_pc

    # Open the sample dialog
    dialog = SampleDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        sample_type = dialog.get_sample_type()

        # Check for sampling type and handle parameters accordingly
        if sample_type in ["Random Sample", "Regular Sample"]:
            value = dialog.get_percentage()
        elif sample_type == "Voxel Downsample":
            value = dialog.get_voxel_size()
        else:
            self.add_log_message(f"Invalid sample type: {sample_type}.")
            return

        for item in selected_items:
            # Determine the file name and check hierarchy
            if item.parent():  # If it's a child item
                parent_name = item.parent().text(0)  # Parent holds the file name
                child_name = item.text(0)  # Child text represents the cloud type
            else:  # If it's a top-level (parent) item
                self.add_log_message("Top-level items cannot be sampled directly.")
                continue

            # Ensure the point cloud is selected
            if child_name != "Pointcloud":
                self.add_log_message(f"Skipping: {child_name}. Only 'Pointcloud' supports sampling.")
                continue

            # Retrieve the point cloud data
            data = self.data.get(parent_name)
            if not data:
                self.add_log_message(f"No valid point cloud found for {parent_name}. Skipping.")
                continue

            point_dataset = data[child_name]

            # Perform sampling
            sampled_pc = None
            if sample_type == "Random Sample":
                sampled_pc = sample_pointcloud_random(point_dataset, value)
            elif sample_type == "Regular Sample":
                sampled_pc = sample_pointcloud_regular(point_dataset, value)
            elif sample_type == "Voxel Downsample":
                sampled_pc = sample_pointcloud_voxel(point_dataset, value)
            else:
                self.add_log_message(f"Invalid sample type: {sample_type}. Skipping {parent_name}.")
                continue

            if not sampled_pc:
                self.add_log_message(f"Sampling failed for {parent_name}.")
                continue

            # Name and store the sampled point cloud
            sampled_file_name = "Sampled Pointcloud"

            self.data[parent_name][sampled_file_name] = sampled_pc

            # Add the sampled point cloud to the tree and viewer
            # parent = item.parent()
            self.add_child_to_tree_and_data(parent_name, "Sampled Pointcloud", sampled_pc)

            # Add sampled point cloud to the viewer
            self.o3d_viewer.add_item(sampled_pc, parent_name, "Sampled Pointcloud")
            self.add_log_message(f"Sampled pointcloud added: {sampled_file_name}")

            # Log the number of points in the sampled point cloud
            num_sampled_points = len(np.asarray(sampled_pc.points))
            self.add_log_message(f"Sampled pointcloud added: {sampled_file_name}, {num_sampled_points} points.")

            self.add_action_to_log(action={f"{self.data[parent_name]}": {
                "Distance filter": {"sample_type": sample_type, "Sample value": value, "num_sampled_points": num_sampled_points}}})

        # Update the viewer
        self.o3d_viewer.update_viewer()
        self.add_log_message("Viewer updated with sampled pointclouds.")

def dbscan_analysis(self, selected_items):

    # Retrieve selected items from the tree
    # selected_items = self.selected_items()

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

def merge_items(self, selected_items):
    """
    Merge selected Open3D objects of the same type and add the result to the tree.
    The merged data is added as a new parent with a child named according to the data type.
    """

    # Retrieve Open3D objects and their parents from the tree
    open3d_objects = []
    parent_names = []
    for item in selected_items:
        parent = item.parent()
        if parent is None:
            self.add_log_message(f"Item '{item.text(0)}' has no parent; skipping.")
            return None
        parent_name = parent.text(0)
        if parent_name not in parent_names:
            parent_names.append(parent_name)  # Avoid duplicates
        item_name = item.text(0)
        open3d_object = self.data[parent_name][item_name]
        open3d_objects.append(open3d_object)

    if len(parent_names) > 2:
        self.add_log_message("Merging is limited to two different parents.")
        return None

    # Ensure all items are of the same type
    first_item_type = type(open3d_objects[0])
    if not all(isinstance(obj, first_item_type) for obj in open3d_objects):
        self.add_log_message("Cannot merge items of different types.")
        return None

    # Merge Open3D objects
    if first_item_type == o3d.geometry.PointCloud:
        self.add_log_message("Merging PointClouds...")
        merged_object = o3d.geometry.PointCloud()
        for obj in open3d_objects:
            merged_object += obj  # Assuming PointCloud supports `+=` for merging
        child_name = "Pointcloud"
    elif first_item_type == o3d.geometry.LineSet:
        self.add_log_message("Merging LineSets...")
        merged_object = o3d.geometry.LineSet()
        for obj in open3d_objects:
            merged_object += obj  # Assuming LineSet supports `+=` for merging
        child_name = "LineSet"
    elif first_item_type == o3d.geometry.TriangleMesh:
        self.add_log_message("Merging TriangleMeshes...")
        merged_object = o3d.geometry.TriangleMesh()
        for obj in open3d_objects:
            merged_object += obj  # Assuming TriangleMesh supports `+=` for merging
        child_name = "TriangleMesh"
    else:
        self.add_log_message(f"Merging for type '{first_item_type.__name__}' is not supported.")
        return None

    # Create a new parent name based on the parent filenames
    new_parent_name = f"{parent_names[0]}_{parent_names[1]}"

    # Add the merged object to the tree and data structure using the helper method
    self.add_child_to_tree_and_data(new_parent_name, child_name, merged_object)

    # Log success
    self.add_log_message(f"Merged items added to the tree under '{new_parent_name}'.")


####
# tools moving over to tools from main
def filter_points_by_hull_footprint(self, selected_items):
    """Filters points from a selected Open3D point cloud that fall within the footprint of a selected line set (3D convex hull)."""
    # selected_items = self.selected_items()

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




######
# Tools in production
import numpy as np
import open3d as o3d
from scipy.spatial import cKDTree
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QDoubleSpinBox, QPushButton, QHBoxLayout

class PointCloudSelectionDialog(QDialog):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.setWindowTitle("Select Point Clouds for Merging")

        layout = QVBoxLayout()

        # Parent and Cloud selection for Cloud 1
        layout.addWidget(QLabel("Select Parent & Base Point Cloud (kept unchanged):"))
        self.parent1_combo = QComboBox()
        self.parent1_combo.addItems(data.keys())  # Parent names
        layout.addWidget(self.parent1_combo)

        self.cloud1_combo = QComboBox()
        layout.addWidget(self.cloud1_combo)

        # Parent and Cloud selection for Cloud 2
        layout.addWidget(QLabel("Select Parent & Secondary Point Cloud (filtered & merged):"))
        self.parent2_combo = QComboBox()
        self.parent2_combo.addItems(data.keys())  # Parent names
        layout.addWidget(self.parent2_combo)

        self.cloud2_combo = QComboBox()
        layout.addWidget(self.cloud2_combo)

        # Update cloud dropdowns based on selected parent
        self.parent1_combo.currentTextChanged.connect(self.update_cloud1_list)
        self.parent2_combo.currentTextChanged.connect(self.update_cloud2_list)

        # Set default cloud lists
        self.update_cloud1_list()
        self.update_cloud2_list()

        # Tolerance input
        layout.addWidget(QLabel("XY Tolerance for Merging (units):"))
        self.tolerance_spin = QDoubleSpinBox()
        self.tolerance_spin.setRange(0.001, 100.0)
        self.tolerance_spin.setDecimals(3)
        self.tolerance_spin.setValue(0.5)  # Default
        layout.addWidget(self.tolerance_spin)

        # OK & Cancel buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def update_cloud1_list(self):
        parent_name = self.parent1_combo.currentText()
        self.cloud1_combo.clear()
        if parent_name:
            self.cloud1_combo.addItems(self.parent().data.get(parent_name, {}).keys())

    def update_cloud2_list(self):
        parent_name = self.parent2_combo.currentText()
        self.cloud2_combo.clear()
        if parent_name:
            self.cloud2_combo.addItems(self.parent().data.get(parent_name, {}).keys())

    def get_selected_values(self):
        return (
            self.parent1_combo.currentText(),
            self.cloud1_combo.currentText(),
            self.parent2_combo.currentText(),
            self.cloud2_combo.currentText(),
            self.tolerance_spin.value()
        )

def substitute_points(self):
    print("Opening merge points dialog...")

    if not self.data:
        self.add_log_message("Error: No point cloud data available.")
        return

    # Open selection dialog for choosing parents and point clouds
    dialog = PointCloudSelectionDialog(self, self.data)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        self.add_log_message("Merge operation canceled.")
        return

    # Get the selected parent and point clouds from the dialog
    parent1, cloud1_name, parent2, cloud2_name, tolerance = dialog.get_selected_values()

    # Retrieve the selected point clouds
    cloud1 = self.data.get(parent1, {}).get(cloud1_name)
    cloud2 = self.data.get(parent2, {}).get(cloud2_name)

    if cloud1 is None or cloud2 is None:
        self.add_log_message(f"Error: Could not retrieve '{cloud1_name}' from '{parent1}' or '{cloud2_name}' from '{parent2}'.")
        return

    # Convert point cloud points to NumPy arrays
    cloud1_points = np.asarray(cloud1.points, dtype=np.float32)
    cloud2_points = np.asarray(cloud2.points, dtype=np.float32)

    # Get the RGB color values from the point clouds
    cloud1_colors = np.asarray(cloud1.colors, dtype=np.float32) if len(np.asarray(cloud1.colors)) > 0 else np.zeros_like(cloud1_points)
    cloud2_colors = np.asarray(cloud2.colors, dtype=np.float32) if len(np.asarray(cloud2.colors)) > 0 else np.zeros_like(cloud2_points)

    if len(cloud1_points) == 0 or len(cloud2_points) == 0:
        self.add_log_message("Error: One or both point clouds are empty.")
        return

    if not np.isfinite(cloud1_points).all() or not np.isfinite(cloud2_points).all():
        self.add_log_message("Error: One or both clouds contain invalid points.")
        return

    # Extract XY coordinates
    cloud1_xy = cloud1_points[:, :2]
    cloud2_xy = cloud2_points[:, :2]

    # Build a KDTree using cloud1 in XY space
    kdtree_xy = cKDTree(cloud1_xy)

    # Find nearest neighbor distances for cloud2 points
    distances, _ = kdtree_xy.query(cloud2_xy, k=1)

    # Identify points in cloud2 that are farther than the tolerance
    non_overlapping_mask = distances > tolerance
    non_overlapping_points = cloud2_points[non_overlapping_mask]
    non_overlapping_colors = cloud2_colors[non_overlapping_mask]

    # Merge the non-overlapping points and their colors with cloud1
    merged_points = np.vstack([cloud1_points, non_overlapping_points])
    merged_colors = np.vstack([cloud1_colors, non_overlapping_colors])

    # Create a new merged point cloud
    merged_cloud = o3d.geometry.PointCloud()
    merged_cloud.points = o3d.utility.Vector3dVector(merged_points)
    merged_cloud.colors = o3d.utility.Vector3dVector(merged_colors)

    # Ensure a unique name for the merged point cloud
    base_name = "pointcloud_merged"
    merged_cloud_name = base_name
    counter = 1
    # Ensure the new name is unique under a new parent (default "Merged Point Clouds")
    parent_name = "Merged Point Clouds"
    while merged_cloud_name in self.data.get(parent_name, {}):
        merged_cloud_name = f"{base_name}_{counter}"
        counter += 1

    # Add the new merged point cloud to the tree and data under the new parent
    self.add_child_to_tree_and_data(parent_name, merged_cloud_name, merged_cloud)

    # Log completion of the merge operation
    self.add_log_message(f"Merge completed: '{merged_cloud_name}' created under '{parent_name}' with {len(merged_points)} points.")


def boundingbox3d(self, selected_items): # todo not working
    print("Not opening ConvexHull dialog...")  # Debugging
    for item in selected_items:
        # Determine the file name and check hierarchy
        if item.parent():  # If it's a child item
            parent_name = item.parent().text(0)  # Parent holds the file name
            child_name = item.text(0)  # Child text represents the cloud type
        else:  # If it's a top-level (parent) item
            self.add_log_message("Top-level items cannot be sampled directly.")
            continue

        # Retrieve the point cloud data
        data = self.data.get(parent_name)
        if not data:
            self.add_log_message(f"No valid point cloud found for {parent_name}. Skipping.")
            continue
        point_dataset = data[child_name]

        # Perform convex hull
        def hull3d(point_cloud):
            # Compute the convex hull of the point cloud
            hull, _ = point_cloud.compute_convex_hull()
            return hull

        hull_mesh = hull3d(point_dataset)

        if not hull_mesh:
            self.add_log_message(f"Sampling failed for {parent_name}.")
            continue

        # Extract points from the convex hull's TriangleMesh
        hull_points = np.asarray(hull_mesh.vertices)  # Get vertices from the hull mesh
        if hull_points.shape[0] == 0:
            self.add_log_message("No vertices found in the convex hull.")
            continue

        # Create the PointCloud for the convex hull vertices
        hull_points_cloud = o3d.geometry.PointCloud()
        hull_points_cloud.points = o3d.utility.Vector3dVector(hull_points)

        # Color the points manually
        rgb_color = [0, 0, 1]  # Blue color
        new_colors = np.tile(rgb_color, (len(hull_points), 1))  # Apply the new color to all points
        hull_points_cloud.colors = o3d.utility.Vector3dVector(new_colors)

        # Debugging step: Ensure the points are valid
        print(f"Hull points cloud has {len(hull_points)} points.")

        # Compute Axis-Aligned Bounding Box (AABB)
        aabb = hull_points_cloud.get_axis_aligned_bounding_box()
        aabb_corners = np.asarray(aabb.get_box_points())

        # Compute Oriented Bounding Box (OBB)
        obb = hull_points_cloud.get_oriented_bounding_box()
        obb_corners = np.asarray(obb.get_box_points())

        # Define lines to visualize the bounding boxes
        aabb_lines = [
            [0, 1], [1, 2], [2, 3], [3, 0],  # bottom face
            [4, 5], [5, 6], [6, 7], [7, 4],  # top face
            [0, 4], [1, 5], [2, 6], [3, 7]   # vertical lines
        ]

        obb_lines = [
            [0, 1], [1, 2], [2, 3], [3, 0],  # bottom face
            [4, 5], [5, 6], [6, 7], [7, 4],  # top face
            [0, 4], [1, 5], [2, 6], [3, 7]   # vertical lines
        ]

        # Create LineSets to visualize the bounding boxes
        aabb_lineset = o3d.geometry.LineSet()
        aabb_lineset.points = o3d.utility.Vector3dVector(aabb_corners)
        aabb_lineset.lines = o3d.utility.Vector2iVector(aabb_lines)
        aabb_lineset.paint_uniform_color([1, 0, 0])  # Set AABB color to red

        obb_lineset = o3d.geometry.LineSet()
        obb_lineset.points = o3d.utility.Vector3dVector(obb_corners)
        obb_lineset.lines = o3d.utility.Vector2iVector(obb_lines)
        obb_lineset.paint_uniform_color([0, 1, 0])  # Set OBB color to green

        # Add the convex hull, AABB, and OBB to the viewer
        self.data[parent_name]["Hull3D"] = hull_mesh
        self.add_child_to_tree_and_data(parent_name, "Hull3D", hull_mesh)

        self.o3d_viewer.add_item(hull_points_cloud, parent_name, "Hull Points")
        self.o3d_viewer.add_item(aabb_lineset, parent_name, "AABB")
        self.o3d_viewer.add_item(obb_lineset, parent_name, "OBB")

        # Log the action
        self.add_log_message(f"Sampled pointcloud added: Hull3D, AABB, OBB")

    # Update the viewer
    self.o3d_viewer.update_viewer()
    self.add_log_message("Viewer updated with ConvexHull and Bounding Boxes.")

class TopBaseSelectionDialog(QDialog):
    def __init__(self, selected_items, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Top and Base Point Clouds with Tolerance")

        # Create widgets for selecting top and base point clouds
        self.top_label = QLabel("Select Top Point Cloud:")
        self.top_combo = QComboBox()
        self.base_label = QLabel("Select Base Point Cloud:")
        self.base_combo = QComboBox()

        # Create widget for tolerance input
        self.tolerance_label = QLabel("Enter Tolerance Value:")
        self.tolerance_input = QLineEdit(self)
        self.tolerance_input.setPlaceholderText("e.g., 0.01")

        # Populate combo boxes with point clouds from selected items
        for item in selected_items:
            # Assuming each 'item' has a 'parent' method and 'text' method to get names
            parent_name = item.parent().text(0) if item.parent() else "No Parent"  # Get parent name
            pointcloud_name = item.text(0)

            display_name = f"{parent_name} - {pointcloud_name}"
            self.top_combo.addItem(display_name)
            self.base_combo.addItem(display_name)

        # Create OK and Cancel buttons
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.top_label)
        layout.addWidget(self.top_combo)
        layout.addWidget(self.base_label)
        layout.addWidget(self.base_combo)
        layout.addWidget(self.tolerance_label)
        layout.addWidget(self.tolerance_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Connect buttons
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_selected_clouds_and_tolerance(self):
        """Returns the selected top and base point clouds and the tolerance entered by the user."""
        # Get the full display names (Parent Name - Point Cloud Name)
        top_display_name = self.top_combo.currentText()
        base_display_name = self.base_combo.currentText()

        # Extract the point cloud names from the full display names
        top_cloud_name = top_display_name.split(" - ")[1]
        base_cloud_name = base_display_name.split(" - ")[1]

        # Get the tolerance entered by the user
        try:
            tolerance = float(self.tolerance_input.text())
            return top_cloud_name, base_cloud_name, tolerance
        except ValueError:
            # Handle invalid input (non-numeric)
            return top_cloud_name, base_cloud_name, None

def fill_holes_delaunay3d(self, selected_items):
    """
    Fills holes in a point cloud using Delaunay triangulation.
    New points are interpolated and merged into the original cloud.
    """
    print("Running Delaunay-based hole filling...")  # Debugging

    for item in selected_items:
        # Determine the file name and check hierarchy
        if item.parent():
            parent_name = item.parent().text(0)
            child_name = item.text(0)
        else:
            self.add_log_message("Top-level items cannot be processed directly.")
            continue

        # Retrieve the point cloud data
        data = self.data.get(parent_name)
        if not data:
            self.add_log_message(f"No valid point cloud found for {parent_name}. Skipping.")
            continue
        point_dataset = data[child_name]

        # Compute 3D Delaunay triangulation and fill holes
        def fill_holes(point_cloud):
            points = np.asarray(point_cloud.points)
            if len(points) < 4:  # Delaunay requires at least 4 non-coplanar points
                return None

            # Perform 3D Delaunay triangulation
            tri = scipy.spatial.Delaunay(points)

            # Compute centroids of triangles to create new points
            centroids = np.mean(points[tri.simplices], axis=1)

            # Estimate Z using k-NN from existing points
            tree = scipy.spatial.cKDTree(points)
            _, idx = tree.query(centroids, k=3)
            estimated_z = np.mean(points[idx][:, :, 2], axis=1)

            # Merge new points into the original point cloud
            new_points = np.hstack((centroids[:, :2], estimated_z.reshape(-1, 1)))
            all_points = np.vstack((points, new_points))

            # Create new Open3D point cloud
            filled_pcd = o3d.geometry.PointCloud()
            filled_pcd.points = o3d.utility.Vector3dVector(all_points)

            # Optional: Downsample for consistency
            filled_pcd = filled_pcd.voxel_down_sample(voxel_size=0.01)

            return filled_pcd

        filled_pointcloud = fill_holes(point_dataset)

        if not filled_pointcloud:
            self.add_log_message(f"Hole filling failed for {parent_name}.")
            continue

        # Store the modified point cloud
        self.data[parent_name]["FilledHoles"] = filled_pointcloud

        # Add to tree and viewer
        self.add_child_to_tree_and_data(parent_name, "FilledHoles", filled_pointcloud)
        self.o3d_viewer.add_item(filled_pointcloud, parent_name, "FilledHoles")
        self.add_log_message(f"Hole-filled point cloud added: FilledHoles")

    # Update the viewer
    self.o3d_viewer.update_viewer()
    self.add_log_message("Viewer updated with hole-filled point cloud.")

def delaunay3d_mesh(self, selected_items):
    print("Running 3D triangulation with trimesh...")

    for item in selected_items:
        if item.parent():
            parent_name = item.parent().text(0)
            child_name = item.text(0)
        else:
            self.add_log_message("Top-level items cannot be processed directly.")
            continue

        # Retrieve the point cloud
        data = self.data.get(parent_name)
        if not data:
            self.add_log_message(f"No valid point cloud found for {parent_name}. Skipping.")
            continue
        point_dataset = data[child_name]

        # Convert Open3D point cloud to numpy array
        points = np.asarray(point_dataset.points)
        if len(points) < 4:
            self.add_log_message(f"Error: {parent_name} does not have enough points for triangulation.")
            continue

        # Perform 3D triangulation with trimesh
        trimesh_mesh = trimesh.Trimesh(vertices=points)
        trimesh_mesh = trimesh_mesh.convex_hull  # Ensure a closed triangulated mesh

        # Convert to Open3D TriangleMesh
        o3d_mesh = o3d.geometry.TriangleMesh()
        o3d_mesh.vertices = o3d.utility.Vector3dVector(np.asarray(trimesh_mesh.vertices, dtype=np.float64))
        o3d_mesh.triangles = o3d.utility.Vector3iVector(np.asarray(trimesh_mesh.faces, dtype=np.int32))

        if len(o3d_mesh.triangles) == 0:
            self.add_log_message(f"Error: No valid triangles generated for {parent_name}.")
            continue

        # Store and display the triangulated mesh
        self.data[parent_name]["Delaunay3D"] = o3d_mesh
        self.add_child_to_tree_and_data(parent_name, "Delaunay3D", o3d_mesh)

        # ✅ Prevent crashing by adding a check before rendering
        try:
            self.o3d_viewer.add_item(o3d_mesh, parent_name, "Delaunay3D")
        except Exception as e:
            self.add_log_message(f"Warning: Open3D viewer failed to render mesh: {e}")

        self.add_log_message(f"Triangulated mesh added: Delaunay3D")

    # ✅ Update viewer safely
    try:
        self.o3d_viewer.update_viewer()
    except Exception as e:
        self.add_log_message(f"Warning: Viewer update failed: {e}")

    self.add_log_message("Viewer updated with trimesh triangulation.")





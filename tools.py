import open3d as o3d
import numpy as np
import random

from dialogs_pyqt5 import (DistanceFilterDialog, SampleDialog, PoissonSurfaceDialog,
                     ScaleFactorDialog)

from dialogs_pyqt5 import (
    # DistanceFilterDialog,
    SampleDialog,
    # PoissonSurfaceDialog,
    ScaleFactorDialog)
import scipy.spatial

import open3d as o3d
import numpy as np


from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel, QDialogButtonBox, QLineEdit, QHBoxLayout

def fill_holes(self, selected_items):
    pass


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


import open3d as o3d
# import pyvista as pv
import numpy as np

import trimesh
import open3d as o3d
import numpy as np

import trimesh
import open3d as o3d
import numpy as np

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


import open3d as o3d
import numpy as np

import open3d as o3d
import numpy as np

#
# def triangulate2_5d_ball_pivoting(self, selected_items):
#     print("Running 2.5D triangulation using Ball-Pivoting...")
#
#     for item in selected_items:
#         if item.parent():
#             parent_name = item.parent().text(0)
#             child_name = item.text(0)
#         else:
#             self.add_log_message("Top-level items cannot be processed directly.")
#             continue
#
#         # Retrieve the point cloud
#         data = self.data.get(parent_name)
#         if not data:
#             self.add_log_message(f"No valid point cloud found for {parent_name}. Skipping.")
#             continue
#         point_dataset = data[child_name]
#
#         # Convert Open3D point cloud to numpy array
#         points = np.asarray(point_dataset.points)
#         if len(points) < 3:
#             self.add_log_message(f"Error: {parent_name} does not have enough points for triangulation.")
#             continue
#
#         # 1️⃣ Ensure the point cloud has normals
#         if not point_dataset.has_normals():
#             self.add_log_message("Estimating normals...")
#             point_dataset.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
#
#             # 2️⃣ Orient normals consistently
#             point_dataset.orient_normals_consistent_tangent_plane(k=30)
#
#             # Optionally, perform normal smoothing to reduce outliers
#             point_dataset = smooth_normals(point_dataset)
#
#         # 3️⃣ Check if normals are consistent after orientation
#         if not np.allclose(np.asarray(point_dataset.normals).mean(axis=0), np.zeros(3)):
#             self.add_log_message(f"Warning: Normals for {parent_name} are still inconsistent after orientation.")
#
#         # 4️⃣ Ball-Pivoting surface reconstruction
#         radii = [0.05, 0.1, 0.2]  # Adjust based on point spacing
#         bpa_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
#             point_dataset, o3d.utility.DoubleVector(radii)
#         )
#
#         if len(bpa_mesh.triangles) == 0:
#             self.add_log_message(f"Error: No valid BPA mesh generated for {parent_name}.")
#             continue
#
#         # Store and display the triangulated surface
#         self.data[parent_name]["BPA_2.5D"] = bpa_mesh
#         self.add_child_to_tree_and_data(parent_name, "BPA_2.5D", bpa_mesh)
#
#         try:
#             self.o3d_viewer.add_item(bpa_mesh, parent_name, "BPA_2.5D")
#         except Exception as e:
#             self.add_log_message(f"Warning: Open3D viewer failed to render mesh: {e}")
#
#         self.add_log_message(f"2.5D BPA triangulated surface added: BPA_2.5D")
#
#     # Update viewer safely
#     try:
#         self.o3d_viewer.update_viewer()
#     except Exception as e:
#         self.add_log_message(f"Warning: Viewer update failed: {e}")
#
#     self.add_log_message("Viewer updated with Ball-Pivoting 2.5D triangulation.")
#
#
#








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
            percentage = dialog.get_percentage()
        elif sample_type == "Voxel Downsample":
            voxel_size = dialog.get_voxel_size()
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
                sampled_pc = sample_pointcloud_random(point_dataset, percentage)
            elif sample_type == "Regular Sample":
                sampled_pc = sample_pointcloud_regular(point_dataset, percentage)
            elif sample_type == "Voxel Downsample":
                sampled_pc = sample_pointcloud_voxel(point_dataset, voxel_size)
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

        # Update the viewer
        self.o3d_viewer.update_viewer()
        self.add_log_message("Viewer updated with sampled pointclouds.")











#


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


import numpy as np

import numpy as np
import open3d as o3d

import numpy as np
import open3d as o3d

def substitute_points(self, selected_items):
    print("Opening substitute points dialog...")

    # Open the dialog
    dialog = TopBaseSelectionDialog(selected_items)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        top_cloud_name, base_cloud_name, tolerance = dialog.get_selected_clouds_and_tolerance()

        if tolerance is None:
            self.add_log_message("Invalid tolerance value. Operation canceled.")
            return

        # Determine parent name for accessing the data
        parent_name = selected_items[0].parent().text(0) if selected_items[0].parent() else "Unknown Parent"

        # Retrieve the selected point clouds
        top_cloud = self.data.get(parent_name, {}).get(top_cloud_name)
        base_cloud = self.data.get(parent_name, {}).get(base_cloud_name)

        if top_cloud is None or base_cloud is None:
            self.add_log_message(f"Error: Could not retrieve point clouds '{top_cloud_name}' or '{base_cloud_name}'.")
            return

        # Convert point cloud points to NumPy arrays
        top_points = np.asarray(top_cloud.points, dtype=np.float32)
        base_points = np.asarray(base_cloud.points, dtype=np.float32)

        if len(top_points) == 0 or len(base_points) == 0:
            self.add_log_message("Error: One or both point clouds are empty.")
            return

        if not np.isfinite(top_points).all() or not np.isfinite(base_points).all():
            self.add_log_message("Error: One or both clouds contain invalid points.")
            return

        # Build KDTree for the top point cloud
        kdtree_top = o3d.geometry.KDTreeFlann(top_cloud)

        # Prepare lists for substituted and remaining points
        substituted_points = []
        remaining_base_points = []

        for i, base_point in enumerate(base_points):
            print(f"Processing point {i}: {base_point}")  # Debugging
            base_point = np.asarray(base_point, dtype=np.float64)  # Ensure correct format
            if base_point.shape != (3,):
                print(f"Skipping invalid base point {i}: {base_point}")
                continue

            if not np.isfinite(base_point).all():
                print(f"Skipping non-finite base point {i}: {base_point}")
                continue

            try:
                # Find the nearest neighbor in the top cloud
                [success, idx, _] = kdtree_top.search_knn_vector_3d(base_point, 1)
                if success <= 0:
                    print(f"No neighbor found for base point {i}. Adding to remaining points.")
                    remaining_base_points.append(base_point)
                    continue

                # Check the Z-coordinate difference
                nearest_top_point = top_points[idx[0]]
                print(f"Nearest top point for base point {i}: {nearest_top_point}")  # Debugging

                if base_point[2] > nearest_top_point[2] + tolerance:
                    print(f"Base point {i} is above the top point by tolerance. Substituting.")
                    substituted_points.append(base_point)
                else:
                    print(f"Base point {i} is not above the top point. Keeping in remaining.")
                    remaining_base_points.append(base_point)

            except Exception as e:
                print(f"Error during KDTree search for base point {i}: {e}")
                remaining_base_points.append(base_point)

        # Create new point clouds with the results
        updated_top_cloud = top_cloud.clone()
        updated_top_cloud.points = o3d.utility.Vector3dVector(np.vstack([top_points, substituted_points]))

        remaining_base_cloud = base_cloud.clone()
        remaining_base_cloud.points = o3d.utility.Vector3dVector(np.array(remaining_base_points))

        # Add the updated clouds to the data and tree
        self.add_child_to_tree_and_data(parent_name, f"{top_cloud_name}_updated", updated_top_cloud)
        self.add_child_to_tree_and_data(parent_name, f"{base_cloud_name}_remaining", remaining_base_cloud)

        # Log completion message
        self.add_log_message(f"Substitution completed: '{top_cloud_name}_updated' and '{base_cloud_name}_remaining' created.")















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



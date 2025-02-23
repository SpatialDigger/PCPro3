import open3d as o3d


def compute_normals_cloudcompare_style(pcd, method="knn", k=6, alpha=0.03):
    """
    Compute normals in a way similar to CloudCompare using triangulation-based local surface modeling.

    Parameters:
    - pcd (o3d.geometry.PointCloud): The input point cloud.
    - method (str): "knn" for k-NN based normal estimation (default),
                    "alpha_shape" for triangulation-based normals.
    - k (int): Number of nearest neighbors to use for k-NN normal estimation.
    - alpha (float): Alpha value for the alpha shape triangulation (if method="alpha_shape").

    Returns:
    - pcd or mesh: Point cloud with computed normals (if method="knn"),
                   or a mesh with computed vertex normals (if method="alpha_shape").
    """

    if method == "knn":
        # Estimate normals using k-NN (default k=6 like CloudCompare)
        pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamKNN(knn=k))

        # Orient normals consistently
        pcd.orient_normals_consistent_tangent_plane(k)

        return pcd

    elif method == "alpha_shape":
        # Generate a triangulated mesh using Alpha Shape
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, alpha)

        # Compute normals on the mesh vertices
        mesh.compute_vertex_normals()

        return mesh

    else:
        raise ValueError("Invalid method. Use 'knn' or 'alpha_shape'.")


# Example usage
if __name__ == "__main__":
    pcd = o3d.io.read_point_cloud("your_point_cloud.ply")

    # Compute normals using k-NN (CloudCompare default)
    pcd_with_normals = compute_normals_cloudcompare_style(pcd, method="knn", k=6)

    # Visualize point cloud with normals
    o3d.visualization.draw_geometries([pcd_with_normals], point_show_normal=True)

    # Alternatively, compute normals using triangulation (alpha shape)
    mesh_with_normals = compute_normals_cloudcompare_style(pcd, method="alpha_shape", alpha=0.03)

    # Visualize triangulated mesh
    o3d.visualization.draw_geometries([mesh_with_normals])

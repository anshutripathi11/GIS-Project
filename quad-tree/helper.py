import json
from quad_tree import Point
import random
from collections import namedtuple
from matplotlib import pyplot
import geopandas as gpd
import contextily as ctx
from shapely.geometry import Point as MapPoint, box
from shapely import affinity

Boundary = namedtuple("Boundary", ["center", "width", "height"])

def load_points_from_geojson(file_path):
    """
    This function is used to load the points from GeoJSON
    """
    points = []
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for feature in data["features"]:
            if feature["geometry"]["type"] == "Point":
                lon, lat = feature["geometry"]["coordinates"]
                points.append(Point(x = lon, y = lat, data = feature["properties"]))
    return points

def calculate_boundary(points, buffer_ratio=0.05):
    """
    Used to Calculate the bounding box based on the points
    """
    # Extract all x (longitude) and y (latitude) coordinates
    x_coords = [p.x for p in points]
    y_coords = [p.y for p in points]

    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)

    # Calculate center
    x_center = (min_x + max_x) / 2
    y_center = (min_y + max_y) / 2

    # Width and height with a small buffer
    width = (max_x - min_x) * (1 + buffer_ratio)
    height = (max_y - min_y) * (1 + buffer_ratio)

    return Boundary(center=(x_center, y_center), width=width, height=height)

def generate_random_points(x, x_range=(0, 100), y_range=(0, 100)):
    """
    Used to generate random points for testing
    """
    all_points = []
    for _ in range(x):
        x_coord = random.uniform(*x_range)
        y_coord = random.uniform(*y_range)
        all_points.append(Point(x_coord, y_coord))
    return all_points

def visualize(tree, xsize = 10, ysize = 10, title = "Quad Tree Visualization", save_plot = False, file_name = "plot.png"):
    """
    Can be used to Visulize the Quad Tree
    """
    def draw_all_nodes(node):
        # Draw the points in the current node
        for pnt in node.points:
            pyplot.plot(pnt.x, pnt.y, ".", color = "black")

        # Draw subdivision lines if node is divided
        if any([node.ul, node.ur, node.ll, node.lr]):
            draw_lines(node)

        # Recursively draw children
        if node.ul:
            draw_all_nodes(node.ul)
        if node.ur:
            draw_all_nodes(node.ur)
        if node.ll:
            draw_all_nodes(node.ll)
        if node.lr:
            draw_all_nodes(node.lr)

    def draw_lines(node):
        bb = node.bounding_box

        # Draw horizontal line at center.y from min_x to max_x
        pyplot.plot([bb.min_x, bb.max_x], [node.center.y, node.center.y], color="black", linewidth=0.5)

        # Draw vertical line at center.x from min_y to max_y
        pyplot.plot([node.center.x, node.center.x], [bb.min_y, bb.max_y], color="black", linewidth=0.5)

    # Set up plot canvas
    pyplot.figure(figsize=(xsize, ysize))

    # Draw axis bounds from tree dimensions
    half_width = tree.width / 2
    half_height = tree.height / 2
    min_x = tree.center.x - half_width
    max_x = tree.center.x + half_width
    min_y = tree.center.y - half_height
    max_y = tree.center.y + half_height
    pyplot.axis([min_x, max_x, min_y, max_y])

    # Draw all nodes starting from root
    draw_all_nodes(tree._root)

    pyplot.gca().set_aspect('equal', adjustable='box')
    pyplot.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Full use of plot area
    pyplot.margins(0, 0)
    pyplot.title(title)
    if not save_plot:
        pyplot.show()
    else:
        pyplot.savefig(file_name, bbox_inches='tight', pad_inches=0.1, dpi=500)

def plot_near_neighbors(points, output_path="near_parks_map.png", rotate_map=False):
    """
    Plots the nearest neighbors
    """
    # Convert parks to GeoDataFrame
    gdf = gpd.GeoDataFrame({
        "label": [p.structure_name if p.structure_name else "" for p in points],
        "geometry": [MapPoint(p.x, p.y) for p in points]
    }, crs="EPSG:4326")


    # Convert to Web Mercator (needed for basemaps)
    gdf = gdf.to_crs(epsg=3857)

    # Optional rotation of geometries
    if rotate_map:
        # Get center for rotation (use centroid of all geometry)
        all_geom = gdf.geometry
        rotation_center = all_geom.unary_union.centroid
        gdf["geometry"] = gdf["geometry"].apply(lambda geom: affinity.rotate(geom, -90, origin=rotation_center))
        
    # Plot everything
    fig, ax = pyplot.subplots(figsize=(15, 15))
    gdf.plot(ax=ax, alpha=0.9, color="blue", edgecolor="black", markersize=100, label="Parks")

    # Park Labels
    for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf["label"]):
        if label:
            ax.text(x, y, label, fontsize=15, ha='right', va='bottom')


    # Basemap and final styling
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
    ax.axis('off')
    pyplot.tight_layout()
    pyplot.savefig(output_path, bbox_inches='tight', dpi=1500)
    print(f"Map saved to {output_path}")

def plot_bounding_box_and_points(points, bb, output_path="bounding_box_map.png", rotate_map=False):
    """
    points: list of `Point` objects (QuadTree points) inside the bounding box
    bb: BoundingBox object (with .min_x, .min_y, .max_x, .max_y)
    """

    # GeoDataFrame of Points
    gdf = gpd.GeoDataFrame({
        "label": [p.structure_name if hasattr(p, "structure_name") and p.structure_name else "" for p in points],
        "geometry": [MapPoint(p.x, p.y) for p in points]
    }, crs="EPSG:4326")

    # GeoDataFrame for Bounding Box Polygon
    bb_geom = box(bb.min_x, bb.min_y, bb.max_x, bb.max_y)
    bb_gdf = gpd.GeoDataFrame(geometry=[bb_geom], crs="EPSG:4326")

    # Convert to Web Mercator for plotting
    gdf = gdf.to_crs(epsg=3857)
    bb_gdf = bb_gdf.to_crs(epsg=3857)

    # Rotation (optional)
    if rotate_map:
        rotation_center = gdf.geometry.unary_union.centroid
        gdf["geometry"] = gdf["geometry"].apply(lambda geom: affinity.rotate(geom, -90, origin=rotation_center))
        bb_gdf["geometry"] = bb_gdf["geometry"].apply(lambda geom: affinity.rotate(geom, -90, origin=rotation_center))

    # Plotting
    fig, ax = pyplot.subplots(figsize=(15, 15))

    # Plot points
    gdf.plot(ax=ax, alpha=0.9, color="green", edgecolor="black", markersize=100, label="Points in BB")

    # Plot bounding box
    bb_gdf.boundary.plot(ax=ax, edgecolor='blue', linewidth=2, label="Bounding Box")

    # Annotate labels
    for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf["label"]):
        if label:
            ax.text(x, y, label, fontsize=10, ha='right', va='bottom')

    # Basemap and styling
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
    ax.axis('off')
    pyplot.tight_layout()
    pyplot.savefig(output_path, bbox_inches='tight', dpi=1500)
    print(f"Bounding Box Map saved to {output_path}")

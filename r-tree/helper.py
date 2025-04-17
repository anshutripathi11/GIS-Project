import json
import Rtree
import random
from collections import namedtuple
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import geopandas as gpd
import contextily as ctx
from shapely.geometry import Point as MapPoint
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
                points.append(Rtree.Point((feature["properties"], lon, lat)))
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
    for id in range(x):
        x_coord = random.uniform(*x_range)
        y_coord = random.uniform(*y_range)
        all_points.append(Rtree.Point((str(id), x_coord, y_coord)))
    return all_points

def print_tree_structure(root_node):
    """
    Prints hierarchical tree structure with node capacities
    Fixed version that stops recursion at leaf nodes
    """
    tree_lines = []
    
    def _traverse(node, prefix="", is_last=False, is_root=True):
        # Get node info
        label = None
        capacity = ""
        if is_root:
            label = "Root"
            capacity = f"B={node.Bvalue}"
        elif isinstance(node, Rtree.Branch):
            label = "Branch"
            capacity = f"[{len(node.childList)}/{node.Bvalue}]"
        elif isinstance(node, Rtree.Leaf):
            label = "Leaf"
            capacity = f"[{len(node.childList)}/{node.Bvalue}]"
            # Don't recurse into leaf's children (they are points, not nodes)
            tree_lines.append(f"{prefix}{label} {capacity}")
            return
        
        # Build current line
        connector = "" if is_root else ("└── " if is_last else "├── ")
        tree_lines.append(f"{prefix}{connector}{label} {capacity}")
        
        # Only process children for Branch nodes
        if isinstance(node, Rtree.Branch):
            children = node.childList
            for i, child in enumerate(children):
                last_child = i == len(children)-1
                new_prefix = prefix + ("    " if is_last else "│   ")
                _traverse(child, new_prefix, last_child, False)

    _traverse(root_node)
    print("R-Tree Node Structure:")
    print("\n".join(tree_lines))

def visualize_rtree(root_node, ax=None, schema = {}):
    """
    schema = {
        "figure_size"
        "leaf_node_color": Color of Leaf Node
        "branch_node_color": Color of Branch Node
        "leaf_node_linestyle"
        "branch_node_linestyle"
        "leaf_node_linewidth"
        "branch_node_linewidth"
        "marker"
        "marker_size"
        "marker_color"
        "marker_fontsize"
        "horizontal_alignment"
        "vertical_alignment"
        "title"
        "save_plot"
        "plot_name"
        "file_dpi"
    }
    """
    if ax is None:
        fig, ax = plt.subplots(figsize = schema.get("figure_size", (10, 10)))

    node_colors = {
        'leaf': schema.get("leaf_node_color", "blue"),
        'branch': schema.get("branch_node_color", "red")
    }

    def draw_node(node):
        # Determine node type and style
        if isinstance(node, Rtree.Leaf):
            color = node_colors['leaf']
            linestyle = schema.get("leaf_node_linestyle", "-")
            linewidth = schema.get("leaf_node_linewidth", 1.2)
        elif isinstance(node, Rtree.Branch):
            color = node_colors['branch']
            linestyle = schema.get("branch_node_linestyle", "--")
            linewidth = linewidth = schema.get("branch_node_linewidth", 0.8)
        else:
            return

        # Draw MBR rectangle
        x0, x1, y0, y1 = node.range
        ax.add_patch(Rectangle(
            (x0, y0), x1-x0, y1-y0,
            fill=False, edgecolor=color,
            linestyle=linestyle, linewidth=linewidth,
            alpha=0.7 if isinstance(node, Rtree.Branch) else 1.0
        ))

        # Process children
        for child in node.childList:
            if isinstance(child, (Rtree.Leaf, Rtree.Branch)):
                draw_node(child)
            elif isinstance(child, Rtree.Point):
                ax.plot(
                    child.x, child.y, 
                    schema.get("marker", "o"), 
                    color = schema.get("marker_color", "green"), 
                    markersize = schema.get("marker_size", 4))
                ax.annotate(
                    child.ident, 
                    (child.x, child.y), 
                    fontsize = schema.get("marker_fontsize", 6), 
                    ha = schema.get("horizontal_alignment", "center"), 
                    va = schema.get("vertical_alignment", "bottom")
                )

    draw_node(root_node)
    
    # Configure plot aesthetics
    ax.set_title(schema.get("title", "r-tree"))
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.grid(False)
    plt.tight_layout()
    
    if not schema.get("save_plot", False):
        plt.show()
    else:
       plt.savefig(
           schema.get("plot_name", "plot.png"), 
           bbox_inches='tight', 
           pad_inches=0.1, 
           dpi=schema.get("file_dpi", 500)
        )



def plot_near_neighbors(points, current_location=None, output_path="near_parks_map.png", rotate_map=False):
    gdf = gpd.GeoDataFrame({
        "label": [p.ident for p in points],
        "geometry": [MapPoint(p.x, p.y) for p in points]
    }, crs="EPSG:4326")

    if current_location:
        clat, clon = current_location
        current_gdf = gpd.GeoDataFrame({
            "label": ["Current Location"],
            "geometry": [MapPoint(clon, clat)]
        }, crs="EPSG:4326")
    else:
        current_gdf = None

    gdf = gdf.to_crs(epsg=3857)
    if current_gdf is not None:
        current_gdf = current_gdf.to_crs(epsg=3857)

    if rotate_map:
        rotation_center = gdf.geometry.unary_union.centroid
        gdf["geometry"] = gdf["geometry"].apply(lambda geom: affinity.rotate(geom, -90, origin=rotation_center))
        if current_gdf is not None:
            current_gdf["geometry"] = current_gdf["geometry"].apply(lambda geom: affinity.rotate(geom, -90, origin=rotation_center))

    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(ax=ax, alpha=0.9, color="blue", edgecolor="black", markersize=80, label="Points")

    for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf["label"]):
        if label:
            ax.text(x, y, label, fontsize=8, ha='right', va='bottom')

    if current_gdf is not None:
        current_gdf.plot(ax=ax, color="red", markersize=120, label="Current Location")

    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', dpi=500)
    print(f"Map saved to {output_path}")

def plot_bounding_box_and_points(points, bounding_box, output_path="bb_result.png"):
    gdf = gpd.GeoDataFrame({
        "label": [p.structure_name if hasattr(p, 'structure_name') else str(p.ident) for p in points],
        "geometry": [MapPoint(p.x, p.y) for p in points]
    }, crs="EPSG:4326")

    bb_poly = gpd.GeoDataFrame({
        "geometry": [
            MapPoint(bounding_box[0], bounding_box[2]).buffer(0).envelope.union(
                MapPoint(bounding_box[1], bounding_box[3]).buffer(0).envelope).envelope
        ]
    }, crs="EPSG:4326")

    gdf = gdf.to_crs(epsg=3857)
    bb_poly = bb_poly.to_crs(epsg=3857)

    fig, ax = plt.subplots(figsize=(10, 10))
    bb_poly.boundary.plot(ax=ax, color='green', linewidth=2, label="Bounding Box")
    gdf.plot(ax=ax, alpha=0.9, color="blue", edgecolor="black", markersize=60, label="Points")

    for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf["label"]):
        ax.text(x, y, label, fontsize=7, ha='right', va='bottom')

    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', dpi=500)
    print(f"Saved bounding box visualization to {output_path}")

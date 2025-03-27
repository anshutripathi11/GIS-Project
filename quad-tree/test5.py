# Test on Actual Data
# fastfood in Texas

from helper import load_points_from_geojson, calculate_boundary, visualize, plot_near_neighbors, plot_bounding_box_and_points
from quad_tree import QuadTree, Point, BoundingBox
import os

def main():
    # Load points from GeoJSON
    geojson_file = os.path.join("..", "gis_data", "fastfood.geojson")
    all_points = load_points_from_geojson(geojson_file)

    boundary = calculate_boundary(all_points)

    print(boundary)

    qt1 = QuadTree(
        center = boundary.center, 
        width = boundary.width, 
        height = boundary.height,
        capacity = 4
    )

    inserted = 0
    for pt in all_points:
        if qt1.insert(pt):
            inserted += 1

    print("Number of fastfood inserted", inserted)

    # Visulize the QT
    visualize(qt1, xsize = 12, ysize = 12, save_plot = True, file_name =   os.path.join("plots", "fastfood_texas_qt.png"))


    # Perform Nearest Neighbor search 
    current_location = Point(-98.47314277856472, 29.526606308748846, {"name": "SAT Airport"})
    near_restaurants = qt1.nearest_neighbors(point = current_location, count = 15)
    print(near_restaurants)
    near_restaurants.append(current_location)
    plot_near_neighbors(points = near_restaurants, output_path = os.path.join("plots", "near_fastfood.png"))
    
    min_point = Point(x = -98.59798601768219, y = 29.56226932638067, data = {"name": "Min Point"})
    max_point = Point(x = -98.58525037258016, y = 29.57124799015953, data = {"name": "Max Point"})

    bb = BoundingBox(
        min_x = min_point.x, 
        min_y = min_point.y, 
        max_x = max_point.x, 
        max_y = max_point.y
    )

    points_within_bb = qt1.within_bb(bb)

    points_within_bb.extend([min_point, max_point])
    print(points_within_bb)
    plot_bounding_box_and_points(points = points_within_bb, bb = bb, output_path = os.path.join("plots", "fastfood_bounding.png"))

if __name__ == '__main__':
    main()


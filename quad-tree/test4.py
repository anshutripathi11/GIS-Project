# Test on Actual Data
# Parks in San Antonio

from helper import load_points_from_geojson, calculate_boundary, visualize, plot_near_neighbors, plot_bounding_box_and_points
from quad_tree import QuadTree, Point, BoundingBox
import os

def main():
    # Load points from GeoJSON
    geojson_file = os.path.join("..", "gis_data", "parks_sanantonio.geojson")
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

    print("Number of Parks inserted", inserted)

    # Visulize the QT
    visualize(qt1, xsize = 12, ysize = 12, save_plot = True, file_name = os.path.join("plots", "sa_parks_qt.png"))

    # Perform Point search 
    point = qt1.find((-98.4991157, 29.4260475))
    print(point)

    # Perform Nearest Neighbor search 
    current_location = Point(-98.49611109016035, 29.42408619530832, {"name": "UTSA SP1"})
    near_parks = qt1.nearest_neighbors(point = current_location, count = 5)
    print(near_parks)
    near_parks.append(current_location)
    plot_near_neighbors(points = near_parks, output_path = os.path.join("plots", "near_maps.png"))
    
    min_point = Point(x = -98.50036957570951, y = 29.421300821345632, data = {"name": "Min Point"})
    max_point = Point(x = -98.48749951848947, y = 29.429557651223536, data = {"name": "Max Point"})

    bb = BoundingBox(
        min_x = min_point.x, 
        min_y = min_point.y, 
        max_x = max_point.x, 
        max_y = max_point.y
    )

    points_within_bb = qt1.within_bb(bb)

    points_within_bb.extend([min_point, max_point])

    print(points_within_bb)

    plot_bounding_box_and_points(points = points_within_bb, bb = bb, output_path = os.path.join("plots", "bounding.png"))

if __name__ == '__main__':
    main()


import RTreeWrapper
import helper
import os
import Rtree
import time
import matplotlib.pyplot as plt

def test_parks():
    geojson_file = os.path.join("..", "gis_data", "parks_sanantonio.geojson")
    all_points = helper.load_points_from_geojson(geojson_file)

    rtree = RTreeWrapper.RTree(B=150)
    rtree.build_from_points(all_points)

    print(rtree.point_query((-98.4991157, 29.4260475)))


    current_location = Rtree.Point(("UTSA SP1", -98.49611109016035, 29.42408619530832))
    near_parks = rtree.nearest_neighbors(
        (current_location.x, current_location.y), 
        k = 10
    )
    type(near_parks[0][0])
    near_parks = list(map(lambda point: Rtree.Point((point[0].get("name", ""), point[1], point[2])), near_parks))
    near_parks.append(current_location)

    helper.plot_near_neighbors(points = near_parks, output_path = os.path.join("plots", "near_parks.png"))

    result = rtree.range_search(
        (-98.50036957570951, 
        29.421300821345632, 
        -98.48749951848947, 
        29.429557651223536)
    )

    result = list(map(lambda point: Rtree.Point((point[0].get("name", ""), point[1], point[2])), result))
    print(result[:100])
    # helper.plot_near_neighbors(points = result, output_path = os.path.join("plots", "near_parks2.png"))

def test_fastfoods():
    geojson_file = os.path.join("..", "gis_data", "fastfood.geojson")
    all_points = helper.load_points_from_geojson(geojson_file)

    print(len(all_points))

    rtree = RTreeWrapper.RTree(B=150)
    rtree.build_from_points(all_points)

    print(rtree.point_query((-95.7210958, 29.863109)))

    current_location = Rtree.Point(("SAT Int Airport", -98.47314277856472, 29.526606308748846))
    near_parks = rtree.nearest_neighbors(
        (current_location.x, current_location.y), 
        k = 20
    )
    type(near_parks[0][0])
    near_parks = list(map(lambda point: Rtree.Point((point[0].get("name", ""), point[1], point[2])), near_parks))
    near_parks.append(current_location)

    helper.plot_near_neighbors(points = near_parks, output_path = os.path.join("plots", "near_fastfood.png"))

    result = rtree.range_search(
        (-98.50036957570951, 
        29.421300821345632, 
        -98.48749951848947, 
        29.429557651223536)
    )

    result = list(map(lambda point: Rtree.Point((point[0].get("name", ""), point[1], point[2])), result))
    print(result[:100])

if __name__ == "__main__":
    test_fastfoods()
    test_parks()
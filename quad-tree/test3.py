# QT Insertion Process time
# QT Point Search time
# QT Nearest Neighbor Search 
# QT Bounding Box Search 

import time
import os
import matplotlib.pyplot as plt
from helper import generate_random_points
from quad_tree import QuadTree, BoundingBox, Point

def test_qt_insertion(sizes):
    times = []
    for size in sizes:
        points = generate_random_points(size, (-100, 100), (-100, 100))
        start = time.perf_counter()
        qt = QuadTree(center=(0, 0), width=200, height=200, capacity=51)
        for pt in points:
            qt.insert(pt)
        times.append(time.perf_counter() - start)

    plt.figure()
    plt.plot(sizes, times, label="Insertion Time")
    plt.xlabel("Number of Points")
    plt.ylabel("Total Time (seconds)")
    plt.title("QuadTree Insertion Performance")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "qt_insertion_performance.png"), bbox_inches='tight', pad_inches=0.1, dpi=500)

def test_qt_point_search(sizes):
    times = []
    for size in sizes:
        points = generate_random_points(size, (-100, 100), (-100, 100))
        qt = QuadTree(center=(0, 0), width=200, height=200, capacity=51)
        for pt in points:
            qt.insert(pt)

        start = time.perf_counter()
        for pt in points:
            _ = qt.find(pt)
        times.append(time.perf_counter() - start)

    plt.figure()
    plt.plot(sizes, times, label="Point Search Time")
    plt.xlabel("Number of Points")
    plt.ylabel("Total Time (seconds)")
    plt.title("QuadTree Point Search Performance")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "qt_point_search_performance.png"), bbox_inches='tight', pad_inches=0.1, dpi=500)

def test_qt_nearest_neighbors(sizes, neighbors_to_find=10):
    times = []
    for size in sizes:
        points = generate_random_points(size, (-100, 100), (-100, 100))
        qt = QuadTree(center=(0, 0), width=200, height=200, capacity=51)
        for pt in points:
            qt.insert(pt)
        query_points = points[:size // 2]

        start = time.perf_counter()
        for q in query_points:
            _ = qt.nearest_neighbors(q, neighbors_to_find)
        times.append(time.perf_counter() - start)

    plt.figure()
    plt.plot(sizes, times, label="Nearest Neighbors")
    plt.xlabel("Number of Points")
    plt.ylabel("Total Time (seconds)")
    plt.title("QuadTree Nearest Neighbors Performance")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "qt_nearest_neighbors_performance.png"), bbox_inches='tight', pad_inches=0.1, dpi=500)

def test_qt_bounding_box(sizes, bb_half_size=15):
    times = []
    for size in sizes:
        points = generate_random_points(size, (-100, 100), (-100, 100))
        qt = QuadTree(center=(0, 0), width=200, height=200, capacity=51)
        for pt in points:
            qt.insert(pt)
        query_points = points[:size // 2]

        start = time.perf_counter()
        for q in query_points:
            bb = BoundingBox(q.x - bb_half_size, q.y - bb_half_size,
                             q.x + bb_half_size, q.y + bb_half_size)
            _ = qt.within_bb(bb)
        times.append(time.perf_counter() - start)

    plt.figure()
    plt.plot(sizes, times, label="Bounding Box Search")
    plt.xlabel("Number of Points")
    plt.ylabel("Total Time (seconds)")
    plt.title("QuadTree Bounding Box Search Performance")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "qt_bounding_box_performance.png"), bbox_inches='tight', pad_inches=0.1, dpi=500)

from kneed import KneeLocator

def test_qt_varying_capacity_with_elbow(fixed_size=100000, capacities=range(1, 1001, 50)):
    times = []
    points = generate_random_points(fixed_size, (-100, 100), (-100, 100))

    for cap in capacities:
        qt = QuadTree(center=(0, 0), width=200, height=200, capacity=cap)
        start = time.perf_counter()
        for pt in points:
            qt.insert(pt)
        times.append(time.perf_counter() - start)

    # Find elbow point
    kneedle = KneeLocator(capacities, times, curve='convex', direction='decreasing')
    elbow_x = kneedle.knee
    elbow_y = kneedle.knee_y

    # Plot
    plt.figure()
    plt.plot(capacities, times, label="Insertion Time")
    if elbow_x is not None:
        plt.axvline(x=elbow_x, color='red', linestyle='--', label=f"Elbow Point: {elbow_x}")
        plt.scatter([elbow_x], [elbow_y], color='red')
    plt.xlabel("Node Capacity")
    plt.ylabel("Total Time (seconds)")
    plt.title("QuadTree Insertion vs Varying Capacity")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "qt_varying_capacity_with_elbow.png"), bbox_inches='tight', pad_inches=0.1, dpi=500)


# Run All
sizes = list(range(20, 500))  # You can adjust
test_qt_insertion(sizes)
test_qt_point_search(sizes)
test_qt_nearest_neighbors(sizes)
test_qt_bounding_box(sizes)
test_qt_varying_capacity_with_elbow()

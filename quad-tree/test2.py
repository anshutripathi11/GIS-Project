# Brute Force Testing
# QT VS Sorting
# Nearest Neighbor Search
# Range Search using Bounding Boxes

import time
from helper import generate_random_points
import matplotlib.pyplot as plt
from quad_tree import QuadTree, BoundingBox, Point, euclidean_distance
import os

def brute_force_nearest_neighbors(all_points, target_point, count):
    return sorted(all_points, key=lambda p: euclidean_distance(p, target_point))[:count]

def brute_force_within_bb(all_points, bb):
    return [p for p in all_points if bb.contains(p)]

def test_nearest_neighbor_performance(sizes, neighbors_to_find=10):
    qt_times = []
    bf_times = []
    
    for size in sizes:
        half_size = size // 2
        all_points = generate_random_points(size, (-100, 100), (-100, 100))
        tree = QuadTree(center=(0, 0), width=200, height=200, capacity=4)
        for pt in all_points:
            tree.insert(pt)

        query_points = all_points[:half_size]

        # QuadTree timing
        start = time.perf_counter()
        for q in query_points:
            _ = tree.nearest_neighbors(q, neighbors_to_find)
        qt_times.append((time.perf_counter() - start) )

        # Brute-force timing (skip if too large)
        if size <= 100_000:
            start = time.perf_counter()
            for q in query_points:
                _ = brute_force_nearest_neighbors(all_points, q, neighbors_to_find)
            bf_times.append((time.perf_counter() - start) )
        else:
            bf_times.append(None)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, qt_times, label="QuadTree")
    plt.plot(sizes[:len(bf_times)], bf_times, label="Brute Force")
    plt.xlabel("Number of Points")
    plt.ylabel("Total Time (seconds)")
    plt.title("Nearest Neighbor Performance")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "nearest_neighbor_performance.png"), bbox_inches='tight', pad_inches=0.1, dpi=500)

def test_bounding_box_performance(sizes, bb_half_size=15):
    qt_times = []
    bf_times = []

    for size in sizes:
        half_size = size // 2
        all_points = generate_random_points(size, (-100, 100), (-100, 100))
        tree = QuadTree(center=(0, 0), width=200, height=200, capacity=4)
        for pt in all_points:
            tree.insert(pt)

        query_points = all_points[:half_size]

        # QuadTree timing
        start = time.perf_counter()
        for q in query_points:
            bb = BoundingBox(q.x - bb_half_size, q.y - bb_half_size,
                             q.x + bb_half_size, q.y + bb_half_size)
            _ = tree.within_bb(bb)
        qt_times.append((time.perf_counter() - start))

        # Brute-force timing (skip if too large)
        if size <= 100_000:
            start = time.perf_counter()
            for q in query_points:
                bb = BoundingBox(q.x - bb_half_size, q.y - bb_half_size,
                                 q.x + bb_half_size, q.y + bb_half_size)
                _ = brute_force_within_bb(all_points, bb)
            bf_times.append((time.perf_counter() - start))
        else:
            bf_times.append(None)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, qt_times, label="QuadTree")
    plt.plot(sizes[:len(bf_times)], bf_times, label="Brute Force")
    plt.xlabel("Number of Points")
    plt.ylabel("Avg Time per Query (seconds)")
    plt.title("Bounding Box Search Performance")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "bounding_box_search_performance.png"), bbox_inches='tight', pad_inches=0.1, dpi=500)

sizes = list(range(20, 500))
test_nearest_neighbor_performance(sizes)
test_bounding_box_performance(sizes)

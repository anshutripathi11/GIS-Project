import RTreeWrapper
import helper
import os
import Rtree
import time
import matplotlib.pyplot as plt
from tqdm import tqdm
from kneed import KneeLocator

for idx, size in enumerate([7, 10, 50]):
    # Create R-tree instance
    rtree = RTreeWrapper.RTree(B=5)

    # Build from in-memory data
    points = helper.generate_random_points(size)

    print("points generated")
    rtree.build_from_points(points)

    helper.visualize_rtree(rtree.root, 
    schema = {
        "figure_size": (10, 10),
        "leaf_node_color": "blue",
        "branch_node_color": "red",
        "leaf_node_linestyle": "-",
        "branch_node_linestyle": "--",
        "leaf_node_linewidth": 1.2,
        "branch_node_linewidth": 0.8,
        "marker": "X",
        "marker_size": 6,
        "marker_color": "black",
        "marker_fontsize": "6",
        "horizontal_alignment": "left", 
        "vertical_alignment": "bottom",
        "title": f"R-Tree Visualization\nNode Capacity: 5; Inserted Points: {size}\n(Leaf=Blue Solid, Branch=Red Dashed)",
        "save_plot": True,
        "plot_name": os.path.join("plots", f"plot{idx + 1}.png"),
        "file_dpi": 500
    })
    print(f"Plot {idx + 1} saved!")

def brute_force_nearest_neighbors(all_points, target_point, count):
    return sorted(all_points, key=lambda p: Rtree.euclidean_distance(p, target_point))[:count]

def brute_force_within_bb(all_points, min_x, min_y, max_x, max_y):
    return [
        p for p in all_points
        if min_x <= p.x <= max_x and min_y <= p.y <= max_y
    ]

def test_rt_insertion(sizes, RUN_COUNT=10):
    times = []
    for size in tqdm(sizes, desc="Testing insertion", unit="size"):
        run_times = []
        for _ in range(RUN_COUNT):
            points = helper.generate_random_points(size, (-100, 100), (-100, 100))
            start = time.perf_counter()
            rtree = RTreeWrapper.RTree(B=51)
            rtree.build_from_points(points)
            run_times.append(time.perf_counter() - start)

        avg_time = sum(run_times) / RUN_COUNT
        times.append(avg_time)

    plt.figure()
    plt.plot(sizes, times, label="Average Insertion Time")
    plt.xlabel("Number of Points")
    plt.ylabel("Average Time (seconds)")
    plt.title("R-Tree Insertion Performance")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "r_tree_insertion_performance.png"), bbox_inches='tight', pad_inches=0.1, dpi=500)


def test_rt_varying_capacity_with_elbow(fixed_size=5000, capacities=range(50, 1001, 50)):
    times = []
    points = helper.generate_random_points(fixed_size, (-100, 100), (-100, 100))

    for cap in tqdm(capacities, desc="Testing R-Tree capacities", unit="cap"):
        rtree = RTreeWrapper.RTree(B=cap)
        start = time.perf_counter()
        rtree.build_from_points(points)
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
    plt.xlabel("Node Capacity (B value)")
    plt.ylabel("Total Time (seconds)")
    plt.title("R-Tree Insertion vs Varying Capacity")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "rtree_varying_capacity_with_elbow.png"), bbox_inches='tight', pad_inches=0.1, dpi=500)

def test_rt_point_search(sizes, RUN_COUNT=10):
    times = []
    for size in tqdm(sizes, desc="Testing R-Tree Point Search", unit="pts"):
        total_time = 0.0

        for _ in range(RUN_COUNT):
            points = helper.generate_random_points(size, (-100, 100), (-100, 100))
            rtree = RTreeWrapper.RTree(B=51)
            rtree.build_from_points(points)

            start = time.perf_counter()
            for pt in points:
                _ = rtree.point_query((pt.x, pt.y))
            total_time += time.perf_counter() - start

        avg_time = total_time / RUN_COUNT
        times.append(avg_time)

    plt.figure()
    plt.plot(sizes, times, label="Average Point Search Time", color="purple")
    plt.xlabel("Number of Points")
    plt.ylabel("Average Time (seconds)")
    plt.title("R-Tree Point Search Performance")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "rtree_point_search_performance.png"), bbox_inches='tight', pad_inches=0.1, dpi=500)

def test_rt_nearest_neighbors(sizes, neighbors_to_find=10, RUN_COUNT=10):
    times = []

    for size in tqdm(sizes, desc="Testing R-Tree Nearest Neighbors", unit="pts"):
        total_time = 0.0

        for _ in range(RUN_COUNT):
            points = helper.generate_random_points(size, (-100, 100), (-100, 100))
            rtree = RTreeWrapper.RTree(B=51)
            rtree.build_from_points(points)

            query_points = points[:size // 2]
            start = time.perf_counter()
            for q in query_points:
                _ = rtree.nearest_neighbors((q.x, q.y), neighbors_to_find)
            total_time += time.perf_counter() - start

        avg_time = total_time / RUN_COUNT
        times.append(avg_time)

    plt.figure()
    plt.plot(sizes, times, label="Average Nearest Neighbors Time", color="orange")
    plt.xlabel("Number of Points")
    plt.ylabel("Average Time (seconds)")
    plt.title("R-Tree Nearest Neighbors Performance")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "rtree_nearest_neighbors_performance.png"), bbox_inches='tight', pad_inches=0.1, dpi=500)

def test_rt_bounding_box(sizes, bb_half_size=15, RUN_COUNT=10):
    times = []

    for size in tqdm(sizes, desc="Testing R-Tree Bounding Box Search", unit="pts"):
        total_time = 0.0

        for _ in range(RUN_COUNT):
            points = helper.generate_random_points(size, (-100, 100), (-100, 100))
            rtree = RTreeWrapper.RTree(B=51)
            rtree.build_from_points(points)

            query_points = points[:size // 2]
            start = time.perf_counter()
            for q in query_points:
                bb = [q.x - bb_half_size, q.x + bb_half_size,
                      q.y - bb_half_size, q.y + bb_half_size]
                _ = rtree.range_search(bb)
            total_time += time.perf_counter() - start

        avg_time = total_time / RUN_COUNT
        times.append(avg_time)

    plt.figure()
    plt.plot(sizes, times, label="Average Bounding Box Search Time", color="green")
    plt.xlabel("Number of Points")
    plt.ylabel("Average Time (seconds)")
    plt.title("R-Tree Bounding Box Search Performance")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "rtree_bounding_box_performance.png"),
                bbox_inches='tight', pad_inches=0.1, dpi=500)
    
def test_rt_vs_brute_nearest_neighbor(sizes, neighbors_to_find=10, RUN_COUNT=5):
    rt_times = []
    bf_times = []

    for size in tqdm(sizes, desc="Testing Nearest Neighbor (R-Tree vs Brute)", unit="pts"):
        rt_total = 0.0
        bf_total = 0.0

        for _ in range(RUN_COUNT):
            all_points = helper.generate_random_points(size, (-100, 100), (-100, 100))
            query_points = all_points[:size // 2]

            # R-Tree build
            rtree = RTreeWrapper.RTree(B=51)
            rtree.build_from_points(all_points)

            # R-Tree timing
            start = time.perf_counter()
            for q in query_points:
                _ = rtree.nearest_neighbors((q.x, q.y), neighbors_to_find)
            rt_total += time.perf_counter() - start

            # Brute-force timing (only for small sizes)
            if size <= 100_000:
                start = time.perf_counter()
                for q in query_points:
                    _ = brute_force_nearest_neighbors(all_points, q, neighbors_to_find)
                bf_total += time.perf_counter() - start

        rt_times.append(rt_total / RUN_COUNT)
        bf_times.append((bf_total / RUN_COUNT) if size <= 100_000 else None)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, rt_times, label="R-Tree", color='blue')
    if any(bf is not None for bf in bf_times):
        plt.plot(sizes[:len(bf_times)], [t for t in bf_times if t is not None], label="Brute Force", color='orange')
    plt.xlabel("Number of Points")
    plt.ylabel("Average Time (seconds)")
    plt.title("R-Tree vs Brute Force: Nearest Neighbor Performance")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "rtree_vs_brute_nearest_neighbor_performance.png"),
                bbox_inches='tight', pad_inches=0.1, dpi=500)

def test_rt_bounding_box_performance(sizes, bb_half_size=15, RUN_COUNT=10):
    rt_times = []
    bf_times = []

    for size in tqdm(sizes, desc="R-Tree Bounding Box Search", unit="size"):
        rt_time_acc = 0
        bf_time_acc = 0
        points = helper.generate_random_points(size, (-100, 100), (-100, 100))
        query_points = points[:size // 2]

        for _ in range(RUN_COUNT):
            rtree = RTreeWrapper.RTree(B=51)
            rtree.build_from_points(points)

            # R-Tree timing
            start = time.perf_counter()
            for q in query_points:
                bb = [q.x - bb_half_size, q.x + bb_half_size,q.y - bb_half_size, q.y + bb_half_size]
                _ = rtree.range_search(bb)
            rt_time_acc += (time.perf_counter() - start)

            # Brute-force timing (skip for large sizes)
            if size <= 100_000:
                start = time.perf_counter()
                for q in query_points:
                    bb = [q.x - bb_half_size, q.x + bb_half_size,q.y - bb_half_size, q.y + bb_half_size]
                    _ = brute_force_within_bb(points, *bb)
                bf_time_acc += (time.perf_counter() - start)

        rt_times.append(rt_time_acc / RUN_COUNT)
        bf_times.append(bf_time_acc / RUN_COUNT if size <= 100_000 else None)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, rt_times, label="Brute Force")
    plt.plot(sizes[:len(bf_times)], bf_times, label="R-Tree")
    plt.xlabel("Number of Points")
    plt.ylabel("Average Time (seconds)")
    plt.title("Bounding Box Search Performance")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "rtree_bounding_box__cmp_performance.png"), bbox_inches='tight', pad_inches=0.1, dpi=500)


if __name__ == "__main__":
    test_rt_insertion(list(range(20, 500)))
    test_rt_varying_capacity_with_elbow()
    test_rt_point_search(list(range(20, 500)))
    test_rt_nearest_neighbors(list(range(20, 500)))
    test_rt_bounding_box(list(range(20, 500)))
    test_rt_vs_brute_nearest_neighbor(list(range(20, 500)))
    test_rt_bounding_box_performance(list(range(20, 500)))

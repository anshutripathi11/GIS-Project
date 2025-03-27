# Python Program to Visualize a Quad Tree Insertion process using Video

import make_video
from helper import generate_random_points

all_points = generate_random_points(
    x = 100,
    x_range = (-100, 100), 
    y_range = (-100, 100)
)
save_path = make_video.visualize_insertion(
    points = all_points, 
    capacity = 4, 
    fps = 5, 
    max_frames_in_memory = 100
)

print("Saved at", save_path)

# Re-import necessary modules and re-execute the hybrid approach code after reset
import os
import uuid
import cv2
import numpy as np
from datetime import datetime
from tqdm import tqdm
from matplotlib import pyplot
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from quad_tree import *

# Sample calculate_boundary and QuadTree placeholders (must be replaced by real implementation)
from collections import namedtuple

Boundary = namedtuple("Boundary", ["center", "width", "height"])
Point = namedtuple("Point", ["x", "y"])

def calculate_boundary(points, buffer_ratio=0.05):
    x_coords = [p.x for p in points]
    y_coords = [p.y for p in points]
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    x_center = (min_x + max_x) / 2
    y_center = (min_y + max_y) / 2
    width = (max_x - min_x) * (1 + buffer_ratio)
    height = (max_y - min_y) * (1 + buffer_ratio)
    return Boundary(center=Point(x_center, y_center), width=width, height=height)

# Re-define visualize and hybrid insertion
import numpy as np
from matplotlib import pyplot
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

def visualize(tree, xsize=10, ysize=10, title="Quad Tree Visualization"):
    fig = pyplot.figure(figsize=(xsize, ysize))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)

    def draw_all_nodes(node):
        for pnt in node.points:
            ax.plot(pnt.x, pnt.y, ".", color="black")
        if any([node.ul, node.ur, node.ll, node.lr]):
            draw_lines(node)
        for child in [node.ul, node.ur, node.ll, node.lr]:
            if child:
                draw_all_nodes(child)

    def draw_lines(node):
        bb = node.bounding_box
        ax.plot([bb.min_x, bb.max_x], [node.center.y, node.center.y], color="black", linewidth=1.5)
        ax.plot([node.center.x, node.center.x], [bb.min_y, bb.max_y], color="black", linewidth=1.5)

    # Set bounds and layout
    half_width = tree.width / 2
    half_height = tree.height / 2
    min_x = tree.center.x - half_width
    max_x = tree.center.x + half_width
    min_y = tree.center.y - half_height
    max_y = tree.center.y + half_height
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    ax.set_aspect('equal', adjustable='box')

    ax.set_title(title, fontsize=12, pad=10)
    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)  # Show frame, but no ticks

    draw_all_nodes(tree._root)

    fig.tight_layout(pad=2.0)  # Ensure title isn't clipped
    canvas.draw()

    image = np.frombuffer(canvas.tostring_rgb(), dtype='uint8')
    image = image.reshape(canvas.get_width_height()[::-1] + (3,))
    pyplot.close(fig)
    return image

def visualize_insertion(points, capacity=4, fps=15, max_frames_in_memory=200):
    now = datetime.now()
    save_dir = now.strftime("%m%d%Y_%H%M%S") + "_" + (uuid.uuid4().hex[:5])
    save_path = os.path.join(os.getcwd(), save_dir)
    os.makedirs(save_path, exist_ok=True)

    boundary = calculate_boundary(points=points)
    qt = QuadTree(center=boundary.center, width=boundary.width, height=boundary.height, capacity=capacity)

    frame_buffer = []
    part_index = 0
    video_parts = []
    title_template = "Inserting ({:.3f}, {:.3f}) in Quad Tree with Capacity {}. Total Points: {}"

    for index, point in enumerate(tqdm(points, desc="Processing")):
        qt.insert(point)
        frame = visualize(tree=qt, title=title_template.format(point.x, point.y, capacity, index + 1))
        frame_buffer.append(frame)

        if len(frame_buffer) >= max_frames_in_memory:
            height, width, _ = frame_buffer[0].shape
            part_path = os.path.join(save_path, f"part_{part_index}.avi")
            writer = cv2.VideoWriter(part_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))
            for frame in frame_buffer:
                writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            writer.release()
            video_parts.append(part_path)
            frame_buffer.clear()
            part_index += 1

    if frame_buffer:
        height, width, _ = frame_buffer[0].shape
        part_path = os.path.join(save_path, f"part_{part_index}.avi")
        writer = cv2.VideoWriter(part_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))
        for frame in frame_buffer:
            writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        writer.release()
        video_parts.append(part_path)

    final_video_path = os.path.join(save_path, "quadtree_insertion.avi")
    final_writer = cv2.VideoWriter(final_video_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))

    for part in video_parts:
        cap = cv2.VideoCapture(part)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            final_writer.write(frame)
        cap.release()

    final_writer.release()

    return final_video_path

import blender_hand_drawn_npr.point_utils as point_utils
import blender_hand_drawn_npr.raster_utils as raster_utils
import blender_hand_drawn_npr.vector_utils as vector_utils

import numpy as np


def illustrate():

    # Read render passes.
    object_image = raster_utils.read_image("/tmp/img/IndexOB0001.png")
    depth_image = raster_utils.read_image("/tmp/img/Depth0001NORM.png")
    diffdir_image = raster_utils.read_image("/tmp/img/DiffDir0001.png")

    # Get the first contour group (seems good enough).
    edge_coords = raster_utils.path_trace(object_image)[0]
    # Convert approximations to pixel values (nearest integer).
    edge_coords = np.round(edge_coords).astype(np.int)

    # Optimise points.
    edge_coords = raster_utils.coord_linear_optimise(edge_coords)

    # Create a list of unique Points, preserving the original order.
    points = []
    seen = set()
    for coord in edge_coords:
        r, c = coord[0], coord[1]
        if (r, c) not in seen:
            seen.add((r, c))

            depth_intensity = depth_image[r, c]
            diffdir_intensity = diffdir_image[r, c]
            point = point_utils.create_point(c, r, depth_intensity, diffdir_intensity)
            points.append(point)

    # Prepare the vector drawing.
    out_file = "/tmp/img/vector_rendering.svg"
    drawing = vector_utils.create(out_file, object_image.shape[1], object_image.shape[0])

    # Define the thickness factor.
    f = 2
    # Create vector strokes.
    for i in range(0, len(points)):
        if i != len(points) - 1:
            # Draw a Stroke between adjacent Points.
            vector_utils.draw_straight_stroke(points[i], points[i + 1], f, drawing)
        else:
            # Draw a Stroke back to the original Point to close the path.
            vector_utils.draw_straight_stroke(points[i], points[0], f, drawing)

    vector_utils.save(drawing)


if __name__ == "__main__":
    illustrate()

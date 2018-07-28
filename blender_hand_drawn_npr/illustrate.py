import blender_hand_drawn_npr.point_utils as point_utils
import blender_hand_drawn_npr.raster_utils as raster_utils
import blender_hand_drawn_npr.vector_utils as vector_utils

import os
import numpy as np
import tempfile
import logging


class Illustrator:

    img_dir = None
    object_image = None
    depth_image = None
    diffdir_image = None
    illustration = None

    def __init__(self, img_dir):

        self.img_dir = img_dir
        # Read render passes.
        self.object_image = raster_utils.read_image(os.path.join(self.img_dir,
                                                                 "IndexOB0001.png"))
        self.depth_image = raster_utils.read_image(os.path.join(self.img_dir,
                                                                "Depth0001.png"))
        self.diffdir_image = raster_utils.read_image(os.path.join(self.img_dir,
                                                                  "DiffDir0001.png"))
        # Prepare the vector illustration.
        out_file = os.path.join(self.img_dir,
                                "vector_rendering.svg")  # TODO: Make user-configurable.
        self.illustration = vector_utils.create(out_file,
                                                self.object_image.shape[1],
                                                self.object_image.shape[0])

    def illustrate_silhouette(self):

        # Get the first contour group (seems good enough).
        try:
            edge_coords = raster_utils.path_trace(self.object_image)[0]
        except IndexError:
            # No silhouette can be drawn if no paths are found...
            return

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

                depth_intensity = self.depth_image[r, c]
                diffdir_intensity = self.diffdir_image[r, c]
                point = point_utils.create_point(c, r, depth_intensity, diffdir_intensity)
                points.append(point)

        # Define the thickness factor.
        f = 10  # TODO: Make user-configurable.
        # Create vector strokes.
        for i in range(0, len(points)):
            if i != len(points) - 1:
                # Draw a Stroke between adjacent Points.
                vector_utils.draw_straight_stroke(points[i], points[i + 1], f, self.illustration)
            else:
                # Draw a Stroke back to the original Point to close the path.
                vector_utils.draw_straight_stroke(points[i], points[0], f, self.illustration)

    def illustrate_internal_edges(self):
        pass

    def save(self):
        vector_utils.save(self.illustration)


if __name__ == "__main__":
    illustrator = Illustrator("/tmp/int_edge")
    illustrator.illustrate_internal_edges()
    illustrator.save()

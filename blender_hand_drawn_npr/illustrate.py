import blender_hand_drawn_npr.point_utils as point_utils
import blender_hand_drawn_npr.raster_utils as raster_utils
import blender_hand_drawn_npr.vector_utils as vector_utils

import os
import numpy as np
import tempfile
import logging

# TODO: Temp imports
import matplotlib.pyplot as plt
from skimage import io

logger = logging.getLogger(__name__)


class Illustrator:
    img_dir = None
    object_image = None
    depth_image = None
    diffdir_image = None
    uv_image = None
    normal_image = None
    illustration = None

    def __init__(self, img_dir):

        logger.debug("Instantiating Illustrator...")

        self.img_dir = img_dir

        # Read render passes.
        self.object_image = raster_utils.read_gray_image(os.path.join(self.img_dir,
                                                                      "IndexOB0001.png"))
        self.depth_image = raster_utils.read_gray_image(os.path.join(self.img_dir,
                                                                     "Depth0001.png"))
        self.diffdir_image = raster_utils.read_gray_image(os.path.join(self.img_dir,
                                                                       "DiffDir0001.png"))
        self.normal_image = raster_utils.read_rgb_image(os.path.join(self.img_dir,
                                                                     "Normal0001.tif"))
        self.uv_image = raster_utils.read_rgb_image(os.path.join(self.img_dir,
                                                                 "UV0001.tif"))

        # Prepare the vector canvas.
        out_file = os.path.join(self.img_dir,
                                "vector_rendering.svg")  # TODO: Make user-configurable.
        self.illustration = vector_utils.create_canvas(out_file,
                                                       self.object_image.shape[1],
                                                       self.object_image.shape[0])

    def illustrate_silhouette(self):

        logger.info("Illustrating silhouette...")

        try:
            # Assume the first contour group captures the needed edges.
            coords = raster_utils.path_trace(self.object_image)[0]
        except IndexError:
            # No silhouette can be drawn if no paths are found...
            logger.warning("No silhouette could be found.")
            return

        points = point_utils.coords_to_points(coords=coords,
                                              depth_image=self.depth_image,
                                              diffdir_image=self.diffdir_image,
                                              uv_image=self.uv_image)
        points = point_utils.remove_duplicate_coords(points)
        points = point_utils.linear_optimise(points)

        # Define the thickness factor.
        f = 10  # TODO: Make user-configurable.

        # Draw vector strokes.
        for i in range(0, len(points)):
            if i != len(points) - 1:
                # Draw a Stroke between adjacent Points.
                vector_utils.draw_straight_stroke(points[i], points[i + 1], f, self.illustration)
            else:
                # Draw a Stroke back to the original Point to close the path.
                vector_utils.draw_straight_stroke(points[i], points[0], f, self.illustration)

    def illustrate_relief_grid(self):
        """
        Illustrate streamlines following UV directions. This results in a superimposed grid arrangement which
        follows the surface topology.

        :return:
        """

        logger.info("Illustrating relief grid...")


        num_slices = 10  # TODO: Make User configurable.

        u_streamlines, v_streamlines = raster_utils.uv_streamlines(num_slices,
                                                                   self.depth_image,
                                                                   self.diffdir_image,
                                                                   self.uv_image)

        # Define the thickness factor.
        f = 3  # TODO: Make user-configurable.

        for points in u_streamlines:
            # Draw vector strokes.
            for i in range(0, len(points)):
                if i != len(points) - 1:
                    # Draw a Stroke between adjacent Points.
                    vector_utils.draw_straight_stroke(points[i], points[i + 1], f, self.illustration)

        for points in v_streamlines:
            # Draw vector strokes.
            for i in range(0, len(points)):
                if i != len(points) - 1:
                    # Draw a Stroke between adjacent Points.
                    vector_utils.draw_straight_stroke(points[i], points[i + 1], f, self.illustration)

        # # TODO: Remove "boundaries" return value from uv_slicemask function?
        # u_slicemask, boundaries = raster_utils.uv_slicemask(self.u_image, min_rgb[0], max_rgb[0], num_slices)
        # # v_slicemask = raster_utils.uv_slicemask(self.v_image, min_rgb[1], max_rgb[1], num_slices)
        #
        # # Compute streamlines in both UV directions. Each coord_set will be a closed loop around each slicemask
        # # segment. As such each coord_set will consist of two streamlines and two edges (which must later be discarded).
        # rejection_threshold = 100  # TODO: Consider making User configurable.
        # u_streamloops_coords = raster_utils.path_trace(u_slicemask, rejection_threshold)
        # # v_streamline_coord_sets = raster_utils.path_trace(v_slicemask, rejection_threshold)
        # # streamloop_coord_lists = u_streamloop_coord_sets #+ v_streamline_coord_sets
        #
        # # Build a list of Point lists representing each streamline loop.
        # u_streamlines = []
        # for u_streamloop_coords in u_streamloops_coords:
        #     points = point_utils.coords_to_points(coords=u_streamloop_coords,
        #                                           depth_image=self.depth_image,
        #                                           diffdir_image=self.diffdir_image,
        #                                           u_image=self.u_image,
        #                                           v_image=self.v_image)
        #     points = point_utils.remove_duplicate_coords(points)
        #
        #     # Break streamloop into two distinct streamlines.
        #     u_threshold = 100  #
        #
        #     u_streamlines.append(points)

        # print(boundaries)
        # raster_image = np.zeros_like(self.object_image)
        # v_buffer = 100
        # u_buffer = 1000
        #
        # accepted_streamlines = []
        # for streamline in u_streamloops_points:
        #     print("hi")
        #     # accepted_streamline = []
        #     # for point in streamline:
        #     #     if point.u > ()

        # for streamline in streamlines:
        #     u_terminators = (min([i.v for i in streamline]), max([i.v for i in streamline]))
        #     print(u_terminators)
        #     for point in streamline:
        #         if point.v > (u_terminators[0] + v_buffer) and point.v < (u_terminators[1] - v_buffer):
        #             if point.u > (boundaries[1] - u_buffer) and point.u < (boundaries[1] + u_buffer):
        #                 print(point)
        #                 raster_image[point.y, point.x] = 1

        # io.imsave("/tmp/test.png", raster_image)

        # TODO: Render Strokes and tings.

    def save(self):
        vector_utils.save(self.illustration)


if __name__ == "__main__":
    # illustrator = Illustrator("/tmp/flat_plane_ortho_uv")
    # illustrator = Illustrator("/tmp/bump_plane_ortho_uv")
    illustrator = Illustrator("/tmp/undulating_plane")
    illustrator.illustrate_silhouette()
    illustrator.illustrate_relief_grid()
    illustrator.save()

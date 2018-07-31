import blender_hand_drawn_npr.point_utils as point_utils
import blender_hand_drawn_npr.raster_utils as raster_utils
import blender_hand_drawn_npr.vector_utils as vector_utils

import os
import numpy as np
import tempfile
import logging

logger = logging.getLogger(__name__)


class Illustrator:
    img_dir = None
    object_image = None
    depth_image = None
    diffdir_image = None
    uv_image = None
    u_image = None
    v_image = None
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
        # Tiff/png file formats are mapped to a non-linear colourspace, which skew the uv coords. Transform to linear
        # colorspace.
        uv_image = raster_utils.linearise_colourspace(self.uv_image)
        self.u_image = uv_image[:, :, 0]
        self.v_image = uv_image[:, :, 1]

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

        # Convert approximations to pixel values (nearest integer).
        coords = np.round(coords).astype(np.int)

        points = point_utils.coords_to_points(coords=coords,
                                              depth_image=self.depth_image,
                                              diffdir_image=self.diffdir_image,
                                              u_image=self.u_image,
                                              v_image=self.v_image)
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

        # It is not guaranteed that uv coords will be mapped across the full available colorspace (this depends on how
        # the User has uv unwrapped their model). The actual min max uv values will define the range over which
        # we will divide the image into slices, so compute that here.
        min_rgb, max_rgb = raster_utils.min_max_rgb(self.uv_image)
        num_slices = 10  # TODO: Make User configurable.

        u_slicemask = raster_utils.uv_slicemask(self.u_image, min_rgb[0], max_rgb[0], num_slices)
        v_slicemask = raster_utils.uv_slicemask(self.v_image, min_rgb[1], max_rgb[1], num_slices)

        # Compute streamlines in both UV directions. Each coord_set will be a closed loop around each slicemask
        # segment. As such each coord_set will consist of two streamlines and two edges (which must later be discarded).
        rejection_threshold = 100  # TODO: Consider making User configurable.
        u_streamline_coord_sets = raster_utils.path_trace(u_slicemask, rejection_threshold)
        v_streamline_coord_sets = raster_utils.path_trace(v_slicemask, rejection_threshold)
        streamline_coord_lists = u_streamline_coord_sets + v_streamline_coord_sets

        # Build a list of Point lists representing each streamline loop.
        streamlines = []
        for streamline_coord_list in streamline_coord_lists:
            coords = np.round(streamline_coord_list).astype(np.int)
            points = point_utils.coords_to_points(coords=coords,
                                                  depth_image=self.depth_image,
                                                  diffdir_image=self.diffdir_image,
                                                  u_image=self.u_image,
                                                  v_image=self.v_image)
            points = point_utils.remove_duplicate_coords(points)
            streamlines.append(points)

        # Eliminate streamline loop segments at the edges.
        for point in streamlines[0]:
            print(point)


        # TODO: Render Strokes and tings.

    def save(self):
        vector_utils.save(self.illustration)


if __name__ == "__main__":
    illustrator = Illustrator("/tmp/flat_plane_ortho_uv")
    # illustrator.illustrate_silhouette()
    illustrator.illustrate_relief_grid()
    # illustrator.save()

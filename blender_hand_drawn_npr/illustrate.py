import blender_hand_drawn_npr.point_utils as point_utils
import blender_hand_drawn_npr.raster_utils as raster_utils
import blender_hand_drawn_npr.vector_utils as vector_utils

import os
import tempfile
import logging
from collections import namedtuple

# TODO: Temp imports
import matplotlib.pyplot as plt
from skimage import io

logger = logging.getLogger(__name__)


class Illustrator:
    img_dir = None
    render_pass = None
    illustration = None

    def __init__(self, img_dir):

        logger.debug("Instantiating Illustrator...")

        self.img_dir = img_dir

        # Read render passes.
        object_image = raster_utils.read_gray_image(os.path.join(self.img_dir,
                                                                 "IndexOB0001.png"))
        depth_image = raster_utils.read_gray_image(os.path.join(self.img_dir,
                                                                "Depth0001.png"))
        diffdir_image = raster_utils.read_gray_image(os.path.join(self.img_dir,
                                                                  "DiffDir0001.png"))
        normal_image = raster_utils.read_rgb_image(os.path.join(self.img_dir,
                                                                "Normal0001.tif"))
        uv_image = raster_utils.read_rgb_image(os.path.join(self.img_dir,
                                                            "UV0001.tif"))
        uv_image = raster_utils.linearise_colourspace(uv_image)

        RenderPass = namedtuple("RenderPass", "object depth diffdir normal uv")
        self.render_pass = RenderPass(object=object_image,
                                      depth=depth_image,
                                      diffdir=diffdir_image,
                                      normal=normal_image,
                                      uv=uv_image)

        # Prepare the vector canvas.
        out_file = os.path.join(self.img_dir,
                                "vector_rendering.svg")  # TODO: Make user-configurable.
        self.illustration = vector_utils.create_canvas(out_file,
                                                       self.render_pass.object.shape[1],
                                                       self.render_pass.object.shape[0])

    def illustrate_silhouette(self):

        logger.info("Illustrating silhouette...")

        try:
            # Assume the first contour group captures the needed edges.
            coords = raster_utils.path_trace(self.render_pass.object)[0]
        except IndexError:
            # No silhouette can be drawn if no paths are found...
            logger.warning("No silhouette could be found.")
            return

        points = point_utils.coords_to_points(coords=coords,
                                              render_pass=self.render_pass)
        points = point_utils.remove_duplicate_coords(points)
        points = point_utils.optimise_path(points)

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

        u_slices = 10  # TODO: Make User configurable.
        v_slices = 10  # TODO: Make User configurable.
        u_threshold = 100  # TODO: Make User configurable.
        v_threshold = 100  # TODO: Make User configurable.

        u_streamlines, v_streamlines = raster_utils.uv_streamlines(u_slices=u_slices,
                                                                   u_threshold=u_threshold,
                                                                   v_slices=v_slices,
                                                                   v_threshold=v_threshold,
                                                                   render_pass=self.render_pass)
        streamlines = u_streamlines + v_streamlines

        # Define the thickness factor.
        f = 3  # TODO: Make user-configurable.

        for points in streamlines:
            # Draw vector strokes.
            vector_utils.draw_curved_stroke(points, 1, self.illustration)

            # for i in range(0, len(points)):
            #     if i != len(points) - 1:
            #         # Draw a Stroke between adjacent Points.
            #         vector_utils.draw_straight_stroke(points[i], points[i + 1], f, self.illustration)

    def save(self):
        vector_utils.save(self.illustration)


if __name__ == "__main__":
    # illustrator = Illustrator("/tmp/flat_plane_ortho_uv")
    # illustrator = Illustrator("/tmp/bump_plane_ortho_uv")
    illustrator = Illustrator("/tmp/undulating_plane")
    # illustrator.illustrate_silhouette()
    illustrator.illustrate_relief_grid()
    illustrator.save()

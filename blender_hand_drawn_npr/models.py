import logging
from collections import namedtuple

import imageio
from skimage import io, exposure

logger = logging.getLogger(__name__)


class Surface:

    def __init__(self, obj_image=None, z_image=None, diffdir_image=None, norm_image=None, u_image=None, v_image=None):
        self.obj_image = obj_image
        self.z_image = z_image
        self.diffdir_image = diffdir_image
        self.norm_image = norm_image
        self.u_image = u_image
        self.v_image = v_image

        self.SurfaceData = namedtuple("SurfaceData", "obj z diffdir norm_x norm_y u v")

    def init_obj_image(self, file_path):
        self.obj_image = io.imread(file_path, as_gray=True)
        logger.info("Object image loaded: %s", file_path)

    def init_z_image(self, file_path):
        self.z_image = io.imread(file_path, as_gray=True)
        logger.info("Z image loaded: %s", file_path)

    def init_diffdir_image(self, file_path):
        self.diffdir_image = io.imread(file_path, as_gray=True)
        logger.info("Diffdir image loaded: %s", file_path)

    def init_norm_image(self, file_path):
        # 16-bit colour-depth, use imageio.
        self.norm_image = imageio.imread(file_path)
        logger.info("Normal image loaded: %s", file_path)
        # TODO: Break into x and y components instead?

    def init_uv_image(self, file_path):
        # 16-bit colour-depth, use imageio.
        uv_image = imageio.imread(file_path)
        # Original image will be mapped to non-linear colourspace. Correct the uv coordinates by adjusting this.
        uv_image = exposure.adjust_gamma(uv_image, 2.2)

        # u coordinates are encoded in red channel.
        self.u_image = uv_image[:, :, 0]
        # v coordinates are encoded in green channel.
        self.v_image = uv_image[:, :, 1]

        logger.info("UV image loaded.: %s", file_path)

    def at_point(self, x, y):
        assert x >= 0
        assert y >= 0

        surface_data = self.SurfaceData(obj=self.obj_image[y, x],
                                        z=self.z_image[y, x],
                                        diffdir=self.diffdir_image[y, x],
                                        norm_x="",
                                        norm_y="",
                                        u=self.u_image[y, x],
                                        v=self.v_image[y, x])
        # logger.debug("Surface data at point (%d, %d): %s", x, y, surface_data)

        return surface_data


if __name__ == "__main__":
    pass

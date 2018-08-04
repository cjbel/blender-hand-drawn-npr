from collections import namedtuple
from skimage import io, exposure
import imageio


class Surface:

    def __init__(self):
        self.obj_image = None
        self.z_image = None
        self.diffdir_image = None
        self.norm_image = None
        self.u_image = None
        self.v_image = None

        self.SurfaceData = namedtuple("SurfaceData", "obj z norm_x norm_y u v")

    def init_obj_image(self, file_path):
        self.obj_image = io.imread(file_path, as_gray=True)

    def init_z_image(self, file_path):
        self.z_image = io.imread(file_path, as_gray=True)

    def init_diffdir_image(self, file_path):
        self.diffdir_image = io.imread(file_path, as_gray=True)

    def init_norm_image(self, file_path):
        # 16-bit colour-depth, use imageio.
        self.norm_image = imageio.imread(file_path)
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

    def at_point(self, x, y):
        return self.SurfaceData(obj=self.obj_image[y, x],
                                z=self.z_image[y, x],
                                norm_x="",
                                norm_y="",
                                u=self.u_image[y, x],
                                v=self.v_image[y, x])


if __name__ == "__main__":

    surface = Surface()
    surface.init_obj_image("/tmp/undulating_plane/IndexOB0001.png")
    surface.init_z_image("/tmp/undulating_plane/Depth0001.png")
    surface.init_uv_image("/tmp/undulating_plane/UV0001.tif")
    data = surface.at_point(689, 539)
    print(data)

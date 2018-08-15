import unittest
import logging

import numpy as np
from skimage import draw, measure

from blender_hand_drawn_npr.models import Surface
from blender_hand_drawn_npr.primitives import Path, ThicknessParameters

logger = logging.getLogger(__name__)

class TestPath(unittest.TestCase):

    def setUp(self):
        # Describe a square, centered on an image.
        rr, cc = draw.rectangle((2, 2), (7, 7))
        fake_image = np.zeros((10, 10))
        fake_image[rr, cc] = 1

        # Base the surface model on this square.
        self.surface = Surface(obj_image=fake_image,
                               z_image=fake_image,
                               diffdir_image=fake_image,
                               norm_x_image=fake_image,
                               norm_y_image=fake_image,
                               norm_z_image=fake_image,
                               u_image=fake_image,
                               v_image=fake_image)

        # Describe a path which follows the external outline of the square.
        self.boundary_path = Path([[1, 1], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1], [7, 1], [8, 1],
                                   [8, 2], [8, 3], [8, 4], [8, 5], [8, 6], [8, 7], [8, 8],
                                   [7, 8], [6, 8], [5, 8], [4, 8], [3, 8], [2, 8], [1, 8],
                                   [1, 7], [1, 6], [1, 5], [1, 4], [1, 3], [1, 2]])

        # Describe a path which follows the internal outline of the square.
        self.edge_path = Path([[2, 2], [3, 2], [4, 2], [5, 2], [6, 2], [7, 2],
                               [7, 3], [7, 4], [7, 5], [7, 6], [7, 7],
                               [6, 7], [5, 7], [4, 7], [3, 7], [2, 7],
                               [2, 6], [2, 5], [2, 4], [2, 3]])

    def test_round(self):
        path = Path([[0, 0],
                     [0.1, 0.8],
                     [10.8, 10.1]])
        rounded = path.round()

        self.assertEqual(((0, 0),
                          (0, 1),
                          (11, 10)), rounded.points)

    def test_nearest_neighbour(self):
        self.assertEqual((2, 2), self.edge_path.nearest_neighbour([0, 0]))
        self.assertEqual((7, 2), self.edge_path.nearest_neighbour([9, 0]))
        self.assertEqual((7, 7), self.edge_path.nearest_neighbour([9, 9]))
        self.assertEqual((2, 7), self.edge_path.nearest_neighbour([0, 9]))

    def test_find_corners(self):
        corners = self.edge_path.find_corners(self.surface.obj_image,
                                              min_distance=1,
                                              window_size=1)

        self.assertTrue((2, 2) in corners)
        self.assertTrue((2, 7) in corners)
        self.assertTrue((7, 7) in corners)
        self.assertTrue((7, 2) in corners)

    def test_split_corners(self):
        corners = ((2, 2), (2, 7), (7, 7), (7, 2))

        paths = self.edge_path.split_corners(corners)
        points = [path.points for path in paths]

        self.assertEqual(4, len(paths))
        self.assertTrue(((2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2)) in points)
        self.assertTrue(((7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)) in points)
        self.assertTrue(((7, 7), (6, 7), (5, 7), (4, 7), (3, 7), (2, 7)) in points)
        self.assertTrue(((2, 7), (2, 6), (2, 5), (2, 4), (2, 3)) in points)

    def test_bump(self):
        bumped = self.boundary_path.bump(self.surface)

        self.assertEqual(((2, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (7, 2), (7, 2), (7, 3),
                          (7, 4), (7, 5), (7, 6), (7, 7), (7, 7), (7, 7), (6, 7), (5, 7), (4, 7), (3, 7),
                          (2, 7), (2, 7), (2, 7), (2, 6), (2, 5), (2, 4), (2, 3), (2, 2)),
                         bumped.points)

    def test_trim_uv(self):
        # Create a fake UV map, gradient image with a black border and a rouge pixel on the isoline, which will force
        # a path split.
        x = np.linspace(0, 1, 10)
        image = np.tile(x, (10, 1))
        boundary = draw.polygon_perimeter((0, 0, 9, 9), (0, 9, 9, 0))
        image[boundary] = 0
        image[4, 4] = 0.55

        contours = measure.find_contours(image, 0.444)
        uv_path = Path(contours[0].tolist(), is_rc=True).round()

        trimmed_paths = uv_path.trim_uv(image=image, target_intensity=0.4, allowable_deviance=0.1)

        # Expected results are two paths as follows.
        self.assertEqual(((4, 8), (4, 8), (4, 7), (4, 6), (4, 5)), trimmed_paths[0].points)
        self.assertEqual(((4, 3), (4, 2), (4, 1), (4, 1)), trimmed_paths[1].points)

    def test_simple_cull(self):
        path = Path(((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)))

        self.assertEqual(((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)), path.simple_cull(1).points)
        self.assertEqual(((0, 0), (2, 0), (4, 0), (7, 0)), path.simple_cull(2).points)
        self.assertEqual(((0, 0), (3, 0), (7, 0)), path.simple_cull(3).points)
        self.assertEqual(((0, 0), (7, 0)), path.simple_cull(4).points)

    def test_compute_thicknesses(self):

        self.edge_path._curvatures = tuple([0.5]) * 20

        self.edge_path.compute_thicknesses(surface=self.surface,
                                           thickness_parameters=ThicknessParameters(const=1,
                                                                                    z=0,
                                                                                    diffdir=0,
                                                                                    curvature=0))
        self.assertEqual(tuple([1]) * 20, self.edge_path.thicknesses)

        self.edge_path.compute_thicknesses(surface=self.surface,
                                           thickness_parameters=ThicknessParameters(const=0,
                                                                                    z=1,
                                                                                    diffdir=0,
                                                                                    curvature=0))
        self.assertEqual(tuple([0]) * 20, self.edge_path.thicknesses)

        self.edge_path.compute_thicknesses(surface=self.surface,
                                           thickness_parameters=ThicknessParameters(const=0,
                                                                                    z=0,
                                                                                    diffdir=1,
                                                                                    curvature=0))
        self.assertEqual(tuple([0]) * 20, self.edge_path.thicknesses)

        self.edge_path.compute_thicknesses(surface=self.surface,
                                           thickness_parameters=ThicknessParameters(const=0,
                                                                                    z=0,
                                                                                    diffdir=0,
                                                                                    curvature=1))
        self.assertEqual(tuple([0.5]) * 20, self.edge_path.thicknesses)

        self.edge_path.compute_thicknesses(surface=self.surface,
                                           thickness_parameters=ThicknessParameters(const=1,
                                                                                    z=1,
                                                                                    diffdir=1,
                                                                                    curvature=1))
        self.assertEqual(tuple([1.5]) * 20, self.edge_path.thicknesses)


class TestStroke(unittest.TestCase):
    pass


class TestSurface(unittest.TestCase):
    pass


class TestSilhouette(unittest.TestCase):
    pass


class TestIllustrator(unittest.TestCase):
    pass

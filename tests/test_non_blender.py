import unittest
import logging

import numpy as np
from skimage import draw, measure

from blender_hand_drawn_npr.model.data import Surface, ThicknessParameters
from blender_hand_drawn_npr.model.primitives import Path

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

        self.assertEqual(6, len(paths))
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

    def test_simple_cull(self):
        path = Path(((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)))

        self.assertEqual(((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)), path.simple_cull(1).points)
        self.assertEqual(((0, 0), (2, 0), (4, 0), (7, 0)), path.simple_cull(2).points)
        self.assertEqual(((0, 0), (3, 0), (7, 0)), path.simple_cull(3).points)
        self.assertEqual(((0, 0), (7, 0)), path.simple_cull(4).points)


class TestStroke(unittest.TestCase):
    pass


class TestSurface(unittest.TestCase):
    pass


class TestSilhouette(unittest.TestCase):
    pass


class TestIllustrator(unittest.TestCase):
    pass

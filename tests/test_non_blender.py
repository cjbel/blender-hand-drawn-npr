import unittest
import numpy as np
from skimage import draw

from blender_hand_drawn_npr.primitives import Path
from blender_hand_drawn_npr.models import Surface


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
                               norm_image=fake_image,
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
        path.round()

        self.assertEqual([[0, 0],
                          [0, 1],
                          [11, 10]], path.points)

    def test_nearest_neighbour(self):
        self.assertEqual([2, 2], self.edge_path.nearest_neighbour([0, 0]))
        self.assertEqual([7, 2], self.edge_path.nearest_neighbour([9, 0]))
        self.assertEqual([7, 7], self.edge_path.nearest_neighbour([9, 9]))
        self.assertEqual([2, 7], self.edge_path.nearest_neighbour([0, 9]))

    def test_find_corners(self):
        self.edge_path.find_corners(self.surface.obj_image,
                                    min_distance=1,
                                    window_size=1)

        self.assertTrue([2, 2] in self.edge_path.corners)
        self.assertTrue([2, 7] in self.edge_path.corners)
        self.assertTrue([7, 7] in self.edge_path.corners)
        self.assertTrue([7, 2] in self.edge_path.corners)

    def test_split_corners(self):
        self.edge_path.corners = [[2, 2], [2, 7], [7, 7], [7, 2]]

        paths = self.edge_path.split_corners()
        points = [path.points for path in paths]

        self.assertEqual(4, len(paths))
        self.assertTrue([[2, 2], [3, 2], [4, 2], [5, 2], [6, 2], [7, 2]] in points)
        self.assertTrue([[7, 2], [7, 3], [7, 4], [7, 5], [7, 6], [7, 7]] in points)
        self.assertTrue([[7, 7], [6, 7], [5, 7], [4, 7], [3, 7], [2, 7]] in points)
        self.assertTrue([[2, 7], [2, 6], [2, 5], [2, 4], [2, 3]] in points)

    def test_validate(self):
        self.boundary_path.bump(self.surface)


class TestStroke(unittest.TestCase):
    pass


class TestSurface(unittest.TestCase):
    pass


class TestSilhouette(unittest.TestCase):
    pass


class TestIllustrator(unittest.TestCase):
    pass

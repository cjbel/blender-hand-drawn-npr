from blender_hand_drawn_npr.point_utils import *
from blender_hand_drawn_npr.vector_utils import *
import unittest
import math


class TestPointUtils(unittest.TestCase):

    def test_create_point(self):
        """ Test that a Point is created as expected. """
        point = create_point(10, 20, 0.4, 0.8)

        # There should be four attributes.
        self.assertEqual(4, len(point))

        # Confirm that each attribute is correctly mapped.
        self.assertEqual(10, point.x)
        self.assertEqual(20, point.y)
        self.assertEqual(0.4, point.depth_intensity)
        self.assertEqual(0.8, point.diffdir_intensity)

    def test_horizontal_delta_1(self):
        """ Test value correctly computed in +x dir. """
        p0 = create_point(0, 0, 0, 0)
        p1 = create_point(10, 0, 0, 0)
        self.assertEqual(10, horizontal_delta(p0, p1))

    def test_horizontal_delta_2(self):
        """ Test value is correctly computed in -x dir. """
        p0 = create_point(10, 0, 0, 0)
        p1 = create_point(0, 0, 0, 0)
        self.assertEqual(-10, horizontal_delta(p0, p1))

    def test_horizontal_delta_3(self):
        """ Test value is correctly computed in +y dir. """
        p0 = create_point(0, 0, 0, 0)
        p1 = create_point(0, 10, 0, 0)
        self.assertEqual(0, horizontal_delta(p0, p1))

    def test_horizontal_delta_4(self):
        """ Test value is correctly computed in -y dir. """
        p0 = create_point(0, 0, 0, 0)
        p1 = create_point(0, -10, 0, 0)
        self.assertEqual(0, horizontal_delta(p0, p1))

    def test_vertical_delta_1(self):
        """ Test value correctly computed in +x dir. """
        p0 = create_point(0, 0, 0, 0)
        p1 = create_point(10, 0, 0, 0)
        self.assertEqual(0, vertical_delta(p0, p1))

    def test_vertical_delta_2(self):
        """ Test value is correctly computed in -x dir. """
        p0 = create_point(10, 0, 0, 0)
        p1 = create_point(0, 0, 0, 0)
        self.assertEqual(0, vertical_delta(p0, p1))

    def test_vertical_delta_3(self):
        """ Test value is correctly computed in +y dir. """
        p0 = create_point(0, 0, 0, 0)
        p1 = create_point(0, 10, 0, 0)
        self.assertEqual(10, vertical_delta(p0, p1))

    def test_vertical_delta_4(self):
        """ Test value is correctly computed in -y dir. """
        p0 = create_point(0, 0, 0, 0)
        p1 = create_point(0, -10, 0, 0)
        self.assertEqual(-10, vertical_delta(p0, p1))

    def test_euclidean_dist_1(self):
        """ Test value correctly computed in +x dir, +y dir. """
        p0 = create_point(0, 0, 0, 0)
        p1 = create_point(1, 1, 0, 0)
        self.assertAlmostEqual(math.sqrt(2), euclidean_dist(p0, p1))

    def test_euclidean_dist_2(self):
        """ Test value correctly computed in -x dir, -y dir. """
        p0 = create_point(1, 1, 0, 0)
        p1 = create_point(0, 0, 0, 0)
        self.assertAlmostEqual(math.sqrt(2), euclidean_dist(p0, p1))

    def test_heading_1(self):
        """ Test value correctly computed in +x dir, +y dir. """
        p0 = create_point(0, 0, 0, 0)
        p1 = create_point(10, 10, 0, 0)
        self.assertEqual(45, heading(p0, p1))

    def test_heading_2(self):
        """ Test value correctly computed in -x dir, -y dir. """
        p0 = create_point(10, 10, 0, 0)
        p1 = create_point(0, 0, 0, 0)
        self.assertEqual(-135, heading(p0, p1))

    def test_heading_3(self):
        """ Test value correctly computed in +x dir. """
        p0 = create_point(0, 0, 0, 0)
        p1 = create_point(10, 0, 0, 0)
        self.assertEqual(0, heading(p0, p1))

    def test_heading_4(self):
        """ Test value correctly computed in -x dir. """
        p0 = create_point(10, 0, 0, 0)
        p1 = create_point(0, 0, 0, 0)
        self.assertEqual(180, heading(p0, p1))

    def test_heading_5(self):
        """ Test value correctly computed in +y dir. """
        p0 = create_point(0, 0, 0, 0)
        p1 = create_point(0, 10, 0, 0)
        self.assertEqual(90, heading(p0, p1))

    def test_heading_6(self):
        """ Test value correctly computed in -y dir. """
        p0 = create_point(0, 10, 0, 0)
        p1 = create_point(0, 0, 0, 0)
        self.assertEqual(-90, heading(p0, p1))

    def test_thickness_depth(self):
        p = create_point(0, 0, 0.2, 0)
        self.assertAlmostEqual(8, thickness_depth(p, 10))

    def test_thickness_diffdir(self):
        p = create_point(0, 0, 0, 0.2)
        self.assertAlmostEqual(8, thickness_diffdir(p, 10))


class TestVectorUtils(unittest.TestCase):

    def test_rotate_about_xy_1(self):
        vertices = [[1, 0]]
        rotated_vertices = np.round(rotate_about_xy(vertices, 1, 1, 90))
        self.assertSequenceEqual([[2, 1]], rotated_vertices.tolist())

    def test_rotate_about_xy_2(self):
        vertices = [[1, 0]]
        rotated_vertices = np.round(rotate_about_xy(vertices, 1, 1, 180))
        self.assertSequenceEqual([[1, 2]], rotated_vertices.tolist())

    def test_rotate_about_xy_3(self):
        vertices = [[1, 0]]
        rotated_vertices = np.round(rotate_about_xy(vertices, 1, 1, 270))
        self.assertSequenceEqual([[0, 1]], rotated_vertices.tolist())

    def test_rotate_about_xy_4(self):
        vertices = [[1, 0]]
        rotated_vertices = np.round(rotate_about_xy(vertices, 1, 1, 0))
        self.assertSequenceEqual([[1, 0]], rotated_vertices.tolist())

    def test_rotate_about_xy_5(self):
        vertices = [[-1, -1]]
        rotated_vertices = np.round(rotate_about_xy(vertices, -2, -2, 90))
        self.assertSequenceEqual([[-3, -1]], rotated_vertices.tolist())

    def test_translate_1(self):
        vertices = [[1, 1]]
        translated_vertices = translate(vertices, 2, 2)
        self.assertSequenceEqual([[3, 3]], translated_vertices.tolist())

    def test_translate_2(self):
        vertices = [[1, 1]]
        translated_vertices = translate(vertices, -2, -2)
        self.assertSequenceEqual([[-1, -1]], translated_vertices.tolist())

"""
Streamlines is a collection of Paths which capture the (u or v) directional streamlines of the render subject.
"""

import logging

from skimage import measure

from blender_hand_drawn_npr.point import Point
from blender_hand_drawn_npr.path import Path
from blender_hand_drawn_npr.stroke import Stroke

logger = logging.getLogger(__name__)


class Streamlines:

    def __init__(self, surface, n):
        self.paths = []
        self.surface = surface
        self.n = n
        self.__u_separation = None
        self.__v_separation = None
        self.__u_intensities = []
        self.__v_intensities = []
        self.candidate_construction_curves = []
        self.svg_candidates = []

    def __compute_separation(self):

        u_image, v_image = self.surface.u_image, self.surface.v_image

        self.__u_separation, self.__v_separation = (u_image.max() - u_image.min()) / self.n, \
                                                   (v_image.max() - v_image.min()) / self.n

        logger.debug("Separation (u, v): %s, %s", self.__u_separation, self.__v_separation)

    def __compute_intensities(self):
        """
        Compute the intensities representing each streamline location.
        :return:
        """
        for streamline_pos in range(1, self.n):
            self.__u_intensities.append(streamline_pos * self.__u_separation)

        for streamline_pos in range(1, self.n):
            self.__v_intensities.append(streamline_pos * self.__v_separation)

        logger.debug("Intensities (u): %s", self.__u_intensities)
        logger.debug("Intensities (v): %s", self.__v_intensities)

    def __generate_candidate_construction_curves(self, image, intensities):

        for intensity in intensities:
            pass
            # contours = measure.find_contours(image, intensity)
            # logger.debug("Contours found: %d", len(contours))
            #
            # for contour in contours:
            #     # Sometimes a contour of small length (~5-10 is found, consider a check here to reject them.
            #     # if len(contour) < 10:
            #     #     logger.debug("Contour of length %s rejected.", len(contour))
            #     #     break
            #
            #     # Create the Path.
            #     path = Path([Point(coord[1], coord[0]) for coord in contour])

    def generate(self):
        """
        Make all such classes which produce paths implement this method to allow for polymorphic calls?
        :return: A collection of Paths which capture the (u or v) directional streamlines of the render subject.
        """

        self.__compute_separation()
        self.__compute_intensities()
        self.__generate_candidate_construction_curves(self.surface.u_image, self.__u_intensities)

        # u_grid_width, v_grid_width = (u_image.max() - u_image.min()) / u_slices, \
        #                              (v_image.max() - v_image.min()) / v_slices
        #
        # # Identify u and v intensity values representing each slice boundary.
        # u_intensities = []
        # for streamline_pos in range(1, u_slices):
        #     u_intensities.append(streamline_pos * u_grid_width)
        #
        # v_intensities = []
        # for streamline_pos in range(1, v_slices):
        #     v_intensities.append(streamline_pos * v_grid_width)

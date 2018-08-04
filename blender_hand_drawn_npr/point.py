class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_rc(self):
        """
        :return: the coordinate value in format (row, column).
        """
        return (self.y, self.x)

    def validate_subject_point(self):
        """
        Validate that the point lies on the surface/edge of the subject.
        :return:
        """


if __name__ == "__main__":
    point = Point(10, 20)
    print(point.to_rc())

import unittest

import geometry
from design_interface import DesignInterface
from geometry import Point, Line, Lattice


class FakeInterface(DesignInterface):
    def create_geometry(self, lattice: Lattice, extrusion_height: float):
        pass

    def __init__(self):
        self.lines_added = []
        self.points_added = []

    def add_line(self, line: Line):
        pass

    def add_point(self, point: Point):
        pass


class AbstractInterfaceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.interface = FakeInterface()

        self.test_lattice_2_inlet = geometry.create_lattice(
            (2, 1, 2, 3, 2, 1, 2, 3, 2, 1, 1), 5, 0.5
        )

        self.test_lattice_3_inlet = geometry.create_lattice(
            (3, 1, 1, 2, 3, 2, 1, 2, 3, 2, 1, 1), 5, 0.5
        )
        self.test_lattices = (
            self.test_lattice_2_inlet,
            self.test_lattice_3_inlet,
        )

    def test_named_faces(self):
        expected_faces = (3, 4)
        expected_names = (
            ("aqueous_inlet_1", "organic_inlet", "outlet"),
            ("aqueous_inlet_1", "organic_inlet", "aqueous_inlet_2", "outlet"),
        )
        for expected, expected_name, lattice in zip(
            expected_faces, expected_names, self.test_lattices
        ):
            named_faces = self.interface.named_faces(lattice)
            self.assertEqual(expected, len(named_faces))
            self.assertEqual(expected_name, tuple(f.name for f in named_faces))

    def test_exclude_points(self):
        expected_point_lens = (6, 8)
        for expected_point_len, lattice in zip(
            expected_point_lens, self.test_lattices
        ):
            self.assertEqual(
                expected_point_len,
                len(tuple(self.interface.exclude_points(lattice))),
            )

    def test_can_filter_on_generator(self):
        def gen():
            for i in range(0, 11, 2):
                yield i

        def add_1(num: int):
            return num + 1

        nums = (i for i in range(0, 10))

        res = tuple(
            i for i in filter(lambda x: x not in gen(), map(add_1, nums))
        )
        self.assertEqual((1, 3, 5, 7, 9), res)

import unittest
import geometry
import matplotlib
import matplotlib.pyplot as plt


class MatplotlibInterface(geometry.DesignInterface):
    def __init__(self):
        matplotlib.rcParams["figure.dpi"] = 600
        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect("equal")

    def add_point(self, point: geometry.Point):
        self.ax.scatter(point.x, point.y, c="blue")

    def add_line(
        self,
        line: geometry.Line,
    ):
        fmt = "b-"
        self.ax.plot(geometry.xs(line), geometry.ys(line), fmt)

    @staticmethod
    def show():
        plt.show()


class DataStructuresTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.interface = MatplotlibInterface()

    def assert_array_equal(self, expected, array: geometry.array):
        for e, a in zip(expected, array):
            self.assertEqual(e, a)

    def test_point_array(self):
        point = geometry.Point(5, 5)
        self.assert_array_equal((5, 5), geometry.point_array(point))

    def test_line_length(self):
        point_1 = geometry.Point(0, 0)
        point_2 = geometry.Point(5, 0)
        line = geometry.Line(point_2, point_1)
        self.assertEqual(5, geometry.line_length(line))

    @staticmethod
    def unit_circle_coords():
        return (
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
            (0, -1),
            (1, -1),
        )

    def test_line_direction(self):
        origin = geometry.Point(0, 0)
        coords = self.unit_circle_coords()
        expected_directions = (
            0,
            geometry.pi / 4,
            geometry.pi / 2,
            3 * geometry.pi / 4,
            geometry.pi,
            -3 * geometry.pi / 4,
            -geometry.pi / 2,
            -geometry.pi / 4,
        )
        for expected, point in zip(expected_directions, coords):
            pt = geometry.Point(*point)
            line = geometry.Line(origin, pt)
            self.assertEqual(
                round(expected, 5), round(geometry.line_direction(line), 5)
            )

    def test_line_degrees(self):
        origin = geometry.Point(0, 0)
        coords = self.unit_circle_coords()
        expected_directions = (
            0,
            45,
            90,
            135,
            180,
            225,
            270,
            315,
        )
        for expected, point in zip(expected_directions, coords):
            pt = geometry.Point(*point)
            line = geometry.Line(origin, pt)
            self.assertEqual(
                round(expected, 5), round(geometry.line_degrees(line), 5)
            )

    def test_connect_layers(self):
        layer_1 = geometry.create_layer(2, 0, 5)
        layer_2 = geometry.create_layer(3, 2.5, 5)
        connection = geometry.connect_layers(layer_2, layer_1)
        self.assertEqual(2, len(connection.layers))
        self.assertEqual(4, len(connection.lines))
        self.assertEqual(0, connection.layers[0][0].y)
        self.assertEqual(0, connection.lines[0].start.y)

    @staticmethod
    def plot_channels(channels):
        interface = MatplotlibInterface()
        for channel in channels:
            interface.add_line(channel.center_line)
            for wall in channel.walls:
                interface.add_line(wall)
        interface.show()

    def test_join_channels(self):
        layer_1 = geometry.create_layer(2, 0, 5)
        layer_2 = geometry.create_layer(1, 2.5, 5)
        connection = geometry.connect_layers(layer_2, layer_1)
        channels = geometry.create_channel_layer(connection, 0.5)
        joined_channels = geometry.join_channels(*channels)
        self.plot_channels(joined_channels)

    def test_create_channel_layer(self):
        layer_1 = geometry.create_layer(2, 0, 5)
        layer_2 = geometry.create_layer(3, 2.5, 5)
        connection = geometry.connect_layers(layer_2, layer_1)
        self.plot_channels(geometry.create_channel_layer(connection, 0.5))

    def test_create_joined_channel_layer(self):
        layer_1 = geometry.create_layer(5, 0, 5)
        layer_2 = geometry.create_layer(6, 2.5, 5)
        connection = geometry.connect_layers(layer_2, layer_1)
        channels = geometry.create_joined_channel_layer(connection, 0.5)
        self.plot_channels(channels)

    def test_flatten_channel_layer(self):
        layer_1 = geometry.create_layer(5, 0, 5)
        layer_2 = geometry.create_layer(6, 2.5, 5)
        connection = geometry.connect_layers(layer_2, layer_1)
        channels = geometry.create_joined_channel_layer(connection, 0.5)
        flattened_channels = geometry.flatten_channel_layer(channels, "end")
        self.plot_channels(flattened_channels)

    def test_create_lattice(self):
        lattice = geometry.create_lattice(
            (2, 1, 2, 3, 2, 1, 2, 3, 2, 1, 1), 5, 0.5
        )
        print(geometry.lattice_point_set(lattice))
        for line in geometry.lattice_line_gen(lattice):
            self.interface.add_line(line)
        self.interface.show()

    def test_extrude_lattice(self):

    def test_point_set(self):
        lattice = geometry.create_lattice(
            (2, 1, 2, 3, 2, 1, 2, 3, 2, 1, 1), 5, 0.5
        )
        print(geometry.lattice_point_set(lattice))


if __name__ == '__main__':
    unittest.main()

from abc import ABC, abstractmethod
from typing import Tuple, Iterable
from random import randint
from math import atan2, pi, cos, sin, sqrt
from numpy import dot, array


class Point:
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = round(x, 5)
        self.y = round(y, 5)

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self):
        return f'({self.x}, {self.y})'


def point_array(point: Point) -> array:
    return array((point.x, point.y))


class Line:
    start: Point
    end: Point

    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end

    def __iter__(self):
        yield self.start
        yield self.end

    def __eq__(self, other):
        return other.start == self.start and other.end == self.end


def xs(line):
    return tuple(map(lambda l: l.x, line))


def ys(line):
    return tuple(map(lambda l: l.y, line))


def d(variable: str, line: Line):
    return getattr(line.end, variable) - getattr(line.start, variable)


def dx(line: Line):
    return d("x", line)


def dy(line: Line):
    return d("y", line)


def line_length(line: Line):
    return sqrt(pow(dx(line), 2) + pow(dy(line), 2))


def line_direction(line: Line):
    return atan2(dy(line), dx(line))


def line_degrees(line: Line):
    direction = line_direction(line)
    if direction < 0:
        direction = direction + 2 * pi
    return direction * 180 / pi


def vector(line: Line):
    return dx(line), dy(line)


def line_arrays(line: Line):
    return tuple(point_array(p) for p in line)


def perp(a: array):
    return array((-a[1], a[0]))


def intersection(line_1: Line, line_2: Line) -> Point:
    a1, a2 = line_arrays(line_1)
    b1, b2 = line_arrays(line_2)
    da = a2 - a1
    db = b2 - b1
    dp = a1 - b1
    dap = perp(da)
    denom = dot(dap, db)
    num = dot(dap, dp)
    return Point(*((num / denom) * db + b1))


class Layer:
    points: Tuple[Point, ...]

    def __init__(self, points: Tuple[Point, ...]):
        self.points = points

    def __len__(self):
        return len(self.points)

    def __iter__(self) -> Iterable[Point]:
        yield from self.points

    def __getitem__(self, item) -> Point:
        return self.points[item]


class ConnectedLayers:
    layers: Tuple[Layer, ...]
    lines: Tuple[Line, ...]

    def __init__(self, layers: Tuple[Layer, ...], lines: Tuple[Line, ...]):
        self.layers = layers
        self.lines = lines


class DesignInterface(ABC):
    @abstractmethod
    def add_point(self, point: Point):
        raise NotImplementedError

    def add_line(
        self,
        line: Line,
    ):
        raise NotImplementedError


def create_layer(n_points, y_level, spacing) -> Layer:
    leftmost = (n_points - 1) * spacing / 2

    def gen() -> Iterable[Point]:
        for i in range(0, n_points):
            x = -leftmost + i * spacing
            yield Point(x, y_level)

    return Layer(tuple(gen()))


def connect_layers(
    layer_1: Layer,
    layer_2: Layer,
) -> ConnectedLayers:
    sorted_layers = sorted((layer_1, layer_2), key=lambda x: len(x))
    diff = abs(len(layer_1) - len(layer_2))

    def line_gen():
        for i in range(len(sorted_layers[0])):
            for j in range(diff + 1):
                point_1 = sorted_layers[0][i]
                point_2 = sorted_layers[1][i + j]
                yield Line(*sorted((point_1, point_2), key=lambda p: p.y))

    return ConnectedLayers(
        layers=tuple(
            sorted((layer_1, layer_2), key=lambda p: next(p.__iter__()).y)
        ),
        lines=tuple(line_gen()),
    )


def offset_point(point: Point, direction: float, offset: float):
    return Point(
        (cos(direction) * offset) + point.x,
        (sin(direction) * offset) + point.y,
    )


def offset_line(line: Line, offset: float, backwards=False) -> Line:
    direction = line_direction(line)
    if backwards:
        offset = offset * -1
    if direction >= 0:
        normal = direction + pi / 2
    else:
        normal = direction - pi / 2

    return Line(
        offset_point(line.start, normal, offset),
        offset_point(line.end, normal, offset),
    )


class Channel:
    walls: Tuple[Line, ...]
    center_line: Line

    def __init__(self, walls: Tuple[Line, ...], center_line: Line):
        self.walls = walls
        self.center_line = center_line

    @property
    def bottom_wall(self):
        return Line(self.walls[0].start, self.walls[1].start)

    @property
    def top_wall(self):
        return Line(self.walls[0].end, self.walls[1].end)

    def __iter__(self):
        yield from self.walls
        yield self.top_wall
        yield self.bottom_wall


class ChannelLayer:
    node_layers: Tuple[Layer, ...]
    channels: Tuple[Channel, ...]

    def __init__(self, node_layers: Tuple[Layer, ...], channels: Tuple[Channel, ...]):
        self.node_layers = node_layers
        self.channels = channels

    def __iter__(self):
        yield from self.channels


class Lattice:
    channel_layers: Tuple[ChannelLayer, ...]

    def __init__(self, channel_layers: Tuple[ChannelLayer, ...]):
        self.channel_layers = channel_layers

    def __iter__(self):
        yield from self.channel_layers


def lattice_channel_gen(lattice: Lattice):
    for channel_layer in lattice:
        yield from channel_layer


def lattice_line_gen(lattice: Lattice):
    for channel in lattice_channel_gen(lattice):
        yield from channel


def lattice_point_gen(lattice: Lattice):
    for wall in lattice_line_gen(lattice):
        yield from wall


def lattice_lines(lattice):
    return tuple(lattice_line_gen(lattice))


def lattice_point_set(lattice: Lattice):
    return set(lattice_point_gen(lattice))


def common_point(line_1: Line, line_2: Line) -> Point:
    for p1 in line_1:
        for p2 in line_2:
            if p1 == p2:
                return p1


def start_or_end(line: Line, point: Point) -> str:
    if point not in (line.start, line.end):
        raise Exception("Point is not on line!")
    elif line.start == point:
        return "start"
    else:
        return "end"


def alter_line(line: Line, new_point: Point, at: str):
    if at == "start":
        return Line(start=new_point, end=line.end)
    else:
        return Line(start=line.start, end=new_point)


def intersect_lines(line_1: Line, line_2: Line):
    intersect = intersection(line_1, line_2)
    join_at = tuple(start_or_end(line, intersect) for line in (line_1, line_2))
    return tuple(
        alter_line(line, intersect, at)
        for line, at in zip((line_1, line_2), join_at)
    )


def create_channel(line: Line, width: float):
    def _walls(_line: Line) -> Tuple[Line, ...]:
        def gen() -> Iterable[Line]:
            for backwards in True, False:
                yield offset_line(_line, width / 2, backwards=backwards)

        return tuple(sorted(gen(), key=lambda x: x.start.x))

    return Channel(walls=_walls(line), center_line=line)


def join_channels(
    channel_1: Channel, channel_2: Channel
) -> Tuple[Channel, ...]:
    common = common_point(channel_1.center_line, channel_2.center_line)
    join_at = tuple(
        start_or_end(c.center_line, common) for c in (channel_1, channel_2)
    )

    def sorted_walls(channel: Channel):
        return sorted(channel.walls, key=lambda w: (w.start.y, w.start.x))

    def altered_wall_gen() -> Iterable[Channel]:
        join_walls = tuple(map(sorted_walls, (channel_1, channel_2)))
        intersections = tuple(map(intersection, *join_walls))
        altered_walls = tuple(
            tuple(map(alter_line, wall, intersections, join_at))
            for wall in join_walls
        )
        for _channel, walls in zip((channel_1, channel_2), altered_walls):
            yield Channel(walls=walls, center_line=_channel.center_line)

    return tuple(altered_wall_gen())


def cut_channel(channel: Channel, line: Line):
    common = next(filter(lambda c: c.y == line.start.y, channel.center_line))
    intersections = tuple(intersection(w, line) for w in channel.walls)
    join_at = start_or_end(channel.center_line, common)

    def alter_func(join: str):
        def ret_func(_line, new_point):
            return alter_line(_line, new_point, join)

        return ret_func

    new_walls = map(alter_func(join_at), channel.walls, intersections)
    return Channel(tuple(new_walls), channel.center_line)


def create_channel_layer(
    connected_layers: ConnectedLayers, channel_width: float
) -> ChannelLayer:
    def channels():
        lines = sorted(
            connected_layers.lines, key=lambda x: (x.start.x, x.end.x)
        )
        for line in lines:
            yield create_channel(line, channel_width)

    return ChannelLayer(
        node_layers=connected_layers.layers, channels=tuple(channels())
    )


def create_joined_channel_layer(
    connected_layers: ConnectedLayers, channel_width: float
) -> ChannelLayer:
    base_layer = create_channel_layer(connected_layers, channel_width)

    def new_channels():
        channel_list = list(base_layer.channels)
        for i in range(len(channel_list) - 1):
            joined = join_channels(channel_list[i], channel_list[i + 1])
            channel_list[i] = joined[0]
            channel_list[i + 1] = joined[1]
        return channel_list

    return ChannelLayer(
        node_layers=connected_layers.layers, channels=tuple(new_channels())
    )


def flatten_channel_layer(channel_layer: ChannelLayer, start_end: str):
    sorted_layers = sorted(channel_layer.node_layers, key=lambda x: x[0].y)
    flat_line = sorted_layers[0] if start_end == "start" else sorted_layers[1]
    if len(flat_line) > 1:
        line_to_intersect = Line(flat_line[0], flat_line[-1])
    else:
        line_to_intersect = Line(
            Point(-100, flat_line[0].y), Point(100, flat_line[0].y)
        )
    new_channels = tuple(
        cut_channel(c, line_to_intersect) for c in channel_layer
    )
    return ChannelLayer(
        node_layers=channel_layer.node_layers,
        channels=new_channels,
    )


def common_layer(channel_layer_1: ChannelLayer, channel_layer_2: ChannelLayer):
    for layer_1 in channel_layer_1.node_layers:
        for layer_2 in channel_layer_2.node_layers:
            if layer_1 == layer_2:
                return layer_1


def channels_through_point(point: Point, channels: Tuple[Channel, ...]):
    for c in channels:
        if point in c.center_line:
            yield c


def channels_in_same_layer(
    channels: Tuple[Channel, ...], layers: Tuple[ChannelLayer, ...]
):
    ret = False
    for layer in layers:
        if all(c in layer.channels for c in channels):
            ret = True
            break
    return ret


def get_wall(channel: Channel, wall: str) -> Line:
    if wall == "right":
        return next(
            filter(
                lambda x: x.start.x >= channel.center_line.start.x
                and x.end.x >= channel.center_line.end.x,
                channel.walls,
            )
        )
    else:
        return next(
            filter(
                lambda x: x.start.x <= channel.center_line.start.x
                and x.end.x <= channel.center_line.end.x,
                channel.walls,
            )
        )


def replace_wall(
    channel: Channel, new_wall: Line, new_wall_index: int
) -> Channel:
    keep_index = 1 if new_wall_index == 0 else 0
    return Channel(
        walls=(channel.walls[keep_index], new_wall),
        center_line=channel.center_line,
    )


def create_lattice(
    layer_points: tuple,
    point_spacing: float,
    channel_width: float,
) -> Lattice:
    def layer_gen():
        for i, points in enumerate(layer_points):
            yield create_layer(
                points,
                point_spacing * i / 2,
                point_spacing,
            )

    layers = tuple(layer_gen())

    def layer_pair_gen():
        for i in range(len(layers)):
            try:
                yield layers[i], layers[i + 1]
            except IndexError:
                pass

    def connected_layer_gen():
        for pair in layer_pair_gen():
            yield connect_layers(*pair)

    def joined_channel_layer_gen():
        for connection in connected_layer_gen():
            yield create_joined_channel_layer(connection, channel_width)

    def cut_channel_gen():
        channels = list(joined_channel_layer_gen())
        _gen = layer_gen()
        _ = next(layer_gen())
        for i in range(len(channels) - 2):
            channels[i] = flatten_channel_layer(channels[i], "end")
            channels[i + 1] = flatten_channel_layer(channels[i + 1], "start")
        return tuple(channels)

    return Lattice(channel_layers=cut_channel_gen())


def random_layer_sequence(n_layers, max_width, max_layer_difference):
    layers = [1, 1]
    prev_int = 1
    for _ in range(n_layers - 2):
        layers.insert(
            prev_int,
            layers[prev_int - 1]
            + randint(-max_layer_difference, max_layer_difference),
        )
        prev_int += 1

    def is_valid():
        for i in range(len(layers)):
            try:
                if (
                    abs(layers[i] - layers[i + 1]) > max_layer_difference
                    or layers[i] > max_width
                    or layers[i + 1] > max_width
                    or layers[i] <= 0
                    or layers[i + 1] <= 0
                ):
                    return False
            except IndexError:
                return True

    if not is_valid():
        return random_layer_sequence(n_layers, max_width, max_layer_difference)
    else:
        return tuple(layers)

from typing import List

from salome.geom import geomBuilder

from geometry import (
    DesignInterface,
    Line,
    Point,
    ExtrudedChannel,
    Lattice,
    lattice_channel_gen,
)


class SalomeVertex:
    obj: object
    point: Point

    def __init__(self, obj: object, point: Point):
        self.obj = obj
        self.point = point


class SalomeLine:
    obj: object
    line: Line

    def __init__(self, obj: object, line: Line):
        self.obj = obj
        self.line = line


class SalomeChannel:
    obj: object
    channel: ExtrudedChannel

    def __init__(self, obj: object, channel: Channel):
        self.obj = obj
        self.channel = channel


class SalomeFusedFaces:
    obj: object
    lattice: Lattice

    def __init__(self, obj: object, lattice: Lattice):
        self.obj = obj
        self.lattice = lattice


class SalomeInterface(DesignInterface):
    fuse: SalomeFusedFaces
    extrusion: object

    def __init__(self):
        self.builder = geomBuilder.New()
        self.vertices: List[SalomeVertex] = []
        self.lines: List[SalomeLine] = []
        self.faces: List[SalomeFace] = []

    def add_point(self, point: Point):
        vertex = self.builder.MakeVertex(point.x, point.y, point.z)
        self.vertices.append(SalomeVertex(vertex, point))
        return vertex

    def add_line(self, line: Line):
        vertexes = tuple(map(self.vertex_lookup, line))
        salome_line = self.builder.MakeLineTwoPnt(*vertexes)
        self.lines.append(SalomeLine(salome_line, line))
        return salome_line

    def add_channel_faces(self, channel: ExtrudedChannel):
        lines = list(map(self.line_lookup, channel))
        print(lines)
        print(len(lines))

        face = self.builder.MakeFaceWires(lines, 1)
        self.faces.append(SalomeFace(face, channel))
        return face

    def fuse_faces(self, lattice: Lattice):
        faces = list(map(self.channel_lookup, lattice_channel_gen(lattice)))
        fuse = self.builder.MakeFuseList(faces, True, True)
        self.fuse = SalomeFusedFaces(fuse, lattice)
        self.builder.addToStudy(fuse, f"fuse")

    def extrude(self, height: float):
        self.extrusion = self.builder.MakePrismDXDYDZ(
            self.fuse.obj, 0, 0, height
        )
        self.builder.addToStudy(self.extrusion, "extrusion")

    def vertex_lookup(self, point: Point) -> object:
        return next(filter(lambda x: x.point == point, self.vertices)).obj

    def line_lookup(self, line: Line) -> object:
        return next(filter(lambda x: x.line == line, self.lines)).obj

    def channel_lookup(self, channel: Channel) -> object:
        return next(filter(lambda x: x.channel == channel, self.faces)).obj

from dataclasses import dataclass
from typing import List

from GEOM_Gen_idl import GEOM_Object
from salome.geom import geomBuilder

from geometry import (
    DesignInterface,
    Line,
    Point,
    Channel,
    Lattice,
    lattice_channel_gen,
)


@dataclass(frozen=True)
class SalomeVertex:
    obj: GEOM_Object
    point: Point


@dataclass(frozen=True)
class SalomeLine:
    obj: GEOM_Object
    line: Line


@dataclass(frozen=True)
class SalomeFace:
    obj: GEOM_Object
    channel: Channel


@dataclass(frozen=True)
class SalomeFusedFaces:
    obj: GEOM_Object
    lattice: Lattice


class SalomeInterface(DesignInterface):
    fuse: SalomeFusedFaces
    extrusion: GEOM_Object

    def __init__(self):
        self.builder = geomBuilder.New()
        self.vertices: List[SalomeVertex] = []
        self.lines: List[SalomeLine] = []
        self.faces: List[SalomeFace] = []

    def add_point(self, point: Point, name: str):
        vertex = self.builder.MakeVertex(point.x, point.y, 0)
        self.vertices.append(SalomeVertex(vertex, point))
        self.builder.addToStudy(vertex, f"vertex_{len(self.vertices)}")
        return vertex

    def add_line(self, line: Line):
        vertexes = tuple(map(self.vertex_lookup, line))
        salome_line = self.builder.MakeLineTwoPnt(*vertexes)
        self.lines.append(SalomeLine(salome_line, line))
        self.builder.addToStudy(salome_line, f"vertex_{len(self.lines)}")
        return salome_line

    def add_face(self, channel: Channel):
        lines = list(map(self.line_lookup, channel))
        face = self.builder.MakeFaceWires(lines, 1)
        self.faces.append(SalomeFace(face, channel))
        self.builder.addToStudy(face, f"face_{len(self.faces)}")
        return face

    def fuse_faces(self, lattice: Lattice):
        faces = list(map(self.channel_lookup, lattice_channel_gen(lattice)))
        fuse = self.builder.MakeFuseList(faces, True, True)
        self.fuse = SalomeFusedFaces(fuse, lattice)
        self.builder.addToStudy(fuse, f"fuse")

    def extrude(self, height: float):
        self.extrusion = self.builder.MakePrismDXDYDZ(self.fuse, 0, 0, height)
        self.builder.addToStudy(self.extrusion, 'extrusion')

    def vertex_lookup(self, point: Point) -> GEOM_Object:
        return next(filter(lambda x: x.point == point, self.vertices)).obj

    def line_lookup(self, line: Line) -> GEOM_Object:
        return next(filter(lambda x: x.line == line, self.lines)).obj

    def channel_lookup(self, channel: Channel) -> GEOM_Object:
        return next(filter(lambda x: x.channel == channel, self.faces)).obj

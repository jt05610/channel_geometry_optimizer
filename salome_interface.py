from typing import List

import SMESH
from salome.geom import geomBuilder
from salome.smesh import smeshBuilder

from geometry import (
    DesignInterface,
    Line,
    Point,
    Channel,
    Lattice,
    lattice_channel_gen,
    lattice_point_set,
    lattice_line_gen,
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


class SalomeFace:
    obj: object
    channel: Channel

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
    lattice: Lattice
    filleted_fuse: object
    extrusion_height: float
    wall_group: object
    aqueous_group: object
    organic_group: object
    outlet_group: object
    extrusion: object

    def __init__(self):
        self.builder = geomBuilder.New()
        self.mesh_builder = smeshBuilder.New()
        self.vertices: List[SalomeVertex] = []
        self.lines: List[SalomeLine] = []
        self.faces: List[SalomeFace] = []
        self.mesh_parameters = None
        self.mesh = None

    def create_geometry(self, lattice: Lattice, extrusion_height: float):

        for point in lattice_point_set(lattice):
            self.add_point(point)

        for line in lattice_line_gen(lattice):
            self.add_line(line)

        for channel in lattice_channel_gen(lattice):
            self.add_face(channel)

        self.fuse_faces(lattice)
        self.fillet()
        self.extrude(extrusion_height)
        self.create_groups()

    def build_hypothesis(self):
        self.mesh_parameters = self.mesh_builder.CreateHypothesis(
            "NETGEN_Parameters", "NETGENEngine"
        )
        self.mesh_parameters.SetSecondOrder(0)
        self.mesh_parameters.SetOptimize(1)
        self.mesh_parameters.SetFineness(3)
        self.mesh_parameters.SetChordalError(-1)
        self.mesh_parameters.SetChordalErrorEnabled(0)
        self.mesh_parameters.SetUseSurfaceCurvature(1)
        self.mesh_parameters.SetFuseEdges(1)
        self.mesh_parameters.SetQuadAllowed(0)
        self.mesh_parameters.SetMaxSize(0.2)
        self.mesh_parameters.SetMinSize(0.1)
        self.mesh_parameters.SetCheckChartBoundary(176)

    def create_mesh(self):
        self.mesh = self.mesh_builder.Mesh(self.extrusion)
        netgen_1d_2d_3d = self.mesh_builder.CreateHypothesis(
            "NETGEN_2D3D", "NETGENEngine"
        )
        self.mesh.AddHypothesis(self.mesh_parameters)
        self.mesh.AddHypothesis(netgen_1d_2d_3d)
        walls = self.mesh.GroupOnGeom(self.wall_group, "walls", SMESH.FACE)
        organic = self.mesh.GroupOnGeom(
            self.organic_group, "organic_inlet", SMESH.FACE
        )
        aqueous = self.mesh.GroupOnGeom(
            self.aqueous_group, "aqueous_inlet", SMESH.FACE
        )
        outlet = self.mesh.GroupOnGeom(self.outlet_group, "outlet", SMESH.FACE)

        self.mesh.Compute()
        self.mesh_builder.SetName(walls, "walls")
        self.mesh_builder.SetName(organic, "organic_inlet")
        self.mesh_builder.SetName(aqueous, "aqueous_inlet")
        self.mesh_builder.SetName(outlet, "outlet")
        self.mesh_builder.SetName(self.mesh.GetMesh(), "outlet")

    def export_mesh(self, filename):
        self.mesh.ExportUNV(filename)

    def mesh_pipeline(self, save_name: str):
        self.build_hypothesis()
        self.create_mesh()
        self.export_mesh(save_name)

    def add_point(self, point: Point):
        vertex = self.builder.MakeVertex(point.x, point.y, 0)
        self.vertices.append(SalomeVertex(vertex, point))
        return vertex

    def add_line(self, line: Line):
        vertexes = tuple(map(self.vertex_lookup, line))
        salome_line = self.builder.MakeLineTwoPnt(*vertexes)
        self.lines.append(SalomeLine(salome_line, line))
        return salome_line

    def add_face(self, channel: Channel):
        lines = list(map(self.line_lookup, channel))
        face = self.builder.MakeFaceWires(lines, 1)
        self.faces.append(SalomeFace(face, channel))
        return face

    def fuse_faces(self, lattice: Lattice):
        faces = list(map(self.channel_lookup, lattice_channel_gen(lattice)))
        fuse = self.builder.MakeFuseList(faces, True, True)
        self.fuse = SalomeFusedFaces(fuse, lattice)
        self.lattice = lattice
        self.builder.addToStudy(fuse, "fuse")

    def extrude(self, height: float):
        self.extrusion = self.builder.MakePrismDXDYDZ(
            self.fillet, 0, 0, height
        )
        self.extrusion_height = height
        self.builder.addToStudy(self.extrusion, "extrusion")

    def vertex_lookup(self, point: Point) -> object:
        return next(filter(lambda x: x.point == point, self.vertices)).obj

    def line_lookup(self, line: Line) -> object:
        return next(filter(lambda x: x.line == line, self.lines)).obj

    def channel_lookup(self, channel: Channel) -> object:
        return next(filter(lambda x: x.channel == channel, self.faces)).obj

    def make_vertex(self, point: Point, height: float = 0):
        return self.builder.MakeVertex(point.x, point.y, height)

    def vertex_func(self, point: Point):
        return self.make_vertex(point, self.extrusion_height)

    @property
    def aqueous_face(self):
        channel = self.lattice.channel_layers[0].channels[0]
        points = tuple(map(self.make_vertex, channel.bottom_wall))
        points += tuple(map(self.vertex_func, channel.bottom_wall))
        return self.builder.GetFaceByPoints(self.extrusion, *points)

    @property
    def organic_face(self):
        channel = self.lattice.channel_layers[0].channels[1]
        points = tuple(map(self.make_vertex, channel.bottom_wall))
        points += tuple(map(self.vertex_func, channel.bottom_wall))
        return self.builder.GetFaceByPoints(self.extrusion, *points)

    @property
    def outlet_face(self):
        channel = self.lattice.channel_layers[-1].channels[0]
        points = tuple(map(self.make_vertex, channel.top_wall))
        points += tuple(map(self.vertex_func, channel.top_wall))
        return self.builder.GetFaceByPoints(self.extrusion, *points)

    def face_id(self, face: object):
        return self.builder.GetSubShapeID(self.extrusion, face)

    def vertex_id(self, face: object):
        return self.builder.GetSubShapeID(self.fuse.obj, face)

    def get_vertex_near_point(self, vertex):
        return self.builder.GetVertexNearPoint(self.fuse.obj, vertex)

    def fillet(self):
        sub_vertices = self.builder.SubShapeAllSortedCentres(
            self.fuse.obj, self.builder.ShapeType["VERTEX"]
        )
        vertices_to_fillet = []
        aqueous_vertices = tuple(
            map(
                self.get_vertex_near_point,
                map(
                    self.make_vertex,
                    self.lattice.channel_layers[0].channels[0].bottom_wall,
                ),
            )
        )
        organic_vertices = tuple(
            map(
                self.get_vertex_near_point,
                map(
                    self.make_vertex,
                    self.lattice.channel_layers[0].channels[1].bottom_wall,
                ),
            )
        )
        outlet_vertices = tuple(
            map(
                self.get_vertex_near_point,
                map(
                    self.make_vertex,
                    self.lattice.channel_layers[-1].channels[0].top_wall,
                ),
            )
        )
        for vertex in sub_vertices:
            vertices_to_fillet.append(self.vertex_id(vertex))
        for vertex_pair in (
            aqueous_vertices,
            organic_vertices,
            outlet_vertices,
        ):
            for vertex in vertex_pair:
                vertices_to_fillet.remove(self.vertex_id(vertex))
        self.filleted_fuse = self.builder.MakeFillet2D(
            self.fuse.obj, 0.1, vertices_to_fillet
        )
        self.builder.addToStudy(self.fillet, "fillet")

    def create_wall_group(self):
        self.wall_group = self.builder.CreateGroup(
            self.extrusion, self.builder.ShapeType["FACE"]
        )
        sub_faces = self.builder.SubShapeAllSortedCentres(
            self.extrusion, self.builder.ShapeType["FACE"]
        )
        for face in sub_faces:
            self.builder.AddObject(self.wall_group, self.face_id(face))

        for face in (self.aqueous_face, self.organic_face, self.outlet_face):
            self.builder.RemoveObject(self.wall_group, self.face_id(face))

        self.builder.addToStudy(self.wall_group, "walls")

    def create_aqueous_group(self):
        self.aqueous_group = self.builder.CreateGroup(
            self.extrusion, self.builder.ShapeType["FACE"]
        )
        self.builder.AddObject(
            self.aqueous_group, self.face_id(self.aqueous_face)
        )
        self.builder.addToStudy(self.aqueous_group, "aqueous_inlet")

    def create_organic_group(self):
        self.organic_group = self.builder.CreateGroup(
            self.extrusion, self.builder.ShapeType["FACE"]
        )
        self.builder.AddObject(
            self.organic_group, self.face_id(self.organic_face)
        )
        self.builder.addToStudy(self.organic_group, "organic_inlet")

    def create_outlet_group(self):
        self.outlet_group = self.builder.CreateGroup(
            self.extrusion, self.builder.ShapeType["FACE"]
        )
        self.builder.AddObject(
            self.outlet_group, self.face_id(self.outlet_face)
        )
        self.builder.addToStudy(self.outlet_group, "outlet")

    def create_groups(self):
        self.create_wall_group()
        self.create_aqueous_group()
        self.create_organic_group()
        self.create_outlet_group()

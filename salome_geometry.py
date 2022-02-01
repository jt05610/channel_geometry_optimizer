#!/usr/bin/env python

import sys
import salome

salome.salome_init()
import salome_notebook

notebook = salome_notebook.NoteBook()
sys.path.insert(0, r"")


import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS


geompy = geomBuilder.New()
O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
Vertex_1 = geompy.MakeVertex(-1, -1, 0)
Vertex_2 = geompy.MakeVertex(-1, 1, 0)
Vertex_3 = geompy.MakeVertex(1, 1, 0)
Vertex_4 = geompy.MakeVertex(1, -1, 0)
Line_1 = geompy.MakeLineTwoPnt(Vertex_4, Vertex_3)
Line_2 = geompy.MakeLineTwoPnt(Vertex_3, Vertex_2)
Line_3 = geompy.MakeLineTwoPnt(Vertex_2, Vertex_1)
Line_1_vertex_2 = geompy.GetSubShape(Line_1, [2])
Line_4 = geompy.MakeLineTwoPnt(Vertex_1, Line_1_vertex_2)
Face_1 = geompy.MakeFaceWires([Line_1, Line_2, Line_3, Line_4], 1)
Vertex_5 = geompy.MakeVertex(2, 0, 0)
Face_1_vertex_4 = geompy.GetSubShape(Face_1, [4])
Line_5 = geompy.MakeLineTwoPnt(Vertex_5, Face_1_vertex_4)
Line_5_vertex_2 = geompy.GetSubShape(Line_5, [2])
Face_1_vertex_5 = geompy.GetSubShape(Face_1, [5])
Line_6 = geompy.MakeLineTwoPnt(Line_5_vertex_2, Face_1_vertex_5)
Face_2 = geompy.MakeFaceWires([Line_1, Line_5, Line_6], 1)
Fuse_1 = geompy.MakeFuseList([Face_1, Face_2], True, True)
Extrusion_1 = geompy.MakePrismDXDYDZ(Fuse_1, 0, 0, 2)
geompy.addToStudy(O, "O")
geompy.addToStudy(OX, "OX")
geompy.addToStudy(OY, "OY")
geompy.addToStudy(OZ, "OZ")
geompy.addToStudy(Vertex_1, "Vertex_1")
geompy.addToStudy(Vertex_2, "Vertex_2")
geompy.addToStudy(Vertex_3, "Vertex_3")
geompy.addToStudy(Vertex_4, "Vertex_4")
geompy.addToStudy(Line_1, "Line_1")
geompy.addToStudy(Line_2, "Line_2")
geompy.addToStudy(Line_3, "Line_3")
geompy.addToStudyInFather(Line_1, Line_1_vertex_2, "Line_1:vertex_2")
geompy.addToStudy(Line_4, "Line_4")
geompy.addToStudy(Face_1, "Face_1")
geompy.addToStudy(Vertex_5, "Vertex_5")
geompy.addToStudyInFather(Face_1, Face_1_vertex_4, "Face_1:vertex_4")
geompy.addToStudy(Line_5, "Line_5")
geompy.addToStudyInFather(Line_5, Line_5_vertex_2, "Line_5:vertex_2")
geompy.addToStudyInFather(Face_1, Face_1_vertex_5, "Face_1:vertex_5")
geompy.addToStudy(Line_6, "Line_6")
geompy.addToStudy(Face_2, "Face_2")
geompy.addToStudy(Fuse_1, "Fuse_1")
geompy.addToStudy(Extrusion_1, "Extrusion_1")


if salome.sg.hasDesktop():
    salome.sg.updateObjBrowser()

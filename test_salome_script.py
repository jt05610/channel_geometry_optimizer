import sys

sys.path.insert(
    0, r"C:\Users\taylojon\PycharmProjects\channel_geometry_optimizer"
)

from salome_interface import SalomeInterface, Point
from geometry import (
    create_lattice,
    lattice_point_set,
    lattice_line_gen,
    lattice_channel_gen,
)

interface = SalomeInterface()

lattice = create_lattice((2, 1, 2, 3, 2, 1, 2, 3, 2, 1, 1), 5, 0.5)

for point in lattice_point_set(lattice):
    interface.add_point(point)

for line in lattice_line_gen(lattice):
    interface.add_line(line)

for channel in lattice_channel_gen(lattice):
    interface.add_face(channel)

interface.fuse_faces(lattice)
interface.extrude(0.28 * 2)

if salome.sg.hasDesktop():
    salome.sg.updateObjBrowser()

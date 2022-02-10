import sys
import os

import killSalomeWithPort

sys.path.insert(
    0,
    r"/Users/jtaylor/PycharmProjects/channel_geometry_optimizer",
)

from salome_interface import SalomeInterface
from geometry import create_lattice

interface = SalomeInterface()

lattice = create_lattice(
    (3, 1, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 3, 2, 1, 1),
    2.5,
    0.5,
)

interface.create_geometry(
    lattice,
    0.56,
)
interface.create_mesh(
    r"/Users/jtaylor/PycharmProjects/channel_geometry_optimizer/meshes/3-1-1-2-1-2-1-2-1-2-1-2-3-2-1-1_2.5_0.5_0.56.unv",
)

killSalomeWithPort.killMyPort(os.getenv("NSPORT"))

import sys
import os

sys.path.insert(0, r"C:\Users\taylojon\PycharmProjects\channel_geometry_optimizer")

from salome_interface import SalomeInterface
from geometry import create_lattice
interface = SalomeInterface()

lattice = create_lattice(
    (2, 1, 2, 3, 2, 1, 2, 3, 2, 1, 1), 5, 0.5
)

save_name = r'C:/Users/taylojon/PycharmProjects/channel_geometry_optimizer/full_stack_from_bat.unv'
interface.create_geometry(lattice, 0.28*2)
interface.mesh_pipeline(save_name)

import killSalomeWithPort
killSalomeWithPort.killMyPort(os.getenv('NSPORT'))

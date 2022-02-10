# channel_geometry_optimizer

This in-progress project is for optimizing the design of microfluidic chips. 

## Design

Scripts are written for creating parametric microfluidic chip channel designs. The designs are turned into 3D geometries in SALOME. A 3D mesh is then
generated using the NETGEN 1D-2D-3D algorithm. The mesh is then exported as an IDEAS Unv file. An OpenFOAM case is generated with this design and solved
using multiphase solver. The results are then analyzed in ParaView for quality of mixing in the channel. A graph neural network may also be trained to predict mixing
based on channel design and fluid dynamic simulation parameters. The entire end-to-end operation is intended to be automated.

## Milestones

* The geometry is succesfully generated and meshing works as intended.
* OpenFOAM cases are generated based on templates.
* ParaView analysis is ~50% done.

## To accomplish
* End-to-end automation using Optuna or similar.
* Tensorflow graph neural network integration. 

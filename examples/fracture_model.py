
## Matthew Dorsey
## Max-Planck-Institute for Colloids and Interfaces
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## 2026.10.09

## FILENAME: examples/fracture_model.py
## PURPOSE: illustrate model used to study poroelastic fracture mechanics

## MODULES
# febio
from febio.feb.geometry.slab import gen_3d_slab_with_hole

## PARAMETERS
# none

## METHODS
# none

## ARGUMENTS
# none

## SCRIPT
# generate slab with hole geometry
m = gen_3d_slab_with_hole(show = False, save = True, hex_mesh = True, dx = 10., dy = 5., lc_min = 0.2)
m.save_model(overwrite = True) # save model to local directory, can load with febio
# TODO add poroelastic material, attach to geometry
# TODO apply boundary conditions to the surfaces
# TODO add step

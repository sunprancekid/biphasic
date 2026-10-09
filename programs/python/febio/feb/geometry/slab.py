
## Matthew Dorsey
## Max-Planck-Institute for Colloids and Interfaces
## matthew.dorsey@mpikg.mpg.de
## 2026.09.17

## FILENAME: programs/python/febio/feb/geometry/slab.py
## PURPOSE: create slab geometries with gmsh, add to febio model files

## MODULES
# native / conda
import gmsh
from febio.feb.model_file import ModelFile


## PARAMETERS
# default slab x-axis length
default_slab_lx = 100.
# default slab y-axis length
## MODULES
# native / conda
import gmsh
from febio.feb.model_file import ModelFile


## PARAMETERS
# default slab x-axis length
default_slab_lx = 100.
# default slab y-axis length
default_slab_ly = 100.
# default slab z-axis length
default_slab_lz = 5.
# default slab oval cutout x-axis diameter
default_slab_oval_dx = 10.
# default slab oval cutout y-axis diameter
default_slab_oval_dy = 5.
# default slab mesh characteristic mesh length
default_slab_mesh_lc = 2.

## METHODS
# generate plate geometry
def gen_3d_slab_with_hole(lx = default_slab_lx, ly = default_slab_ly, lz = default_slab_lz, dx = default_slab_oval_dx, dy = default_slab_oval_dy, lc = default_slab_mesh_lc, show = True, save = False, hex_mesh = True):
	""" generates 3d febio model for slab geometry with hole.

	Arguments:
	----------
	lx : float (mm)
		slab x-axis
	ly : float (mm)
		slab y-axis
	lz : float (mm)
		slab z-axis, oval cut out direction
	dx : float (mm)
		oval diameter in x-axis (must be less than l_x)
	dy : float (mm)
		oval diameter in y-axis (must be less than l_y)
	lc : float (mm)
		characteristic mesh size
	show : bool
		display meshing in gmsh GUI
	save : bool
		write gmsh to feb model, save
	hex_mesh : bool
		if 'True', generate hex mesh. Otherwise, generates with triagnular mesh.

	Returns:
	--------
	ModelFile
		xml formatter feb file if 'save' is 'True' (else None).
	"""

	# initialize gmsh API
	gmsh.initialize()

	# Create a new model named '3d_plate'
	gmsh.model.add("3d_plate")

	# create 2d geometry
	rect = gmsh.model.occ.addRectangle(0, 0, 0, lx, ly)
	hole = gmsh.model.occ.addDisk(lx/2, ly/2, 0, dx/2, dy/2)

	# Cut circular hole from plate
	plate, _ = gmsh.model.occ.cut([(2, rect)], [(2, hole)])
	gmsh.model.occ.synchronize()
	surface_tag = plate[0][1]

	# set mesh
	gmsh.model.mesh.setSize(gmsh.model.getBoundary([(2, surface_tag)],recursive=True), lc)
	# Recombine 2D triangles into quadrilaterals
	if hex_mesh: gmsh.model.mesh.setRecombine(2, surface_tag)

	# Extrude the surface in Z direction
	# numElements=[5] means 5 elements through thickness -> TODO this int should be related to lc
	# recombine=True creates hexahedral elements from the quadrilateral surface mesh
	out = gmsh.model.occ.extrude([(2, surface_tag)], 0, 0, lz, numElements=[5], recombine=True)
	gmsh.model.occ.synchronize()

	# generate 3D mesh
	gmsh.option.setNumber("Mesh.ElementOrder", 1)
	gmsh.model.mesh.generate(3)


	# Launch the Gmsh GUI to view the 3D model and mesh
	if show: gmsh.fltk.run()

	# pass model to febio
	if save:
		nodeTags, coords, parametricCoord = gmsh.model.mesh.getNodes(-1, -1)
		if hex_mesh:
			# get all hex elements
			elmType = 5
			elmTags, elmNodes = gmsh.model.mesh.getElementsByType(5, -1)
		else:
			# get all triangular elements
			elmType = 3
			elmTags, elmNodes = gmsh.model.mesh.getElementsByType(3, -1)
		febio_model = ModelFile("")
		febio_model.add_geometry(name = "slab_with_hole", element_type = elmType, node_tags = nodeTags, node_coordinates = coords.reshape(-1, 3), element_nodes = elmNodes.reshape(-1, 8), element_tags = elmTags)

		# Finalize the API to clear memory
		gmsh.finalize()
		return febio_model
	else:
		return # return nothing
default_slab_ly = 100.
# default slab z-axis length
default_slab_lz = 5.
# default slab oval cutout x-axis diameter
default_slab_oval_dx = 10.
# default slab oval cutout y-axis diameter
default_slab_oval_dy = 5.
# default slab mesh minimum characteristic length (at the hole edge)
default_slab_mesh_lc_min = 1.
# default slab mesh maximum characteristic length (far from the hole)
default_slab_mesh_lc_max = 5.

## METHODS
# generate plate geometry
def gen_3d_slab_with_hole(lx = default_slab_lx, ly = default_slab_ly, lz = default_slab_lz, dx = default_slab_oval_dx, dy = default_slab_oval_dy, lc_min = default_slab_mesh_lc_min, lc_max = default_slab_mesh_lc_max, show = True, save = False, hex_mesh = True):
	""" generates 3d febio model for slab geometry with hole.

	Arguments:
	----------
	lx, ly, lz : float (mm)
		slab dimensions (lz is the oval cut out direction)
	dx, dy : float (mm)
		oval diameters in x- and y-axis (must be less than lx, ly)
	lc_min : float (mm)
		characteristic mesh size at the edge of the hole
	lc_max : float (mm)
		characteristic mesh size far from the hole (reached at the slab boundary)
	show : bool
		display meshing in gmsh GUI
	save : bool
		write gmsh to feb model, save
	hex_mesh : bool
		if 'True', generate hex mesh. Otherwise, generates with triagnular mesh.

	Returns:
	--------
	ModelFile
		xml formatter feb file if 'save' is 'True' (else None).
	"""

	# initialize gmsh API
	gmsh.initialize()

	# Create a new model named '3d_plate'
	gmsh.model.add("3d_plate")

	# create 2d geometry
	rect = gmsh.model.occ.addRectangle(0, 0, 0, lx, ly)
	hole = gmsh.model.occ.addDisk(lx/2, ly/2, 0, dx/2, dy/2)

	# Cut circular hole from plate
	plate, _ = gmsh.model.occ.cut([(2, rect)], [(2, hole)])
	gmsh.model.occ.synchronize()
	surface_tag = plate[0][1]

	# find the curve(s) forming the hole edge: those lying entirely inside the hole's bounding box
	eps = 1e-6
	hole_curves = [tag for dim, tag in gmsh.model.getEntitiesInBoundingBox(
		lx/2 - dx/2 - eps, ly/2 - dy/2 - eps, -eps,
		lx/2 + dx/2 + eps, ly/2 + dy/2 + eps, eps, dim = 1)]

	# mesh size field: distance from the hole edge
	dist_field = gmsh.model.mesh.field.add("Distance")
	gmsh.model.mesh.field.setNumbers(dist_field, "CurvesList", hole_curves)
	gmsh.model.mesh.field.setNumber(dist_field, "Sampling", 200)

	# distance from the hole edge to the nearest slab edge: lc_max is reached here
	dist_max = min(lx - dx, ly - dy) / 2

	# threshold field: lc_min at the hole edge, linearly growing to lc_max at dist_max
	thr_field = gmsh.model.mesh.field.add("Threshold")
	gmsh.model.mesh.field.setNumber(thr_field, "InField", dist_field)
	gmsh.model.mesh.field.setNumber(thr_field, "SizeMin", lc_min)
	gmsh.model.mesh.field.setNumber(thr_field, "SizeMax", lc_max)
	gmsh.model.mesh.field.setNumber(thr_field, "DistMin", 0)
	gmsh.model.mesh.field.setNumber(thr_field, "DistMax", dist_max)
	gmsh.model.mesh.field.setAsBackgroundMesh(thr_field)

	# let the background field alone control the size
	gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
	gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
	gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
	gmsh.option.setNumber("Mesh.MeshSizeMin", lc_min)
	gmsh.option.setNumber("Mesh.MeshSizeMax", lc_max)

	if hex_mesh:
		# recombine triangles into quadrilaterals (Frontal-Delaunay for quads, full-quad recombination)
		gmsh.model.mesh.setRecombine(2, surface_tag)
		gmsh.option.setNumber("Mesh.Algorithm", 8)
		gmsh.option.setNumber("Mesh.RecombinationAlgorithm", 3)

	# extrude the surface in z; recombine=True creates hexahedra from the quad surface mesh
	n_layers = 5 # TODO: relate to lc_min
	gmsh.model.occ.extrude([(2, surface_tag)], 0, 0, lz, numElements=[n_layers], recombine=True)
	gmsh.model.occ.synchronize()

	# generate 3D mesh
	gmsh.option.setNumber("Mesh.ElementOrder", 1)
	gmsh.model.mesh.generate(3)


	# Launch the Gmsh GUI to view the 3D model and mesh
	if show: gmsh.fltk.run()

	# pass model to febio
	febio_model = None
	if save:
		nodeTags, coords, parametricCoord = gmsh.model.mesh.getNodes(-1, -1)
		if hex_mesh:
			# get all hex elements
			elmType = 5
			elmTags, elmNodes = gmsh.model.mesh.getElementsByType(5, -1)
		else:
			# get all triangular elements
			elmType = 3
			elmTags, elmNodes = gmsh.model.mesh.getElementsByType(3, -1)
		febio_model = ModelFile("")
		febio_model.add_geometry(name = "slab_with_hole", element_type = elmType, node_tags = nodeTags, node_coordinates = coords.reshape(-1, 3), element_nodes = elmNodes.reshape(-1, 8), element_tags = elmTags)

	# Finalize the API to clear memory
	gmsh.finalize()
	return febio_model


## CLASSES
# none


## ARGUMENTS
# none


## SCRIPT
# none

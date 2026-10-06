
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
# none


## METHODS
# generate plate geometry
def gen_3d_slab_with_hole(show = True, save = False, hex_mesh = True):
	""" generates 3d febio model for slab geometry with hole.

	Arguments:
	----------
	show : bool
		display mesh in gmsh
	save : bool
		save gmsh file
	hex_mesh : bool
		if 'True', generate hex mesh. Otherwise, generates with triagnular mesh.

	Returns:
	--------
	ModelFile
		xml formatter feb file
	"""
	## TODO add slab / hole dimensions to method call

	# initialize gmsh API
	gmsh.initialize()

	# Create a new model named '3d_plate'
	gmsh.model.add("3d_plate")

	# Define plate dimensions
	length = 100.0  # X-axis
	width = 50.0    # Y-axis
	thickness = 5.0 # Z-axis

	# Define hole parameters (centered in X and Y)
	hole_radius = 10.0
	hole_x = length / 2.0
	hole_y = width / 2.0

	# Target element size
	mesh_size = 2.5

	if not hex_mesh:

		# Use the OpenCASCADE kernel to easily build a 3D block
		# gmsh.model.occ.addBox(x, y, z, dx, dy, dz, tag=-1)
		plate_dimtag = gmsh.model.occ.addBox(0, 0, 0, length, width, thickness)

		# 2. Create a cylinder that will act as the tool to cut the hole
		# Arguments: (x, y, z) of base center, (dx, dy, dz) axis vector, radius
		hole_cylinder = gmsh.model.occ.addCylinder(hole_x, hole_y, 0, 0, 0, thickness, hole_radius)

		# 3. Perform the boolean subtraction (Plate minus Cylinder)
		# Arguments: object dimTags, tool dimTags
		# The cut function returns a tuple: (remaining_entities, mapping_of_entities)
		out, out_map = gmsh.model.occ.cut([(3, plate_dimtag)], [(3, hole_cylinder)])

		# Synchronize the OCC CAD kernel with the Gmsh model
		gmsh.model.occ.synchronize()

		# Set global mesh size fields (alternative to specifying at points)
		gmsh.option.setNumber("Mesh.MeshSizeMin", mesh_size)
		gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size)

		# --- Define Physical Groups ---
		# To apply loads or boundary conditions later, group the geometrical entities.
		# In a 3D model: volumes have dimension 3, surfaces have dimension 2.
		final_volume_tag = out[0][1]

		# 1. Volume Group (for material properties)
		# Get the tag of the 3D volume we just created
		# volume_tag = plate_dimtag
		gmsh.model.addPhysicalGroup(3, [final_volume_tag], name="Plate_Volume")

		# 2. Surface Groups (e.g., for clamping or pressure)
		# Let's find the boundary surfaces automatically using boundaries of our volume
		# dimTags is a list of (dim, tag) tuples
		boundaries = gmsh.model.getBoundary([(3, final_volume_tag)], combined=False, oriented=False)

		# Optional: Identify specific faces based on center coordinate
		# For instance, finding the face at X = 0 (left edge) to apply a clamp
		for dim, tag in boundaries:
			# Get mass center of the surface
			mass_center = gmsh.model.occ.getCenterOfMass(dim, tag)
			x_center = mass_center[0]

			if abs(x_center - 0.0) < 1e-5:
				gmsh.model.addPhysicalGroup(2, [tag], name="Clamped_Edge")
			elif abs(x_center - length) < 1e-5:
				gmsh.model.addPhysicalGroup(2, [tag], name="Loaded_Edge")

		# generate
		gmsh.model.mesh.generate(3)

	else:

		# # ------------------------------------------------------------
		# # Parameters
		# # ------------------------------------------------------------
		L = 100.0       # plate length
		W = 50.0        # plate width
		R = 10.0        # hole radius
		H = 5.0         # plate thickness

		lc = 2.0        # characteristic mesh size

		# ------------------------------------------------------------
		# Create the 2D geometry using OpenCASCADE
		# ------------------------------------------------------------
		rect = gmsh.model.occ.addRectangle(
			0, 0, 0,
			L, W
		)

		hole = gmsh.model.occ.addDisk(
			L/2, W/2, 0,
			R, R
		)

		# Cut circular hole from plate
		plate, _ = gmsh.model.occ.cut(
			[(2, rect)],
			[(2, hole)]
		)

		gmsh.model.occ.synchronize()

		# The resulting surface
		surface_tag = plate[0][1]
		print(surface_tag)

		# ------------------------------------------------------------
		# Mesh size
		# ------------------------------------------------------------
		gmsh.model.mesh.setSize(
			gmsh.model.getBoundary(
				[(2, surface_tag)],
				recursive=True
			),
			lc
		)

		# ------------------------------------------------------------
		# Recombine 2D triangles into quadrilaterals
		# ------------------------------------------------------------
		gmsh.model.mesh.setRecombine(2, surface_tag)

		# ------------------------------------------------------------
		# Extrude the surface in Z direction
		#
		# numElements=[5] means 5 elements through thickness
		# recombine=True creates hexahedral elements from
		# the quadrilateral surface mesh
		# ------------------------------------------------------------
		out = gmsh.model.occ.extrude(
			[(2, surface_tag)],
			0, 0, thickness,
			numElements=[5],
			recombine=True
		)

		gmsh.model.occ.synchronize()

		# ------------------------------------------------------------
		# Generate the 3D mesh
		# ------------------------------------------------------------
		gmsh.option.setNumber("Mesh.ElementOrder", 1)

		gmsh.model.mesh.generate(3)


	# Save the mesh to file
	if save: gmsh.write("plate_3d.msh")

	# Launch the Gmsh GUI to view the 3D model and mesh
	# Skip this in headless environments or batch runs
	if show: gmsh.fltk.run()

	# pass model to febio
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
	# febio_model = add_part_to_model3d(feb_model = ModelFile(""), name = "slab_with_hole", element_type = elmType, node_tags = nodeTags, node_coordinates = coords.reshape(-1, 3), element_nodes = elmNodes.reshape(-1, 8), element_tags = elmTags)

	# Finalize the API to clear memory
	gmsh.finalize()

	return febio_model



## CLASSES
# none


## ARGUMENTS
# none


## SCRIPT
# none

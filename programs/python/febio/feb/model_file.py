
## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max-Planck-Institut for Colloids and Interfacial Sciences
## 2026.03.12

## FILENAME: programs/python/feb/model.py
## PURPOSE: handle feb model files

## MODULES
# native, conda
import sys, os
import xml.etree.ElementTree as ET # handles xml formatting
# import gmsh
# local
from util.xml_file import xmlFile, add_element_to_tree

## PARAMETERS
# accepted element data properties
ELM_PROP = ['p']
# default biphasic material properties
default_biphasic_phi0 = 0.2
default_biphasic_elastic_modulus = 0.5 # MPa
default_biphasic_permeability = 0.001 ## mm ^4 / Ns
default_biphasic_tau = 0
default_biphasic_poisson_ratio = 0.33
default_biphasic_fluid_density = 1.0
default_biphasic_solid_density = 1.0
biphasic_poisson_ratio_min = 0.05
biphasic_poisson_ratio_max = 0.45
biphasic_phi0_min = 0.01
biphasic_phi0_max = 0.99

## METHODS
# none

## CLASSES
# model class
class ModelFile(xmlFile):

    """ handles xml formatted feb model files.

    Attributes:
    -----------
    None

    Methods:
    --------
    __init__():
        initialize model object.
    save_model():
        save model tree to file.
    update_model():
        save model tree file to location of original feb file.
    """

    def __init__ (self, feb_file = None):
        """

        Arguments:
        ----------
        feb_file : str
            path to feb file

        Returns:
        --------
        None
        """
        try:
            # attempt to load file
            super().__init__(feb_file)
            self.feb_file = self.xml_file
        except:
            # file cannot be loaded, reset model
            self.reset_model()

    def reset_model (self):
        """ reset element tree root, add base branches.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        # establish base
        self.root = ET.Element("febio_spec", attrib = {'version' : "4.0"})
        self.tree = ET.ElementTree(self.root)
        # add module
        self.add_element_to_tree(path = "", new_element = "Module", attributes = {'type': "biphasic"})
        self.add_element_to_tree(path = "Module", new_element = "units", value = "mm-N-s")
        # add base branches
        # Globals
        self.reset_globals()
        # Material
        self.add_element_to_tree(path = "", new_element = "Material")
        # MeshDomains
        self.add_element_to_tree(path = "", new_element = "Mesh")
        self.add_element_to_tree(path = "", new_element = "MeshDomains")
        # Boundary
        # Rigid
        # Contact
        # Step
        self.add_element_to_tree(path = "", new_element = "Step")
        # LoadData
        # Output
        self.reset_output()

    def save_model (self, saveto = None, saveas = None, overwrite = False):
        """ save model file.

        Parameters:
        -----------
        saveto : str (optional, default is './')
            path to save location
        saveas : str (optional, default is 'model.feb')
            path to location to save model.
        overwrite : bool
            if 'True' and the file already exists, it will not be overwritten.

        Returns:
        --------
        bool
            'True' if saving operation was successful, else 'False'.
        """
        # check the save directory
        if saveto is None:
            saveto = './'
        elif not os.path.exists(saveto):
            # if the path does not exists, make it
            os.makedirs(saveto)

        # check the filename
        if saveas is None:
            saveas = 'model.feb'

        # check if the file already exits
        savepath = saveto + saveas
        if os.path.exists(savepath) and not overwrite:
            print("ERROR :: Model.save_model() :: file '{0}' already exists and cannot be overwritten.".format(savepath))
            return False

        # write the tree to the file
        self.tree.write(savepath, encoding='ISO-8859-1', xml_declaration=True)
        return True

    def update_model (self, filename = None, overwrite = False):
        """ save model tree to location of original model file.

        Parameters:
        -----------
        overwrite : bool
            checks if the file already exists. if 'True', file is overwritten.

        Returns:
        --------
        bool
            'True' if writing operating was successful, else 'False'.
        """
        return self.save_model(self.feb_file, overwrite = overwrite)

    ## GLOBALS ##

    def reset_globals(self):
        """ assign default global values.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        # if globals already exists in root, remove element
        self.remove_element_from_tree('Globals')
        # readd globals with default values
        self.add_element_to_tree(path = '', new_element = 'Globals')
        self.add_element_to_tree(path = 'Globals', new_element = 'Constants')
        self.add_element_to_tree (path = 'Globals/Constants', new_element = 'T', value = '0')
        self.add_element_to_tree (path = 'Globals/Constants', new_element = 'P', value = '0')
        self.add_element_to_tree (path = 'Globals/Constants', new_element = 'R', value = '8.31446e-06')
        self.add_element_to_tree (path = 'Globals/Constants', new_element = 'Fc', value = '9.64853e-05')

    def set_globals(self):
        """ assign or update global values.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        pass

    ## MATERIALS ##

    def has_material(self, material_name = None, material_id = None, material_type = None):
        """ checks if material exists in mode file.

        Arguments:
        ----------
        material_name : str
            name of material which exists in 'febio_spec/Material'
        material_id : str or int
        material_type : str

        Returns:
        --------
        bool
            'True' if model file has material, else 'False'.
        """
        attrib_dict = {}
        if material_name is not None: attrib_dict.update({'name': material_name})
        if material_id is not None: attrib_dict.update({'id': material_id})
        if material_type is not None: attrib_dict.update({'type': material_type})
        return self.tree_has_element(elm_path = "Material/material", attrib_dict = attrib_dict) or self.tree_has_multiple_elements(elm_path = "Material/material", attrib_dict = attrib_dict)

    def add_biphasic_material (self, phi0 = None, elastic_modulus = None, poisson_ratio = None, permeability = None, material_name = None, material_id = None):
        """ add biphasic material to model.

        for this biphasic material, the solid is isotropic elastic and the
        permeability is constant isotropic.

        material cannot be added to model if another material with either the
        same 'material_id' or 'material_name' already exists in the model.

        Arguments:
        ----------
        phi0 : float (optional, default is 'default_biphasic_phi0')
            initial material solid fraction, must be a value within range (0., 1.)
        elastic_modulus : float (optional, default is 'default_biphasic_elastic_modulus')
            solid isotropic elastic modulus, units MPa
        poisson_ratio : float (optional, default is 'default_biphasic_poisson_ratio')
            solid poisson_ratio, must be a value within range (0., 1.)
        permeability : float (optional, default is 'default_biphasic_permeability')
            fluid permeability through solid, units mm^4 / N*s
        material_name : str (optional)
            name of material in model file, default is 'elastic_biphasic'
        material_id : int (optional)
            material id, default is lowest unused integer

        Returns:
        --------
        bool
            'True' if successful, else 'False.'
        """
        # check that the module for the feb model is biphasic
        if not self.tree_has_element(elm_path = "Module", attrib_dict = {"type": "biphasic"}):
            Exception("ERROR :: ModelFile.add_biphasic_material() :: biphasic material cannot be added to ModelFile whose 'Module' is not 'biphasic'.")
            return False
        # check that the material name and id is unique
        if self.has_material(material_name = material_name, material_id = material_id, material_type = "biphasic") and (material_name is not None or material_id is not None):
            # the material already exists, it cannot be added to the current model
            Exception("ERROR :: ModelFile.add_biphasic_material() :: material already exists in current model with attributes {0}.".format({"name": material_name, "id": material_id, "type": "biphasic"}))
            return False

        # if the material id is unspecified, find the first unused integer
        if material_id is None:
            i = 0
            while True:
                i += 1
                if not self.has_material(material_id = i):
                    material_id = i
                    break
        # if the material name is unspecified, use "elastic_phasic"
        if material_name is None: material_name = "elastic_biphasic"

        # check method arguments for material values within boundaries
        # phi0
        if phi0 is None:
            phi0 = default_biphasic_phi0
        elif (not isinstance(phi0, float)) or (phi0 < biphasic_phi0_min) or (phi0 > biphasic_phi0_max):
            Exception("ERROR :: ModelFile.add_biphasic_material() :: method argument 'phi0' is either not type 'float', or is outside the boundaries of ({0}, {1}) .. assigning 'phi0' default value of {2}.".format(biphasic_phi0_min, biphasic_phi0_max, default_biphasic_phi0))
            phi0 = default_biphasic_phi0
        # elastic modulus
        if elastic_modulus is None:
            elastic_modulus = default_biphasic_elastic_modulus
        elif (not isinstance(elastic_modulus, float)) and (not isinstance(elastic_modulus, int)):
            Exception("ERROR :: ModelFile.add_biphasic_material() :: method argument 'elastic_modulus' is not type 'float' or 'int' .. assigning 'elastic_modulus' default value '{0}'.".format(default_biphasic_elastic_modulus))
            elastic_modulus = default_biphasic_elastic_modulus
        # poisson ratio
        if poisson_ratio is None:
            poisson_ratio = default_biphasic_poisson_ratio
        elif not isinstance(poisson_ratio, float) or (poisson_ratio <= biphasic_poisson_ratio_min) or (poisson_ratio >= biphasic_poisson_ratio_max):
            Exception("ERROR :: ModelFile.add_biphasic_material() :: method argument 'poisson_ratio' is either not type 'float' or outside the boundaries of ({0}, {1}) .. assigning 'poisson_ratio' default vaule of {2}.".format(biphasic_poisson_ratio_min, biphasic_poisson_ratio_max, default_biphasic_poisson_ratio))
            poisson_ratio = default_biphasic_poisson_ratio
        # permeability
        if permeability is None:
            permeability = default_biphasic_permeability
        elif (not isinstance(permeability, float) and (not isinstance(permeability, int))):
            Exception("ERROR :: ModelFile.add_biphasic_material() :: method argument 'permeability' is not type 'float' or 'int' .. assigning 'permeability' default value '{0}'.".format(default_biphasic_permeability))
            permeability = default_biphasic_permeability

        # check that the model module is biphasic
        # add biphasic material with specified values
        self.add_element_to_tree(path = "Material", new_element = "material", attributes = {"name": material_name, "id": str(material_id), "type": "biphasic"}, duplicate = True)
        self.add_element_to_tree(path = "Material/material[@id='{0}']".format(material_id), new_element = "phi0", value = phi0, duplicate = True)
        self.add_element_to_tree(path = "Material/material[@id='{0}']".format(material_id), new_element = "fluid_density", value = default_biphasic_fluid_density, duplicate = True)
        self.add_element_to_tree(path = "Material/material[@id='{0}']".format(material_id), new_element = "tau", value = default_biphasic_tau, duplicate = True)
        # biphasic solid
        self.add_element_to_tree(path = "Material/material[@id='{0}']".format(material_id), new_element = "solid", attributes = {'type': "isotropic_elastic"}, duplicate = True)
        self.add_element_to_tree(path = "Material/material[@id='{0}']/solid".format(material_id), new_element = "density", value = default_biphasic_solid_density, duplicate = True)
        self.add_element_to_tree(path = "Material/material[@id='{0}']/solid".format(material_id), new_element = "E", value = elastic_modulus, duplicate = True)
        self.add_element_to_tree(path = "Material/material[@id='{0}']/solid".format(material_id), new_element = "v", value = poisson_ratio, duplicate = True)
        # biphasic permeability
        self.add_element_to_tree(path = "Material/material[@id='{0}']".format(material_id), new_element = "permeability", attributes = {'type': "perm-const-iso"}, duplicate = True)
        self.add_element_to_tree(path = "Material/material[@id='{0}']/permeability".format(material_id), new_element = "perm", value = permeability, duplicate = True)
        # successful
        return True


    ## MESH ##
    def has_object(self, name):
        """ determines if model has object.

        objects are list of nodes with specific coordinates.

        Arguments:
        ----------
        name : str
            name of object in model file.

        Returns:
        --------
        bool
            'True' if the object exists in the file, else 'False'.
        """
        if self.tree_has_element("Mesh/Nodes", attrib_dict = {'name': name}): return True
        else: return False

    def has_part(self, name):
        """ determines if model has part.

        parts are sets of nodes that make individual meshing elements.

        Arguments:
        ----------
        name : str
            name of part in mode file.

        Returns:
        --------
        bool
            'True' if part exists in file, else 'False'.
        """
        if self.tree_has_element("Mesh/Elements", attrib_dict = {'name': name}): return True
        else: return False

    def add_geometry (self, name = None, material = None, element_type = None, element_nodes = None, element_tags = None, node_tags = None, node_coordinates = None):
        """ add geometry as object and part to model.

        NOTE: currently meshing implemented for 'hex8' element types (element_type = 5 in gmsh module).

        Arguments:
        ----------
        name : str
            object and part name in model file.
        material : str (optional)
            attach already existing material to object in 'MeshDomains'
        element_type : int
            defines element type, according to 'gmsh' element type integers.
        element_nodes : ndarray
            2D array containing node ids making each element.
        element_types : ndarray
            1D array containing id for each element.
        node_tags : []
            1D array containing id for each node.
        node_coordinates : [][]
            2D array containing 3D coordinates for each node.

        Returns:
        --------
        bool
            'True' if operation was successful, else 'False'.
        """
        ## check method arguments
        # element type
        if element_type != 5:
            raise Exception ("ERROR :: ModelFile.add_geometry() :: method currently only supports 'hex8' element types (corresponding to 'element_type = 5').")
        else:
            element_name = 'hex8'
        # geometry material
        if material is not None:
            # check that the material exists in the model file
            pass
        # geometry name
        if name is None:
            # update object and part names
            object_name = "object1"
            part_name = "part1"
        else:
            # used name to specify object and part names
            object_name = name + "_object"
            part_name = name + "_part"

        ## add NODES as OBJECT
        self.add_element_to_tree (path = 'Mesh', new_element = 'Nodes', attributes = {'name': object_name})
        for t, xyz in zip(node_tags, node_coordinates):
            self.add_element_to_tree(path = 'Mesh/Nodes', new_element = 'node', value = f"{xyz[0]},{xyz[1]},{xyz[2]}", attributes = {'id': f"{t}"}, duplicate = True)

        ## add ELEMENTS as PART
        self.add_element_to_tree (path = 'Mesh', new_element = 'Elements', attributes = {'type': "hex8", 'name': part_name})
        for t, node in zip(element_tags, element_nodes):
            self.add_element_to_tree(path = 'Mesh/Elements', new_element = 'elem', value = f"{node[0]},{node[1]},{node[2]},{node[3]},{node[4]},{node[5]},{node[6]},{node[7]}", attributes = {'id': f"{t}"}, duplicate = True)

        # add material, if specified
        if material is not None:
            pass

    def has_surface(self, name):
        pass

    def define_surface(self, surface_name = None, object_name = None, node_tags = None, nodes = None):
        """ define surface on object by specifying set of nodes.

        Arguments:
        ----------
        object_name : str
            name of object in model file that has nodes
        node_tags : ndarray
            2D array of node ids, values correspond only to nodes in object
        name : str (optional)
            name assigned to surface. default assigned if unsepcified.

        Returns:
        --------
        bool
            'True' if successful, else 'False'
        """
        # check that the object already exists in the model file
        if (not self.has_object(object_name)) or (not isinstance(object_name, str)):
            Exception("ERROR :: ModelFile.define_surface() :: 'object_name' ('{0}') does not exist in model file, cannot procceed.".format(object_name))
            return False

        # check that the name does not already eixst
        if surface_name is None:
            # create default name of surface
            pass
        else:
            # check that the name does not already exist
            if self.has_surface(surface_name): pass

        # add NODES as SURFACE
        self.add_element_to_tree (path = 'Mesh', new_element = 'Surface', attributes = {'name': surface_name})
        for t, n in zip(node_tags, nodes):
            self.add_element_to_tree(path = f"Mesh/Surface[@name='{surface_name}']", new_element = 'quad4', value = f"{n[0]},{n[1]},{n[2]},{n[3]}", attributes = {'id': f"{t}"}, duplicate = True)
            ## TODO determine surface winding ..


    ## OUTPUT ##
    # reset output
    def reset_output (self):
        """ reset output.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        # add plotfile defaults
        self.add_element_to_tree(path = "", new_element = "Output")
        self.add_element_to_tree(path = "Output", new_element = "plotfile", attributes = {'type': "febio"}, duplicate = True)
        self.add_element_to_tree(path = "Output/plotfile", new_element = "var", attributes = {'type': "displacement"}, duplicate = True)
        self.add_element_to_tree(path = "Output/plotfile", new_element = "var", attributes = {'type': "stress"}, duplicate = True)
        self.add_element_to_tree(path = "Output/plotfile", new_element = "var", attributes = {'type': "relative volume"}, duplicate = True)
        self.add_element_to_tree(path = "Output/plotfile", new_element = "var", attributes = {'type': "solid stress"}, duplicate = True)
        self.add_element_to_tree(path = "Output/plotfile", new_element = "var", attributes = {'type': "effective fluid pressure"}, duplicate = True)
        self.add_element_to_tree(path = "Output/plotfile", new_element = "var", attributes = {'type': "fluid pressure"}, duplicate = True)
        self.add_element_to_tree(path = "Output/plotfile", new_element = "var", attributes = {'type': "fluid flux"}, duplicate = True)
        self.add_element_to_tree(path = "Output/plotfile", new_element = "compression", value = "1")

    # get element
    def add_element_data_to_logfile_output (self, elements = None, properties = None, filename = None, delim = None):
        """ adds instructions to write specific element data to property file.

        Arguments:
        ----------
        elements : int or List[int]
            integers ranging from 1 to the maximum number of elements in the mesh file.
        properties : str or List[str]
            list of properties which can be exported from febio simulation (from ELM_PROP)
        filename : str (optional, default is 'None')
            data is exported to specific file
        delim : str (optional, default is 'None')
            delimitter used during file writing

        Returns:
        -----------
        bool
            'True' if operation was successful, else 'False'.
        """
        # path to element data output in model tree
        elm_data_path = 'Output/logfile/element_data'
        ## check method arguments
        # check 'elements'
        if elements is None:
            print("ERROR :: Model.add_element_output() :: must specify 'elements' in method arguments.")
            return
        elif not isinstance(elements, list):
            if not isinstance(elements, int):
                print("ERROR :: Model.add_element_output() :: method argument 'elements' must be of type 'int' or 'List[int]'.")
                return
            else:
                elements = [elements]
        else:
            # elements is a list
            for i in range(len(elements) - 1, -1, -1):
                if not isinstance(elements[i], int):
                    # remove non integer elements from the list
                    print("ERROR :: Model.add_element_output() :: element '{0}' in 'elements' list is of non-integer type.".format(elements.pop(i)))
            if len(elements) == 0:
                print("ERROR :: Model.add_element_output() :: method argument 'elements' is an empty list.")
                return'https://example.com/api/data.xml'
        ## elements are now a list of integers
        ## convert list to str
        elements_str = ""
        for i in range(len(elements)):
            elements_str += "{:d}".format(elements[i])
            if i < len(elements) - 1:
                elements_str += ","
        # check 'properties'
        ## TODO complete ELM_PROP
        if not isinstance(properties, list):
            properties = [properties]

        # check element path in model tree
        # check if there is already element data
        if self.tree_has_element(elm_data_path):
            # element data output has already been specified within the model
            print("ERROR :: Model.add_element_output() :: model file '{0}' already has element data in '{1}'.".format(self.feb_file, elm_data_path))
            return

        ## establish attributes
        # create an attribute dictionary
        attrib_dict = {}
        # append properties
        prop_str = ""
        for i in range(len(properties)):
            # add properties to list
            if i != (len(properties) - 1):
                prop_str += "{0};".format(properties[i])
            else:
                prop_str += "{0}".format(properties[i])
        attrib_dict.update({'data': prop_str})
        # add the delimitter
        if delim is not None:
            attrib_dict.update({'delim': delim})
        if filename is not None:
            attrib_dict.update({'file': filename})
        self.add_element_to_tree(path = 'Output/logfile', new_element = 'element_data', value = elements_str, attributes = attrib_dict)
        return True



if __name__ == "__main__":
    pass
    ## ARGUMENTS
    # none

    ## SCRIPT
    # none

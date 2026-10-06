
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

    def has_material(self, material_name = None):
        """ checks if material exists in mode file.

        Arguments:
        ----------
        material_name : str
            name of material which exists in 'febio_spec/Material'

        Returns:
        --------
        bool
            'True' if model file has material, else 'False'.
        """
        pass

    ## MESH ##
    def add_geometry (self, name = None, material = None, element_type = None, element_nodes = None, element_tags = None, node_tags = None, node_coordinates = None):
        """ add geometry as object and part to model.

        NOTE: currently meshing implemented for 'hex8' element types (element_type = 5).

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

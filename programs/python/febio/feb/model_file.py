
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
# adds part to model file
def add_part_to_model3d(feb_model, namem, element_type, element_nodes, element_tags, node_tags, node_coordinates):
    """ translated gmsh model to febio model.

    Arguments:
    ----------
    feb_model : ModelFile
        xml formatted model for febio simulation
    name : str
    element_type : int
        integer corresponding to element type in gmsh
    element_nodes : []
    element_tags : []
    node_tags : []
        list of cordinate numbers
    node_coordinates : []
        list of spatial coordinates for each node in 3-dim

    Returns:
    -------
    bool
    """
    # if unspecified, create empty model
    # print all nodes and their positions
    for t, xyz in zip(node_tags, node_coordinates):
        print(f"Node #{t} is at {xyz}.")

    # print all elements and their nodes
    for t, node in zip(element_tags, element_nodes):
        print(f"Element #{t} has nodes {node}")

    # add NODES as OBJECT
    # add ELEMENTS as PART
    # iteratively add nodes and elements to MESH section
    # check for either test4 or hex8 elements.\
    # tube: https://www.youtube.com/watch?v=cQwYmk3bMSo&t=114s

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
        # add base branches
        # Globals
        self.reset_globals()
        # Material
        add_element_to_tree (root = self.root, elm_path = '', tag = 'Material')
        # MeshDomains
        add_element_to_tree (root = self.root, elm_path = '', tag = 'Mesh')
        # Boundary
        # Rigid
        # Contact
        # LoadData
        # Output

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

    ## OUTPUT ##

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

    ## TODO :: add methods for writing plotfile, rigid_body data


if __name__ == "__main__":
    pass
    ## ARGUMENTS
    # none

    ## SCRIPT
    # none


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
# local
# none

## PARAMETERS
# accepted element properties
ELM_PROP = ['p']

## METHODS
# none

## CLASSES
# model class
class Model(object):

    """ handles xml formatted feb model files.

    Attributes:
    -----------
    None

    Methods:
    --------
    None
    """

    def __init__ (self, feb_file):
        """

        Arguments:
        ----------
        feb_file : str
            path to feb file

        Returns:
        --------
        Model
            initialized Model object
        """
        # check that the path exists
        if not os.path.exists(feb_file):
            print("ERROR :: Model.__init__() :: path to model file '{0}' cannot be found.".format(feb_file))
            return None
        # load file tree
        self.feb_file = feb_file
        self.tree = ET.parse(feb_file)
        self.root = self.tree.getroot()
        # TODO get max number of elements from meshing file

    def update_model (self, filename = None, overwrite = False):
        """ save model to feb_file location, unless otherwise specified.

        Parameters:
        -----------
        filename : str (default location is 'feb_file')
            path to location to save file.
        overwrite : bool
            checks if the file already exists. if 'True', file is overwritten.

        Returns:
        --------
        bool
            'True' if writing operating was successful, else 'False'.
        """
        # check the filename
        if filename is None:
            filename = self.feb_file
        # check if the path already exists
        if os.path.exists(filename) and not overwrite:
            # the file exists and should not be overwritten
            print("ERROR :: Model.update_model() :: model file '{0}' already exists and cannot be overwritten.".format(filename))
            return False
        # write the tree to the file
        self.tree.write(filename, encoding='ISO-8859-1', xml_declaration=True)

    # show sub elements
    def show_sub_elements (self, path = None):
        """ write elements below specified path to CLT.

        Arguments:
        ----------
        path : str
            path in model xml tree which exists.

        Returns:
        --------
        None
        """
        # check that the path exists
        if self.has_element(path):
            print("The path '{0}' exists.".format(path))
            for child in self.root.findall(path):
                print(child.tag)
        else:
            print("The path '{0}' does not exist.".format(path))

    def has_element(self, elm_path = None):
        """ check it element path exists within model tree.

        Arguments:
        ----------
        elm_path : str
            xml format path

        Returns:

    def update_model (self):

        --------
        bool
            'True' is the element pathway exists, else 'False'.
        """
        if elm_path is None:
            return False
        elm = self.root.findall(elm_path)
        if elm is None or (isinstance(elm, list) and len(elm) == 0):
            return False
        else:
            return True

    def has_multiple_elements (self, elm_path = None):
        """ checks if multiple elements exists in tree at specified location.

        Parameters:
        -----------
        elm_path : str
            path to element in model tree

        Returns:
        --------
        bool
            'True' if path describes multiple elements in model tree, else 'False'
        """
        if elm_path is None:
            return False
        elm = self.root.findall(elm_path)
        if elm is None or (isinstance(elm, list) and len(elm) == 1):
            return False
        else:
            return True

    # add element
    def add_element_to_tree (self, path = None, new_element = None, value = None, attributes = None, duplicate = False):
        """ adds element to model tree.
        
        Arguments:
        ----------
        path : str
            path in tree which points to location to store element
        new_element : str
            name of element stored at path
        value : str
            value which is stored in element tree
        attributes : dict
            additional properties which are associated with element
        duplicate : bool (default is 'False')
            if 'True', checks that element does not already exist in path before appending.

        Returns:
        --------
        bool
            'True' if operation successful, else 'False.'
        """
        # check if duplicates exist
        if self.has_multiple_elements(path):
            print("ERROR :: Model.add_element_to_tree() :: unable able to add element '{0}', multiple paths '{1}' exist.")
            return False
        # check that value is a string
        if not isinstance(value, str):
            print("ERROR :: Model.add_element_to_tree() :: method argument 'value' must be type 'str'.")
            return False
        # get element at path
        elm = self.tree.getroot().find(path)
        # append subelement
        sub = ET.SubElement(elm, new_element, attrib = attributes)
        if value is not None:
            sub.text = value

    # remove element

    # get element

    def add_output_element (self, elements = None, properties = None, filename = None):
        """ adds instructions to write specific element data to property file.

        Arguments:
        ----------
        elements : int or List[int]
            integers ranging from 1 to the maximum number of elements in the mesh file.
        properties : str or List[str]
            list of properties which can be exported from febio simulation (from ELM_PROP)
        filename : str (optional)
            data is exported to specific file

        Returns:
        -----------
        None
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
                return
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
        if self.has_element(elm_data_path):
            # element data output has already been specified within the model
            print("ERROR :: Model.add_element_output() :: model file '{0}' already has element data in '{1}'.".format(self.feb_file, elm_data_path))
            return

        ## ADD element output into the model tree
        # create an attribute dictionary
        attrib_dict = {}
        prop_str = ""
        for i in range(len(properties)):
            # add properties to list
            if i != (len(properties) - 1):
                prop_str += "{0},".format(properties[i])
            else:
                prop_str += "{0}".format(properties[i])
        attrib_dict.update({'data': prop_str})
        ## TODO :: add filename if requested
        self.add_element_to_tree(path = 'Output/logfile', new_element = 'element_data', value = elements_str, attributes = attrib_dict)
        pass


if __name__ == "__main__":
    pass
    ## ARGUMENTS
    # none

    ## SCRIPT
    # none

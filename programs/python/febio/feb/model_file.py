
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
# accepted element data properties
ELM_PROP = ['p']

## METHODS
# none

## CLASSES
# model class
class ModelFile(object):

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
    show_tree_sub_elements():
        write elements below specified path to CLT, if any.
    tree_has_element():
        check if element exists within model tree.
    tree_has_multiple_elements():
        check if multiple elements exist within model tree.
    add_element_to_tree():
        add element to model tree.
    remove_element_from_tree():
        removes element from model tree.
    add_element_data_to_logfile_output():
        add intructions to model file to write property data from specific elements to logfile.
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
            print("ERROR :: Model.save_model() :: file '{0}' already exists and cannot be overwritte.".format(savepath))
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

    ## XLM ROOT / TREE

    # show sub elements
    def show_tree_sub_elements (self, path = None):
        """ write elements below specified path to CLT, if any.

        Arguments:
        ----------
        path : str
            path in model xml tree which exists.

        Returns:
        --------
        None
        """
        # check that the path exists
        if self.tree_has_element(path):
            print("The path '{0}' exists.".format(path))
            for child in self.root.findall(path):
                print(child.tag)
        else:
            print("The path '{0}' does not exist.".format(path))

    def tree_has_element(self, elm_path = None):
        """ check it element path exists within model tree.

        Arguments:
        ----------
        elm_path : str
            xml format path

        Returns:
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

    def tree_has_multiple_elements (self, elm_path = None):
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

    # update element
    def update_element_value (self, elm_path, value, format_str = "{0}"):
        """ updates tag associated with element.

        if element path correspondes to multiple elements, method aborts.

        Arguments:
        ----------
        elm_path : str
            path to element in model, there cannot be duplicate
        value
            value stored in element, can be any type but will be stored as string
        format_str : str (optional, default is "{0}")
            optional format string

        Returns:
        --------
        bool
            'True' if operation is successful, else 'False'
        """
        # check the element path
        if not self.tree_has_element(elm_path):
            print("ERROR :: ModelFile.update_element_value() :: model does not have any elements corresponding to '{0}'.".format(elm_path))
            return False
        elif self.tree_has_multiple_elements():
            print("ERROR :: ModelFile.update_element_value() :: model has multiple elements corresponding to {0}.".format(elm_path))
            return False

        # get the element, update it's value
        for elm in self.root.findall(elm_path):
            elm.text = format_str.format(value)

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
        if self.tree_has_multiple_elements(path):
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
    def remove_element_from_tree (self, path = None):
        """ remove specified path and subelements from the model tree.

        Arguments:
        ----------
        path : str
            existing xml path in model tree

        Returns:
        --------
        bool
            'True' if operation was successful, else 'False'.
        """
        pass

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

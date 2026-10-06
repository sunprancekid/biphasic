
##

## MODULES
# native / conda
import sys, os
import copy
import pandas as pd # DataFrame
import xml.etree.ElementTree as ET # handles xml formatting
# local


## PARAMETERS
# none


## METHODS
# collects all paths in element tree
def rec_elm_tree (root, abs_path = None, sl = None):
    """ recursively gets paths of all elements in a tree with attributes.

    Arguments:
    ----------
    root : element
        element with sub-elements
    abs_path : str
        absolute path to root
    sl : List[str]
        string list containing paths in root

    Returns:
    --------
    List[str]
        list of strings containing absolute path of all elemnts in tree.
    """
    if abs_path is None:
        abs_path = " "
    if sl is None:
        sl = []
    for child in root:
        # translate child text to string
        cld_txt = str(child.text)
        if "\t" in cld_txt:
            cld_txt = ""
        # translate child attributes to string
        cld_att = str(child.attrib)
        if not child.attrib:
            cld_att = ""
        nxt_path = ""
        if abs_path == " ":
            nxt_path = abs_path + root.tag
        else:
            nxt_path = abs_path + "/" + root.tag
        sl.append(nxt_path + "/" + child.tag + " " + cld_txt + " " + cld_att)
        subelm_list = root.findall(child.tag + "/")
        if not (subelm_list is None or (isinstance(subelm_list, list) and len(subelm_list) == 0)):
            # sl.append(root.tag + "/" + child.tag + " ... (x{0})".format(len(subelm_list)))
            rec_elm_tree(child, abs_path = nxt_path, sl = sl)
    return sl

# checks if path exists in element tree
def tree_has_path (root, elm_path):
    """ determines if xml path exists in root tree.

    Arguments:
    ----------
    root : Element
        contains element tree
    elm_path : str
        xml path to check for in root tree

    Returns:
    --------
    bool
        'True' if element path exists in root, else 'False'
    """
    if elm_path is None:
        return False
    elm = root.findall(elm_path)
    if elm is None or (isinstance(elm, list) and len(elm) == 0):
        return False
    else:
        return True

# add element to tree
def add_element_to_tree(root, elm_path, tag, value = None, attributes = None, duplicate = False):
    """ adds element to tree. if the element already exists, properties are replaced.

    Arguments:
    ----------
    root : Element
        element tree which sub-elements can be added to
    elm_path : str
        element path which exists in root tree, location where new element is stored
    tag : str
        name of new element in element tree
    value : str
        value which is stored in new element
    attributes : dictY
        attributes associated with element
    duplicate : bool (optional, default is 'False')
        if 'True', adds duplicate tag to elm path if it already exists

    Returns:
    --------
    bool
        'True' if addition operation was successful, else 'False'
    """
    # if an element path has been specified
    if elm_path:
        # check that the path exists
        if not tree_has_path(root, elm_path): return False
        # check that tag does not exist in element path
        if (not duplicate) and tree_has_path (root, elm_path + "/" + tag):
            # if it does, replace the values and attributes
            for elm in root.findall(elm_path + "/" + tag):
                # replace the value
                if value is not None:
                    elm.text = str(value)
                # remove the previous attributes
                if attributes is not None:
                    old_attrib = copy.deepcopy(elm.attrib)
                    for a in old_attrib:
                        elm.attrib.pop(a)
                    # add new attributes
                    for a in attributes:
                        elm.set(a, attributes[a])
            return True
        else:
            # if it does not, add new subelement to tree with attributes and values
            # get element at path
            elm = root.find(elm_path)
            # append subelement
            if attributes:
                sub = ET.SubElement(elm, tag, attrib = attributes)
            else:
                sub = ET.SubElement(elm, tag)
            if value is not None:
                sub.text = value
            return True
    else: # the element path is an empty string, append tag to root
        if (not duplicate) and tree_has_path(root, tag):
            # replace the attributes of tag
            for elm in root.findall(tag):
                # replace the value
                if value is not None:
                    elm.text = str(value)
                # remove the previous attributes
                if attributes is not None:
                    old_attrib = copy.deepcopy(elm.attrib)
                    for a in old_attrib:
                        elm.attrib.pop(a)
                    # add new attributes
                    for a in attributes:
                        elm.set(a, attributes[a])
            return True
        else:
            # add new sub element to root
            if attributes:
                sub = ET.SubElement(root, tag, attrib = attributes)
            else:
                sub = ET.SubElement(root, tag)
            if value is not None:
                sub.text = str(value)
            return True

# remove element from tree
def remove_element_from_tree (root, elm_path):
    """  removes element from element tree 'root'

    Arguments:
    ----------
    root : Element
        element tree with sub elements
    elm_path : str
        path to element that should be removed, exists in root
    """
    for elm in root.findall(elm_path):
        root.remove(elm)

## CLASSES
# handles xml files
class xmlFile (object):
    """ class used for handling xml formatted files as objects.

    Attributes:
    -----------
    xml_file : str
        path to xml file
    root : ET
        root for xml tree
    tree : ET
        xml element tree base

    Methods:
    --------
    __init__():
        initialize xml object
    __str__():
        return xml object state as string
    tree_has_element():
        determines if element path exists in element tree
    tree_has_multiple_elements():
        determines if multiple elements paths exist in element tree
    show_tree_sub_elements():
        returns string containg all subelements from element path.
    update_element_value():
        repalce element value.
    add_element_to_tree():
        add new element to tree
    remove_element_from_tree():
        remove existing element from tree
    """
    # init
    def __init__ (self, xml_file = None):
        """ initialize xml object.

        attempts to load xml_file. if the file does not exist or cannot be
        loaded then an exception is thrown.

        Arguments:
        xml_file : str
            path to xml file.

        Returns:
        None
        """
        # if file exists, load file
        if os.path.exists(xml_file):
            self.xml_file = xml_file
            self.tree = ET.parse(xml_file)
            self.root = self.tree.getroot()
        else:
            raise Exception("ERROR :: xmlFile.__init()__ :: file '{0}' does not exist.".format(xml_file))

    # str
    def __str__ (self):
        """ returns all xml path in tree as string.

        Arguments:
        ----------
        None

        Returns:
        --------
        str
        """
        # get absolute paths for all elements in tree
        l = rec_elm_tree(self.root)
        # convert list of elements to string
        s = ""
        for i in range(len(l)):
            # append element absolute path
            s += l[i]
            # add newline character if not last string
            if i != len(l) - 1: s += "\n"
        # return string
        return s

    # write xml file
    def write_xml (self):
        """ write xml file with tab indentations.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        pass

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

    # show sub elements
    def show_tree_sub_elements (self, path = None):
        """ returns string that has all subpaths below path.

        Arguments:
        ----------
        path : str
            path in model xml tree which exists.

        Returns:
        --------
        str
        """
        # check that the path exists
        if self.tree_has_element(path):
            # get all elements in tree
            l = rec_elm_tree(self.root, abs_path = None)
            # convert list of elements to string
            s = ""
            for i in range(len(l)):
                # append element absolute path, only if it contains the subpath
                if path in l[i]:
                    if s: s += "\n"
                    s += l[i]
                    # add newline character if not last string
                    # if i != len(l) - 1: s += "\n"
            # return string
            return s
        else:
            return ""

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
        # if self.tree_has_multiple_elements(path):
        #     print("ERROR :: Model.add_element_to_tree() :: unable able to add element '{0}', multiple paths '{1}' exist.")
        #     return False
        # # check that value is a string
        # if not isinstance(value, str):
        #     print("ERROR :: Model.add_element_to_tree() :: method argument 'value' must be type 'str'.")
        #     return False
        # get element at path
        add_element_to_tree(root = self.root, elm_path = path, tag = new_element, value = value, attributes = attributes, duplicate = duplicate)

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
        if self.tree_has_element(path):
            remove_element_from_tree(self.root, path)
            return True
        else:
            return False


## ARGUMENTS
# none


## SCRIPT
# none

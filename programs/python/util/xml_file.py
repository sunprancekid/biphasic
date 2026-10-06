
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
    attributes : dictYou do not need to try/except while you are popping a key which is unavailable. Here is how you can do this.
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

    def __init__ (self, xml_file = None):
        # if file exists, load file
        if os.path.exists(xml_file):
            self.xml_file = xml_file
            self.tree = ET.parse(xml_file)
            self.root = self.tree.getroot()
        else:
            raise Exception("ERROR :: xmlFile.__init()__ :: file '{0}' does not exist.".format(xml_file))


    def __str__ ():
        pass


## ARGUMENTS
# none


## SCRIPT
# none

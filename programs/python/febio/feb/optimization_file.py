
## Matthew A. Dorsey
## matthew.dorsey@mpikg.mpg.de
## @mad-mpikg
## Max-Planck-Institute for Colloids and Interfaces
## 2026.05.27

## FILENAME: programs/python/febio/feb/optimization_file.py
## PURPOSE: handle, generate optimization files for febio


## MODULES
# native, conda
import sys, os
import copy
import xml.etree.ElementTree as ET # handles xml formatting
# local
# none

## PARAMTERS
## default values
# default objective tolerance
default_objective_tolerance = 0.00001
# default f_diff_scale value
default_f_diff_scale = 0.01
# default log_level value
default_log_level = "LOG_FILE_AND_SCREEN"
# default print_level value
default_print_level = "PRINT_VERBOSE"


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
        print(elm_path)
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
    """

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
# used for handling optimization files
class OptimizationFile (object):
    """ handles, generates optimization files for febio.

    Attributes:
    -----------
    None

    Methods:
    --------
        return
    __init__():
        initialize object
    __str__():
        return string representation of optimization file xml tree
    load_optimization_file():
        load existing file into object

    """

    def __init__ (self, filepath = None):
        """ initialize optimization file.

        if 'filepath' is specified, the optimization file is loaded from
        the existing format. if not, a blanck optimization file is generated.

        Arguments:
        ----------
        filepath : str
            path to existing optimization file

        Returns:
        --------
        None
        """
        if filepath is not None:
            self.load_optimization_file(filepath)
        else:
            self.reset_optimization_file()

    def __str__(self):
        """ return optimization file as string.

        Arguments:
        ----------
        None

        Returns:
        --------
        str
            file state as string.
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

    def load_optimization_file (self, filepath):
        """ replace object with existing data from file.

        Arguments:
        ----------
        None

        Returns:
        --------
        bool
            'True' if file was successfully loaded into object, else 'False'.
        """
        # check that the file exists
        if not os.path.exists(filepath):
            print("ERROR :: OptimizationFile.load_optimization_file() :: path '{0}' does not exist, unable to load.".format(filepath))
            return False
        # parse the element tree
        self.tree = ET.parse(filepath)
        self.root = self.tree.getroot()
        return True

    def save_optimization_file (self, directory, filename):
        """

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        pass

    def reset_optimization_file (self):
        """ reset all mandatory fields.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        self.root = ET.Element("febio_optimize")
        # reset options
        self.reset_options()
        # reset parameters
        self.reset_parameters()
        # reset objective
        pass

    ## PARAMETERS

    def reset_parameters (self):
        """ remove any parameters assigned to root.

        Arguments:
        ----------
        None

        Returns:
        -----------
        None
        """
        # remove previous parameters from list
        if tree_has_path(self.root, "Parameters"):
            remove_element_from_tree(self.root, "Parameters")
        # add new parameters branch to root
        add_element_to_tree(self.root, "", "Parameters", value = "")

    def add_parameters (self, name, min_val, max_val, start_val):
        """ add parameter to tree

        NOTE: for more about paraemters, see below.

        https://help.febio.org/docs/FEBioUser-4-1/UM41-Subsection-7.1.3.html

        Arguments:
        ----------
        name : str
            path to model parameter in 'feb' file
        min_val : float
            minimum possible value to assign to parameter during optimization
        max_val : float
            maximum possible value to assign to parameter during optimization
        start_val : float
            initial value assigned during parameter during optimization

        Returns:
        --------
        None
        """
        # todo :: boolean for duplicates
        add_element_to_tree(self.root, "Parameters", "parm", value = "{0:.4f},{1:.4f},{2:.4f}".format(start_val, min_val, max_val), attributes = {"name": name})

    def has_parameters (self):
        """ determines if any parameters has been specified.

        Arguments:
        ----------
        None

        Returns:
        --------
        bool
            'True' if optimization file has parameters, else 'False'
        """
        return tree_has_path(self.root, "Parameters/param")

    ## OPTIONS

    # set options
    def set_options (self, obj_tol = None, f_diff_scale = None, log_level = None, print_level = None):
        """ update certain options. unspecified options are left unchanged.

        NOTE: only levmar type optimization are performed.

        Read more here: https://help.febio.org/docs/FEBioUser-4-1/UM41-Subsection-7.1.2.html

        Arguments:
        ----------
        obj_tol : float (optional, default is 'None')
            objective tolerance value
        f_diff_scale : float (optional, default is 'None')
            forward difference scale factor value
        log_level : str (optional, default is 'None')
            log_level value
        print_level : str (optional, default is 'None')
            print_level value

        Returns:
        --------
        None
        """
        if obj_tol is not None: self.set_objective_tolerance(obj_tol)
        if f_diff_scale is not None: self.set_f_diff_scale(f_diff_scale)
        if log_level is not None: self.set_log_level(log_level)
        if print_level is not None: self.set_print_level(print_level)

    # reset options
    def reset_options(self):
        """ set all options to their default values.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        add_element_to_tree(self.root, "" , "Options", value = "", attributes = {"type" : "levmar"})
        self.reset_objective_tolerance()
        self.reset_f_diff_scale()
        self.reset_log_level()
        self.reset_print_level()

    # objective tolerence
    def set_objective_tolerance (self, value, attributes = None):
        """ assigns objective tolerance to optimization value

        Arguments:
        ----------
        value : float
            objective tolerance value (real number greater than 0)
        attributes : dict (optional, default is 'None')
            replace previous attributes with new attributes

        Returns:
        --------
        None
        """
        # adjust the value
        add_element_to_tree(self.root, "Options", "obj_tol", value = value, attributes = attributes)

    # reset objective tolerance
    def reset_objective_tolerance (self):
        """ assigns default value to objective tolerance.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        self.set_objective_tolerance(default_objective_tolerance)

    # set f_diff_scale
    def set_f_diff_scale (self, value, attributes = None):
        """ change fdiff scale value and attributes.

        Arguments:
        ----------
        value : float
            'f_diff_scale' value (real number greater than 0)
        attributes : dict (optional, default is 'None')
            replace previous attributes with new attributes

        Returns:
        --------
        None
        """
        add_element_to_tree(self.root, "Options", "f_diff_scale", value = value, attributes = attributes)

    # reset f_diff scale
    def reset_f_diff_scale (self):
        """ assign 'f_diff_scale' parameter default value.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        self.set_f_diff_scale(default_f_diff_scale)

    # set log_level field
    def set_log_level (self, value, attributes = None):
        """ sets log level to user specified value.

        Arguments:
        ----------
        value : str
            'log_level' value
        attributes : dict (optional, default is 'None')
            replace previous attributes with new attributes

        Returns:
        --------
        None
        """
        add_element_to_tree(self.root, "Options", "log_level", value = value, attributes = attributes)

    # reset log level field
    def reset_log_level (self):
        """ sets log level field to default value

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        self.set_log_level(default_log_level)

    # set print_level field
    def set_print_level (self, value, attributes = None):
        """

        Arguments:
        ----------
        value : str
            'print_level' value
        attributes : dict (optional, default is 'None')
            replace previous attributes with new attributes

        Returns:
        --------
        None
        """
        add_element_to_tree(self.root, "Options", "print_level", value = value, attributes = attributes)

    # reset print level field
    def reset_print_level (self):
        """ resets print level to default value.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        self.set_print_level(default_print_level)

    ## DATA

    def reset_objective (self):
        """ reset objective section.

        NOTE :: here, only 'data-fit' is used (see link below).

        https://help.febio.org/docs/FEBioUser-4-1/UM41-Subsection-7.1.4.html

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        # remove objective
        if tree_has_path(self.root, "Objective"):
            remove_element_from_tree(self.root, "Objective")
        # add objective
        add_element_to_tree (self.root, "", "Objective", value = "", attributes = {'type': 'data-fit'})
        # reset data, objective function
        self.reset_optimization_function()
        self.reset_data()

    def reset_data (self):
        """ remove data from optimization model.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        # remove data if it exists on the root tree already
        if tree_has_path(self.root, "Objective/data"):
            remove_element_from_tree(self.root, "Obhttps://help.febio.org/docs/FEBioUser-4-1/UM41-Subsection-7.1.4.htmljective/data")
        # add empty sub-tree
        add_element_to_tree(self.root, "Objective", "data", value = "")

    def add_data_pair (self, x_val, y_val):
        """ append single data set to data points.

        Arguments:
        ----------
        x_val : float
            x value
        y_val : float
            y value

        Returns:
        --------
        None
        """
        add_element_to_tree(self.root, "Objective/data", "pt", value = "{0:.4f},{1:.4f}".format(x_val, y_val))

    def add_data_list (self, x_list, y_list):
        """ append a list of data points to data list.

        Arguments:
        ----------
        x_list : List[float]
            list of floats, same length as 'y_list'
        y_list : List[float]
            list of floats, same length as 'x_list'

        Returns:
        --------
        None
        """
        # check that the list of values are the same length
        if len(x_list) != len(y_list):
            print("ERROR :: OptimizationFile.add_data_list() :: length of arguments 'x_list' and 'y_list' are unequal.")
            return

        # loop through each pair, append
        for i in range(len(x_list)):
            self.add_data_pair(x_list[i], y_list[i])

    def get_data (self):
        """

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        pass

    def has_data (self):
        """

        Arguments:
        ----------
        None

        Returns:
        --------
        bool
            'True' if data points have been attached to optimization, else 'False'.
        """
        return tree_has_path(self.root, "Objective/data/pt")

    def reset_optimization_function (self):
        """ resets optimization function assigned to optimization file.

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        # remove function if it already exists in the tree
        if tree_has_path (self.root, "Objective/fnc"):
            remove_element_from_tree (self.root, "Objective/fnc")
        # add empty tree to optimization file
        add_element_to_tree(self.root, "Objective", "fnc", value = "", attributes = {'type': 'parameter'})

    def set_optimization_function (self):
        """

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """
        pass

    def get_optimization_function (self):
        """

        Arguments:
        ----------
        None

        Returns:
        --------
        None
        """

    def has_optimization_function (self):
        """

        Arguments:
        ----------
        None

        Returns:
        --------
        bool
            'True' if optimization function has been attached to file, else 'False'.
        """
        pass

## ARGUMENTS
# none


## SCRIPT
# none

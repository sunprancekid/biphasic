
## Matthew A. Dorsey
## @ mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfaces
## the goal of this program is to extract or augment informtion stored in '.feb' type files

## PACKAGES
# conda / python native
import sys, os
import xml.etree.ElementTree as ET

# local
# none

## PARAMETERS
# non-zero exit code
NONZERO_EXITCODE = 120

## METHODS
# augments parameters in feb file
def augment_feb(feb_file, elm_path, new_val, new_file = None):

    # doc_string
    """
    augment_feb(feb_file, elm_path, new_val, new_file = None)

    Replaces element value in '.feb' file with new value.

    Parameters
    ----------
    feb_file: string
        path to '.feb.' file (xml format) used as input to febio4
    elm_path : string
        path to element (in XPath format) which should be replaced
    new_val : string
        new value which should replace previous element value
    new_file : string, optional
        path to new file to write xml file to, rather than overwriting old file.

    Returns
    -------
    boolean
        return 'True' if operation was successful, otherwise return 'False'

    """

    # check that the file exists, open as element tree
    if not os.path.exists(feb_file):
        print("ERROR :: augment_feb :: 'feb_file' ({}) could not be found.".format(feb_file))
        return False
    tree = ET.parse(feb_file)
    root = tree.getroot()

    # find the element corresponding to the XPath
    elm = root.findall(elm_path)
    if elm is None or (isinstance(elm, list) and len(elm) == 0):
        # no elements were found
        print("ERROR :: augment_feb :: {} ({}) does not contain element '{}'.".format(root.tag, feb_file, elm_path))
        return False
    elif isinstance(elm, list) and len(elm) > 1:
        # more than one element was found
        print("ERROR :: augment_feb :: {} ({}) contains multiple elements '{}':".format(root.tag, feb_file, elm_path))
        for e in elm:
            print("\t", e.tag, e.attrib)
        return False
    else:
        # only one option exists
        # remove the old element from the tree
        # print(type(elm))
        # for e in root.findall(elm_path):
        #     print(type(e))
        #     root.remove(e)

        # update the value, add to root
        for e in elm:
            e.text = new_val
            # root.append(e)

        # write to file
        if new_file is None:
            new_file = feb_file
        tree.write(new_file, encoding='ISO-8859-1', xml_declaration=True)


    # update file


## SCRIPT
# open feb file via xml
if __name__ == '__main__':
    ## ARGUMENTS
    # first argument: '.feb' file to parse
    feb_file = sys.argv[1]
    # second argument: path to element in xml tree, in XPath format
    elm_path = sys.argv[2]
    # third argument: new value to assign to element specified by XPath
    new_val = sys.argv[3]
    # run script
    augment_feb(feb_file, elm_path, new_val)


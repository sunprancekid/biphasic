
## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfaces
## 2025.10.16

## FILE: programs/bash/febio/augment_feb_batch.py
## PURPOSE: generate simulation files associated with parameterized jobs

## MODULES
# conda / python native
import sys, os
import pandas as pd
import xml.etree.ElementTree as ET

## PARAMETERS
# nonzero exit code
nonzero_exitcode = 120
# file name
filename = "programs/bash/febio/augment_feb_batch.py"

## METHODS
# generate and augment single feb file associated with integer
def augment_feb_single (feb, path, job, simint):

    # check that the parameter and configuation file exist
    parm_file = "{:s}{:s}/{:s}.parm.csv".format(path,job,job)
    config_file = "{:s}{:s}/{:s}.config.csv".format(path,job,job)
    if not os.path.exists(parm_file):
        print("\nERROR :: {:s} :: unable to find job parameter file '{:s}'.\n".format(filename, parm_file))
        exit(nonzero_exitcode)
    if not os.path.exists(config_file):
        print("\nERROR :: {:s} :: unable to find job configuration file '{:s}'.\n".format(filename, config_file))
        exit(nonzero_exitcode)
    if not os.path.exists(feb):
        # the feb file does not exist
        print("\nERROR :: {:s} :: unable to file FEB FILE '{:s}'.".format(filename, feb))
        exit(nonzero_exitcode)

    # open the parm and config files
    df_parm = pd.read_csv(parm_file)
    df_config = pd.read_csv(config_file)

    # find the id associated with a job
    df_gen = df_parm.loc[df_parm['n'] == simint]
    if len(df_gen.index) == 0:
        print("\nERROR :: {:s} :: no jobs exists within PARM FILE '{:s}' with integer '{:n}'".format(filename, parm_file, simint))
        exit(nonzero_exitcode)
    elif len(df_gen.index) >= 2:
        print("\nERROR :: {:s} :: multiple jobs exist within PARM FILE '{:s} with integer '{:n}'".format(filename, parm_file, simint))
        exit(nonzero_exitcode)

    # parse information from parameter file, config file
    # open the feb file
    # print("opening feb files")
    tree = ET.parse(feb_file)
    root = tree.getroot()
    # parse each path way from the config file, check that it exists
    for idx, row in df_config.iterrows():
        elm_path = row['xml']

        # check if the xml path is na
        if elm_path == 'na':
            # skip augmenting this value in the feb file
            continue

        # otherwise, find the xml path in the tree
        elm = root.findall(elm_path)
        if elm is None or (isinstance(elm, list) and len(elm) == 0):
            print("ERROR :: {:s} :: UNABLE  to find ELEMENT '{:s}' in FEB FILE '{:s}'".format(filename, elm_path, feb))
        elif isinstance(elm, list) and len(elm) > 1:
            # more than one element was found
            print("ERROR :: {:s} :: FEB FILE '{:s}' contains multiple ELEMENTS '{:s}'.".format(filename, feb_file, elm_path))
        else:
            # check the relationship
            # print ("KEY '{:s}' exists in FEB '{:s}' as ELEMENT '{:s}'".format(row['key'], feb, elm_path))
            if row['related'] == 0:
                # the new value is independent of other values
                # update the value in the tree
                # print(" - KEY '{:s}' in JOB '{:s}' is INDEPENDENT of other values.".format(row['key'], job))
                for e in elm:
                    e.text = str(df_gen.iloc[0][row['key']])
            else:
                # the new value is dependent on other values
                # determine which ones
                # print(" - KEY '{:s}' in JOB '{:s}' is DEPENDENT on other values.".format(row['key'], job))
                key_jdx_list = []
                relationship = df_gen.iloc[0][row['key']]
                # print("BEFORE: {:s}".format(relationship))
                for jdx, row2 in df_config.iterrows():
                    # skip line if self
                    if jdx == idx: continue
                    # determine if the row corresponds to a value in the value
                    if row2['key'] in df_gen.iloc[0][row['key']]:
                        # print(row2['key'])
                        relationship = relationship.replace(row2['key'],"{:.2f}".format(df_gen.iloc[0][row2['key']]))

                # check if the relationship should be evaluated (i.e. is not symbolic), or should be left as is
                if row['symbolic'] == 0:
                    # if the relationship is not symbolic, evaluate it
                    relationship = eval(relationship)
                    # print(relationship)

                # print("AFTER: {:s}".format(relationship)) 
                for e in elm:
                    e.text = str(relationship)

    # make the simulation subdirectory
    simdir=df_gen.iloc[0]['path']
    simdir="{:s}{:s}/{:s}".format(path, job, simdir)
    if not os.path.exists(simdir):
        # if the simulation path does not exist, make the directory
        os.makedirs(simdir)
    # write to file
    tree.write("{:s}{:s}/{:s}{:s}.feb".format(path, job, df_gen.iloc[0]['path'], df_gen.iloc[0]['id']), encoding='ISO-8859-1', xml_declaration=True)
    # with open("{:s}{:s}/{:s}{:s}.feb".format(path, job, df_gen.iloc[0]['path'], df_gen.iloc[0]['id']), 'w') as f:
    #     print("{:s}{:s}/{:s}{:s}.feb".format(path, job, df_gen.iloc[0]['path'], df_gen.iloc[0]['id']))
    #     tree.write(f, encoding='ISO-8859-1', xml_declaration=True)


# generate and augment feb files en masse
def augment_feb_batch (feb, path, job):

    # check that the parameter and configuation file exist
    parm_file = "{:s}{:s}/{:s}.parm.csv".format(path,job,job)
    config_file = "{:s}{:s}/{:s}.config.csv".format(path,job,job)
    if not os.path.exists(parm_file):
        print("\nERROR :: {:s} :: unable to find job parameter file '{:s}'.\n".format(filename, parm_file))
        exit(nonzero_exitcode)
    if not os.path.exists(config_file):
        print("\nERROR :: {:s} :: unable to find job configuration file '{:s}'.\n".format(filename, config_file))
        exit(nonzero_exitcode)

    # open the parm and config files
    df_parm = pd.read_csv(parm_file)
    df_config = pd.read_csv(config_file)

    print ("\nTODO :: {:s} :: implement batch feb augmentation.".format(filename))



## SCRIPT
# open parameter file
if __name__ == '__main__':

    ## ARGUMENTS
    # first argument: vanilla feb file
    feb_file = sys.argv[1]
    # second argument: path to simulation directory
    path = sys.argv[2]
    # third argument: job name
    job = sys.argv[3]
    # fourth argument: integer indicated specific job to generate (if 0, generate all)
    simint = int(sys.argv[4])

    if simint == 0:
        augment_feb_batch (feb_file, path, job)
    else:
        augment_feb_single (feb_file, path, job, simint)


## Matthew A. Dorsey
## @mad-mpikg
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institute for Colloids and Interfacial Sciences
## the purpose of this program is to handle io surrounding with febio programs

## PACKAGES
# from python / conda
import sys, os, math
import pandas as pd
import numpy as np 
# local / custom
# none

## PARAMETERS
# boolean that prints debugging statements
DEBUG = False
# nonzero exit code for faulty method execution
nonzero_exitcode = 120
# default name for saving files
default_savefile = "febio4.out.csv"
# default name for saving files
default_savefile_opt = "febio4.opt.csv"

## METHODS
# from d (directory), f (file), and s (save file), return the directory and file name
def parse_io (d = None, f = None, s = None):

	## debugging statement
	if DEBUG:
		print("parse_io")

	## check that the correct information was passed to the method
	# check that a file name was specified
	if f is None:
		# if not, report an error
		print(" ERROR :: parse_febio_out :: filename ('f') must be specified. ")
		exit(nonzero_exitcode)

	# check if the file exists
	if d is None:
		# if the directory was not specified by user
		# check if the file exists
		if not os.path.exists(f):
			# if the file does not exist, report an error to the user
			print(" ERROR :: parse_febio_out :: directory ('d') was not specified and filename {} does not exist in local directory.".format(f))
			exit(nonzero_exitcode)
		else:
			# the file does exist
			# seperate the directory from the file name
			temp = f.split("/")
			d = ""
			f = temp[-1]
			for i in range(len(temp) - 1):
				d += "{}/".format(temp[i])

	elif not os.path.exists(d + f):
		# the directory and the file were supplied seperately by the user but the path does not exist
		print(" ERROR :: parse_febio_out :: path {}{} does not exist.".format(d, f))
		exit(nonzero_exitcode)

	return d, f, s

def parse_element_data (f = None, elm = None, prop = None):
	""" open '.dat' file, return element data stored within. 

	## TODO :: add option to specify delimiter
	
	Arguments:
	----------
	f : str
		path to '.dat' file
	elm : List[int] (optional)
		specific list of elements to extract data for
	prop : List[str] (optional)
		specified set of properties to extract data for

	Returns:
	--------
	Dict[DataFrame]
		dictionary containing element data over time, where
		keys correspond to each property.
	"""
	## check method arguments
	# check that the file exists
	if not os.path.exists(f):
		print("ERROR :: get_element_data() :: file 'f' ({0}) does not exist or cannot be found.".format(f))
		return None
	
	# check the 'prop' is a string or a list of strings
	if  isinstance(prop, list):
		# prop is a list
		# parse through each item in the list 
		for i in range(len(prop) - 1, -1, -1):
			# transverse the list in reverse order
			if not isinstance(prop[i], str):
				# the property should be a string, drop it
				print("ERROR :: get_element_data() :: property '{0}' in argument list 'prop' must be type 'str'.".format(prop.pop(i)))
		# check that there are still items in the list
		if len(prop) == 0:
			print("ERROR :: get_element_data() :: method argument 'prop' is empty.")
			return None
	elif isinstance(prop, str):
		# prop is a string, store it as a list
		prop = [prop]
	elif prop is not None:
		# prop was specified but is neither a list not a string
		# report an error
		print("ERROR :: get_element_data() :: method argument 'prop' must be either of type 'list' or 'str', or left unspecified.")
		return None
	
	# check that 'elm' is a list of integers
	if isinstance(elm, list):
		# elm is a list
		# parse through each item in the list
		for i in range(len(elm) - 1, -1, -1):
			# transverse the list in reverse order
			if not isinstance(elm[i], int):
				# the elmement should be stored as an integer, drop it
				print("ERROR :: get_element_data() :: element number {0} in argument list 'elm' ({1}) must be of type 'int', removing.".format(i, elm.pop(i)))
		# check that there are still items in the list
		if len(elm) == 0:
			print("ERROR :: get_element_data() :: method argument 'elm' is empty.")
			return None
	elif isinstance(elm, int):
		# elm is a integer
		# reformat as a list of integers
		elm = [elm]
	elif elm is not None:
		# 'elm' was specified but is neither a list nor an integer
		print("ERROR :: get_element_data() :: method argument 'elm' must be either of type 'list' or 'int', or left unspecified.")
		return None

	## open the file, parse data stored within file to initialize data_dict
	data_dict = {} # empty dictionary which contains property / element data
	with open (f, 'r') as f_io:
		## skip the first two lines
		# the first line is the step number
		f_io.readline()
		# the second line is the current time
		f_io.readline()

		## check the properties stored in the file
		# the third line is the properties
		l = f_io.readline()
		l = l[9:].strip('\n') # drop the first 9 characters, newline character
		p = l.split(';')
		# use the existing properties to initialize the data dictionary
		if prop is not None:
			# if properties were specified in the arguments
			for i in range(len(prop) - 1, -1, -1):
				if prop[i] not in p:
					# the requested property does not exist, remove it from the list
					print("ERROR :: get_element_data() :: property '{0}' was not written to '{1}'.".format(prop.pop(i), f))
			# check that there are still items in the property dictionary
			if len(prop) != 0:
				# initialize the data dictionary using the specified dictionary
				for i in prop:
					data_dict.update({i: None}) # initialize with empty object
			else:
				# all of the properties were removed from the argument list
				# return None with error
				print("ERROR :: get_element_data() :: unable to return requested data.")
				return None
		else:
			# property list was not specified by the user
			# use the properties stored in the file to initialize the data dictionary
			for i in p:
				# initialize with an empty object
				data_dict.update({i: None})
			# store prop as p
			prop = p

		## check the elements store in the file
		# get elements from file
		e = [] # empty list of elements stored in file
		while True:
			l = f_io.readline()
			if len(l.split(' ')) > 1:
				# if the line contains spaces, then element data has ended
				break
			# parse  the element number from the line
			e.append(int(l.split(',')[0]))
		# initialize data_dict with DataFrame for each object
		if elm is not None:
			# if a list of elements were specified
			# check that the elements
			for i in range(len(elm) - 1, -1, -1):
				# traverse the list in reverse order
				if elm[i] not in e:
					# the specified element does not exist in the file
					print("ERROR :: get_element_data() :: elmement '{0}' in 'elm' does not exist.".format(elm.pop(i)))
			if len(elm) == 0:
				# if the list is empty, return nothing
				print("ERROR :: get_element_data() :: unable to return the requested data.")
				return None
			else:
				# use the specified list to initialize the data frame
				for i in list(data_dict.keys()):
					data_dict[i] = pd.DataFrame(columns = ['Step', 'Time'] + elm)
		else:
			# elements were not specified by the user
			# initialize the property data frames with all elements in the file
			for i in list(data_dict.keys()):
				data_dict[i] = pd.DataFrame(columns = ['Step', 'Time'] + e)
			# store e in elm
			elm = e
		# close the file
		f_io.close()

	## restart reading the file, store data in dict
	with open(f, 'r') as f_io:
		# initialize the number of steps
		n_step = 0
		count = 0
		# loop through each line
		while True:
			l = f_io.readline()
			# check for the end of the file
			if not l:
				break

			if l == "*Step  = {0}\n".format(n_step) or l == "*Step  = 1\n":
				# increment the step
				count += 1
				n_step += 1
				if l == "*Step  = 1\n":
					n_step = 2
				# the next line is the simulation time
				l = f_io.readline().strip('\n').split(' ')
				# the third line contains the data specification, skip
				f_io.readline()
				# initialize the property dictionary with the 
				for i in list(data_dict.keys()):
					data_dict[i].loc[len(data_dict[i])] = [count - 1, l[3]] + [np.nan for j in range(len(elm))]
			else:
				# the line is a piece of element data
				# determine the element
				l = l.split(',')
				h = int(l[0])
				if h in elm:
					# the element is in the list data to get
					for i in list(data_dict.keys()):
						# get the list of properties to get
						j = p.index(i) # index corresponding to property in file
						k = elm.index(h) # index corresponding to elm in df column
						data_dict[i].loc[len(data_dict[i]) - 1, h] = float(l[1 + j])
	return data_dict


def extract_febio_opt (d = None, f = None, s = None):
	""" extract results from febio optimization routine.

	Arguments:
	----------
	d : str
		directory which contains febio optimization log file
	f : str
		name of log file in directory ('d')
	s : str
		name of file to save results as in directory ('d')

	Returns:
	--------
	bool
		'True' if loading and saving was successful, else 'False'.
	"""
	# check that the loading file exists
	if not os.path.exists(d + f): return False
	# check that the paths and filenames are correct
	d, f, s = parse_io (d, f, s)
	# if the savefile name is still none, use the default
	if s is None:
		s = default_savefile_opt

	## open optimization log file, parse information
	with open(d + f, 'r') as f_io:
		# initialize delimitting parameters
		n_it = 1 # number of iterations that have been completed
		n_opt_parm = 0 # number of parameters which were optimized
		opt_parm = [] # contains the variables used for the optimized parameters
		opt_val = [[] for i in range(1)] # contains the values used for the
		has_opt_parameters = False # the optimizable parameters have been determined
		n_data = 0
		has_n_data = False # the number of optimized data points have been determined
		obj_val = []
		reg_coeff = []
		has_final = False # a final, optimal value has been determined

		# loop through all lines in optimization file
		while True:

			# get the next line
			l = f_io.readline()
			# if the line is empty, the end of the file has been reached
			if not l:
				break
			l = l.strip() # remove newline character

			# check if the line matches iteration format
			# n_it += 1
			if l == "----- Iteration: {0} -----".format(n_it):

				## PARAMETER ADJUSTMENT VALUES
				# get the next line
				l = f_io.readline().strip()
				# get optimized parameter values
				if not has_opt_parameters:
					# get the parameters which were optimized
					while 'fem' in l:
						n_opt_parm += 1
						opt_parm.append(l.split(" ")[0].split(".")[-1] + "_opt")
						opt_val[0].append(float(l.split(" ")[2]))
						# go to the next line
						l = f_io.readline().strip()
					# the optimization parameters have been parsed
					has_opt_parameters = True
				else:
					opt_val.append([])
					for i in range(n_opt_parm):
						opt_val[n_it - 1].append(float(l.split(" ")[2]))
						# go to the next line
						l = f_io.readline().strip()
						print(l)

				## OPTIMIZATION DATA
				if not has_n_data:
					# if the optimization data has not been parsed yet
					# skip through the data while also counting the number of data points
					while "objective" not in l:
						n_data += 1
						l = f_io.readline().strip()
						print(l)
					# the end of the data points have been reached
					has_n_data = True
				else:
					# skip through the optimization data point without counting them
					for i in range(n_data):
						l = f_io.readline().strip()
						print(l)

				# SCORING
				# get the objective value
				obj_val.append(float(l.split(" ")[2]))
				l = f_io.readline()
				# get the regression coefficient
				reg_coeff.append(float(l.split(" ")[2]))

				# iterate iterations
				n_it += 1
			elif l == "P A R A M E T E R   O P T I M I Z A T I O N   R E S U L T S":
				# end of the optimization with the final results
				# skip lines until the results
				while "objective" not in l:
					l = f_io.readline().strip()

				# the final objective value
				obj_val.append(float(l.split(" ")[-1]))
				l = f_io.readline().strip()
				l = f_io.readline().strip()

				# the final regression coefficient
				reg_coeff.append(float(l.split(" ")[-1]))
				l = f_io.readline().strip()
				l = f_io.readline().strip()
				l = f_io.readline().strip()
				l = f_io.readline().strip()

				# get the optimzed values
				opt_val.append([])
				for i in range(n_opt_parm):
					opt_val[n_it - 1].append(float(l.split(" ")[2]))
					l = f_io.readline().strip()

				has_final = True

	# done with file, save data
	## write io to formatted file within same directory
	# write the out information
	if s is None:
		# overwrite the file, if none has been previded
		s = f

	with open(d + s, 'w') as s_io:
		header = "n"
		for i in range(n_opt_parm):
			header += ",{0}".format(opt_parm[i])
		header += ",obj_val,reg_coeff"
		s_io.writelines(header + "\n")
		for i in range(len(opt_val) - 1):
			line = "{0}".format(i + 1)
			for j in range(len(opt_val[i])):
				line += ",{0}".format(opt_val[i][j])
			line += ",{0}".format(obj_val[i])
			line += ",{0}".format(reg_coeff[i])
			s_io.writelines(line + "\n")
		# add the final values, if requested
		if has_final:
			final = "f"
			for i in range(len(opt_val[n_it - 1])):
				final += ",{0}".format(opt_val[n_it - 1][i])
			final += ",{0}".format(obj_val[-1])
			final += ",{0}".format(reg_coeff[-1])
			s_io.writelines(final + "\n")

	return True


# parse custom output from febio simulations, save to file
def extract_febio_out (d = None, f = None, s = None):
	
	## debugging statement
	if DEBUG:
		print("extract_febio_out")

	## check that the correct information was passed to the method
	d, f, s = parse_io (d, f, s)
	# if the save file is still none, give a name
	if s == None:
		s = default_savefile

	## open file, parse information
	with open(d + f, 'r') as f_io:

		# initialize io collection
		n_step = 0 # count the number of data points collected
		n_total = 0
		has_header = False # boolean determining if header has been parsed
		has_end = False # boolean determining if the end of the simulation was reached
		header = None # contains header, once parsed
		time = [] # array contianing increments
		data = []

		while True:

			# loop through file until the end
			l = f_io.readline()
			# check for the end of the file
			if not l:
				break
			l = l.strip()

			# if the line matched for the format for the data entry
			if l == "Data Record #1":
				# next line is filler
				f_io.readline()

				# next line contains the number of steps
				f_io.readline()
					
				# parse the time
				l = f_io.readline().strip() # remove leading and trailing spaces
				l = l.split(" ") # split line into array seperated by spaces
				time.append(l[2])

				# if n is 0 / has_header is false, parse the header
				l = f_io.readline().strip()
				if not has_header:
					l = l.split(" ")
					header = l[2]
					header = header.replace(";", ",")
					has_header = True
					# print("n,t,{}".format(header))

				# get the data
				l = f_io.readline().strip()
				# data.append(l)
				temp = l.split(" ")
				data.append("")
				# remove the first line
				for i in range(1, len(temp)):
					data[-1] += ",{}".format(temp[i])
				# print("{},{}{}".format(n,time[-1],data[-1]))
				n_step += 1
				n_total += 1
			elif "N O N L I N E A R   I T E R A T I O N   S U M M A R Y" in l:
				# end of the simulation
				# parse the final statistics

				# number of time steps completed
				f_io.readline() # skip the filler line
				l = f_io.readline().strip() # parse the line from the file
				l = l.split(" ") # break into an array
				n_steps = l[7] # the eigth string has the number of steps

				# total number of equilibrium iterations
				f_io.readline()
				l = f_io.readline().strip()
				l = l.split(" ")
				n_equil_it = l[7]

				# total number of right hand evaluations
				f_io.readline() # skip the filler line
				l = f_io.readline().strip()
				l = l.split(" ")
				n_rh_eval = l[7]

				# total number of stiffness reformations
				f_io.readline() # skip the filler line
				l = f_io.readline().strip()
				l = l.split(" ")
				n_stiff_ref = l[7]

				# time in linear solver
				f_io.readline() # skip the filler line
				l = f_io.readline().strip()
				l = l.split(" ")
				time_linear = l[4]

				# elapsed time
				f_io.readline() # skip the filler line
				f_io.readline() # skip the filler line
				l = f_io.readline().strip()
				l = l.split(" ")
				time_total = l[3]

				# if this point was reached, the simulation ended properly
				has_end = True

	## write io to formatted file within same directory
	# write the out information
	if s is None:
		# overwrite the file, if none has been previded
		s = f

	with open(d + s, 'w') as s_io:
		s_io.writelines("n,t,{}\n".format(header))
		for i in range(len(time)):
			s_io.writelines("{},{}{}\n".format(i,time[i],data[i]))

	# write the cpu information
	with open(d + 'febio.cpu.csv', 'w') as s_io:
		s_io.writelines("steps,time_linear,time_total\n")
		if has_end:
			# if the end was reached, write the job performance
			s_io.writelines("{},{},{}\n".format(n_steps, time_linear, time_total))
		else:
			# write 'na' to indicate that the end of the job was not reached
			s_io.writelines("na,na,na\n".format(n_steps, time_linear, time_total))

# calculate material displacement
def calculate_force (d = None, f = None, s = None, z = False, y = False, x = False):
	
	## debugging statement
	if DEBUG:
		print("calculate_force")

	## parse the load file, save file
	d, f, s = parse_io(d, f, s)
	# if the save file is not specified, use the default
	if s == None:
		s = default_savefile

	## open the file, check the header
	df = pd.read_csv(d + f)
	z = z and 'Fz' in df.columns
	y = y and 'Fy' in df.columns
	x = x and 'Fx' in df.columns
	if not z and not y and not x:
		## error
		print("ERROR :: calculate_force :: not enough information has been specified to exctract displacement from '{}'".format(d + s))
		return None, None, None

	# for each line, calculate the displacement
	force_mag = []
	for index, r in df.iterrows():
		temp = 0.
		if z: temp += math.pow(r['Fz'],2)
		if y: temp += math.pow(r['Fy'],2)
		if x: temp += math.pow(r['Fx'],2)
		force_mag.append(math.sqrt(temp))

	# add the new column to the file and save
	df['F_mag'] = force_mag
	df.to_csv(d + s, index = False)

# calculate force magnitude
def calculate_displacement	(d = None, f = None, s = None, x = False, y = False, z = False):
	
	## debugging statement
	if DEBUG:
		print("calculate_displacement")

	## parse the load, save file
	d, f, s = parse_io (d, f, s)
	# if the save file is not specified, use the default
	if s == None:
		s = default_savefile

	## open the file, check the header
	df = pd.read_csv(d + f)
	z = z and 'z' in df.columns
	y = y and 'y' in df.columns
	x = x and 'x' in df.columns
	if not z and not y and not x:
		## error
		print("ERROR :: calculate_displacement :: not enough information has been specified to extract displacement from '{}'".format(d + f))
		return None, None, None
	elif sum([z, y, x]) > 1:
		## error
		print("ERROR :: calculate_displacement :: algorithm not implemented for more than one dimension.")
		print("TODO  :: calculate_displacement :: write displacement algorithm for multiple dimensions.")
		return None, None, None

	# for each line, determine the distance traveled from the first line
	disp = []
	for i, r in df.iterrows():
		temp = 0.
		if z: temp += r['z']
		if y: temp += r['y']
		if x: temp += r['x']
		if i == 0: disp.append(temp)
		else: disp.append(temp - disp[0])
		## NOTE :: this algorthim may need refinement for more than two dimensions and the definition for displacement might be highly user dependent
		## TODO :: replace displacement calculation with path integral

	# add new column and save file
	df['disp'] = disp
	df.to_csv(d + s, index = False)

# calculate hysteresis from force and displacement
def calculate_work (d = None, f = None, s = None, f_col = None, v_col = None, x_col = None, t_col = None):
	
	## debugging statement
	if DEBUG:
		print("calculate_work")

	## parse the load, save file
	d, f, s = parse_io (d, f, s)
	# if the save file is not specified, use the default
	if s == None:
		s = default_savefile

	## open the file, check the headers
	df = pd.read_csv(d + f)
	has_f = f_col in df.columns
	has_v = v_col in df.columns
	has_x = x_col in df.columns
	has_t = t_col in df.columns
	calc_fxdx = has_f and has_x # to calculate work from force, both force and position must be specified
	calc_fvdt = has_f and has_v and has_t # to calculate work from force and velocity, force, velocity, and time must be specified
	if not calc_fvdt and not calc_fxdx:
		# not enough informaiton was specified to calculate work
		print("ERROR :: calculate_work :: not enough information was specified in order to calculate work from '{}'".format(d + f))
		return

	## calculate work
	if calc_fvdt:
		dw = [0.] # first line corresponds to no work being done
		for i, r1 in df.iterrows():
			if i != 0:
				# skip the calculation for the first entry
				dw.append(0.5 * (r1[f_col] * r1[v_col] + r0[f_col] * r0[v_col]) * (r1[t_col] - r0[t_col]))
			r0 = r1 # save the current row for the next calculation
		# append the work calculation to the data frame
		df['dw_fvdt'] = dw

	if calc_fxdx:
		dw = [0.]
		for i, r1 in df.iterrows():
			if i != 0:
				# skip the calculation for the first entry
				dw.append(0.5 * (r1[f_col] + r0[f_col]) * (r1[x_col] - r0[x_col]))
			r0 = r1 # save the current row for the next calculation
		# append the work calculation to the data frame
		df['dw_fdx'] = dw

	## save the dataframe
	df.to_csv(d + s, index = False)

if __name__ == '__main__':
	## ARGUMENTS
	# first argument: path to directory that contains the file
	d = sys.argv[1]
	# second argument: file that contains output from simulation
	f = sys.argv[2]

	## SCRIPT / MAIN
	# call parse method
	extract_febio_out(d = d, f = f)
	# calculate velocity
	# TODO :: calculate velocity magnitude
	# calculate displacement
	calculate_displacement (d = d, f = default_savefile, z = True)
	# calculate force magnitude
	calculate_force (d = d, f = default_savefile, z = True, y = True, x = True)
	# calculate work
	calculate_work(d = d, f = default_savefile, x_col = 'z', v_col = 'vz', f_col = 'Fz', t_col = 't')

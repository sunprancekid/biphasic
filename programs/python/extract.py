
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
# nonzero exit code for faulty method execution
nonzero_exitcode = 120
# default name for saving files
default_savefile = "febio4.out.csv"

## METHODS
# from d (directory), f (file), and s (save file), return the directory and file name
def parse_io (d = None, f = None, s = None):

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

# parse custom output from febio simulations, save to file
def extract_febio_out (d = None, f = None, s = None):

	## check that the correct information was passed to the method
	d, f, s = parse_io (d, f, s)
	# if the save file is still none, give a name
	if s == None:
		s = default_savefile

	## open file, parse information
	with open(d + f, 'r') as f_io:

		# initialize io collection
		n = 0 # count the number of data points collected
		has_header = False # boolean determining if header has been parsed
		header = None # contains header, once parsed
		time = [] # array contianing increments
		data = []

		while True:

			# loop through file until the end
			l = f_io.readline()
			if not l:
				break
			l = l.strip()

			# if the line matched for the format for the data entry
			if l == "Step = {}".format(n):
				# parse the time
				l = f_io.readline().strip()
				l = l.split(" ")
				time.append(l[2])

				# if n is 0 / has_header is false, parse the header
				l = f_io.readline().strip()
				if not has_header:
					l = l.split(" ")
					header = l[2]
					header = header.replace(";", ",")
					has_header = True
					print("n,t,{}".format(header))

				# get the data
				l = f_io.readline().strip()
				# data.append(l)
				temp = l.split(" ")
				data.append("")
				# remove the first line
				for i in range(1, len(temp)):
					data[-1] += ",{}".format(temp[i])
				print("{},{}{}".format(n,time[-1],data[-1]))
				n += 1

	## write io to formatted file within same directory
	if s is None:
		# overwrite the file, if none has been previded
		s = f

	with open(d + s, 'w') as s_io:
		s_io.writelines("n,t,{}\n".format(header))
		for i in range(len(time)):
			s_io.writelines("{},{}{}\n".format(i,time[i],data[i]))

# calculate material displacement
def calculate_displacement (d = None, f = None, s = None, z = False, y = False, x = False):

	## parse the load file, save file
	d, f, s = parse_io(d, f, s)
	# if the save file is not specified, use the default
	if s == None:
		s = default_savefile

	## open the file, check the header
	df = pd.read_csv(d + s)
	z = z and 'Fz' in df.columns
	y = y and 'Fy' in df.columns
	x = x and 'Fx' in df.columns
	if not z and not y and not x:
		## error
		print("ERROR :: calculate_displacement :: not information has been specified to exctract displacement from '{}'".format(d + s))
		exit(nonzero_exitcode)

	# for each line, calculate the displacement
	disp = []
	for index, r in df.iterrows():
		temp = 0.
		if z: temp += math.pow(r['Fz'],2)
		if y: temp += math.pow(r['Fy'],2)
		if x: temp += math.pow(r['Fx'],2)
		disp.append(math.sqrt(temp))

	# add the new column to the file and save
	df['F_mag'] = disp
	df.to_csv(d + s, index = False)


# calculate force magnitude
def calculate_force	(d = None, f = None, s = None):
	pass

# calculate hysteresis from force and displacement
def calculate_work (d = None, f = None, s = None, fdx = False, fvdt = False):
	pass

## ARGUMENTS
# first argument: path to directory that contains the file
d = sys.argv[1]
# second argument: file that contains output from simulation
f = sys.argv[2]

## SCRIPT / MAIN
# call parse method
extract_febio_out(d = d, f = f)
# calculate displacement
calculate_displacement (d = d, f = default_savefile, z = True, y = False, x = False)
# calculate velocity
# calculate force
calculate_force(f = f, s = default_savefile)
# calculate work - F(x)dx
calculate_work(f = f, s = default_savefile, fdx = True)
# calculate work - F(t)v(t)dt
calculate_work(f = f, s = default_savefile, fvdt = True)

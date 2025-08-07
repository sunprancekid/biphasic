
## Matthew A. Dorsey
## @sunprancekid
## matthew.dorsey@mpikg.mpg.de
## Max Planck Institut for Colloids and Interfacial Sciences
## the purpose of this program is to io surrounding with febio programs

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

## METHODS
# parse custom output from febio simulations
def extract_febio_out (d = None, f = None, s = None):

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
				temp = l.split(",")
				data.append("")
				# remove the first line
				for i in range(1, len(temp)):
					data[-1] += "{},".format(temp[i])
				print("{},{},{}".format(n,time[-1],data[-1]))
				n += 1

	## write io to formatted file within same directory
	if s is None:
		# overwrite the file, if none has been previded
		s = f

	with open(d + s, 'w') as s_io:
		s_io.writelines("n,t,{}\n".format(header))
		for i in range(len(time)):
			s_io.writelines("{},{},{}\n".format(i,time[i],data[i]))

## ARGUMENTS
# first argument: path to file
f = sys.argv[1]
# second argument: save name
s = sys.argv[2]

## SCRIPT / MAIN
# call parse method
extrat_febio_out(f = f, s = s)
# calculate displacement
# calculate velocity
# calculate force
# calculate work - F(x)dx
# calculate work - F(t)v(t)dt

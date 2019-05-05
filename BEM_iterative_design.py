import math
import csv
import numpy as np 
import matplotlib.pyplot as plt

v0=8		#free stream velocity
w=30		#rotation of blades in rpm
r=11		#radius of section in question
theta = 4.5	#twist in degrees
B=3			#number of blades
c=1.2		#chord length

a=0			#Initial guess for axial induction factor
adash=0		#Initial guess for angular induction factor

increment = 0.001	#increment for a and adash

w = 30 * 2 * math.pi / 60	#convert rpm to rad/s
theta = theta * math.pi / 180
sigma = c*B/(2*math.pi*r)

coefficient_storage = [] #storing CN and CT for later use

def csv_to_list():
	outputdata = [[],[],[]] # alpha, Cl, Cd

	with open('data.csv', 'r') as csvFile:
	    reader = csv.reader(csvFile)
	    for i, row in enumerate(reader):
	        if i > 82:
		        for j in range(0, 3):
		        	outputdata[j].append(float(row[j]))

	csvFile.close()
	return outputdata

def find_coefficients(alpha, data):
	diff = 100
	index = 0
	interpoloation = 0 
	for i, value in enumerate(data[0]):
		if abs(alpha-value) < diff:
			diff = abs(alpha-value)
			index = i

	if alpha - data[0][index] < 0:
		index -= 1
	try:
		interpoloation = round((alpha - data[0][index])/(data[0][index+1]-data[0][index]), 3)
	except:
		print("index out of range while trying to perform linear interpoloation")

	Coefficients = []
	for i in range (1, 3):
		Coefficients.append(round(data[i][index] + (data[i][index+1] - data[i][index]) * interpoloation , 6))

	return Coefficients


def find_new_alpha(old_alpha, data):
	a_axial		= old_alpha[0]
	a_angular	= old_alpha[1]

	phi = math.atan(v0*(1-a_axial)/(w*r))
	attack = (phi - theta) * (180/math.pi)	#angle of attack in degrees

	# Sanity check here
	assert attack < 15, "alpha too large, tweak threshold and increment"

	C = find_coefficients(attack, data)
	CN = C[0]*math.cos(phi)+C[1]*math.sin(phi)
	CT = C[0]*math.sin(phi)-C[1]*math.cos(phi)

	coefficient_storage.append((CN,CT))

	new_a_axial		= 1/(  ( (4*(math.sin(phi)**2))/(sigma*CN)) + 1)
	new_a_angular	= 1/(  ( (4*math.sin(phi)*math.cos(phi))/(sigma*CT)) - 1)

	return (new_a_axial, new_a_angular)

def get_relevant_values(alpha_info, lookup_info):

	axial_index = alpha_info[1].index(min(alpha_info[1]))
	angular_index = alpha_info[3].index(min(alpha_info[3]))

	axial_induction_factor   = alpha_info[0][axial_index]
	angular_induction_factor = alpha_info[2][axial_index]

	print("Axial induction factor, Angular induction factor:")
	print(axial_induction_factor, angular_induction_factor, "\n")

	General_Force = 0.5*1.2*c*(v0**2)
	Fn = coefficient_storage[axial_index][0] * General_Force
	Ft = coefficient_storage[angular_index][1] * General_Force

	print("Normal Force, Tangential Force:")
	print(Fn, Ft)


if __name__ == "__main__":
	lookup = csv_to_list()

	a_data = []
	a_error = []

	adash_data = []
	adash_error = []

	loopcap = int(0.8/increment)
	for i in range(0, loopcap):
		new_alpha = find_new_alpha([a, adash],lookup)

		a_data.append(a)
		a_error.append(abs(a-new_alpha[0]))

		adash_data.append(adash)
		adash_error.append(abs(adash-new_alpha[1]))

		#print(abs(a-new_alpha[0]), abs(adash-new_alpha[1]))
		a += increment
		adash += increment

	get_relevant_values([a_data,a_error,adash_data,adash_error], lookup)

	plt.plot(a_data, a_error, 'ro', markersize = 0.3)
	plt.plot(adash_data, adash_error, '+', markersize = 0.3)
	plt.show()
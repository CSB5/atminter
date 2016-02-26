#!/usr/bin/env python3
"""
initialize.py
	loads the pubdip or quetzacoatl .ini file
	returns a dictionary containing all terms
	Provides a set of easy readers for file initialization
"""

import csv

def execute(target):
	res = dict()
	with open(target) as f:
		for i in f:
			if i[0] == '#':
				continue
			temp = i.split('=')
			res[temp[0]] = temp[1].strip()
	return res

def readCSV(target):
	holder = []
	with open(target) as csvFile:
		reader = csv.reader(csvFile, delimiter = ',')
		for row in reader:
			holder.append(row)
	return holder



if __name__ == "__main__":
	path = "../quetzalcoatl.ini"
	ini = execute(path)
	bactNames = readCSV("../" + ini["BACTNAMES"])
	print (bactNames[1:5])


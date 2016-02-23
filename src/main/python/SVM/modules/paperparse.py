#!/usr/bin/env python3

"""
paperparse.py
	A set of functions to deal with pubcrawl data

"""

import nltk
import os
import re
import json

"""
getNames(filePath):
	input:
		pubcrawl json
	output: 
		names, shortened name and genus of all species in the file_name

	Sample pubcrawl output file:
		Escherichia_coli#Pseudomonas_aeruginosa.compiled
		Escherichia_coli#Pseudomonas_aeruginosa.sp

	Resultant getNames output:
		[['escherichia coli', 'e. coli', 'escherichia'], ['pseudomonas aeruginosa', 'p. aeruginosa', 'pseudomonas']]
"""


def getNames(filePath):
	def shorten(tup):
		return tup[0][0] + '. ' + tup[1]
	filePath = os.path.basename(filePath)
	name = os.path.splitext(filePath)[0]
	
	# print(name)
	name = [i.split('_') for i in name.split('#')]
	name = [[i.lower() for i in j] for j in name]

	#check if genus only
	# print(name)
	if len(name[0]) ==1:
			return [[i[0]] for i in name]

	return [[" ".join(i), shorten(i), i[0]] for i in name] 

"""
loadFile(filepath):
	generic file input. Takes in the file as raw data and returns a list of stripped and lowered lines.
"""

def loadFile(filePath):
	holder = []
	with open(filePath) as f:
		for i in f:
			holder.append(i.strip().lower())
	return holder

"""
tagStrip(line):
	removes the medline tag from the line

"""

def tagStrip(line):
	return line[6:]



"""""""""""""""""""""
#####################
#     .sp Files     #
#####################
"""""""""""""""""""""

"""
WARNING: OUTDATED. CURRENTLY KEPT TO PREVENT BREAKING


spFile():
	Class representation of a single .sp file. Contains the title, abstract, and their respective stemmed and tokenized forms

	loadSection(section):
		Loads a .sp section into split {TERM: DATA} dicitonaries.)
	
	readSpFile(spFIlePath):
		reads a SP file

	NOTE: Use as base class for all the other paper derivatives
	NOTE: For all future pubcrawl outputs, pmid is NECESSARY
"""
class spFile():

	#@profile
	def __init__(self, spFilePath, purge = False, reduced = False):
		self.file_name = os.path.basename(spFilePath)
		self.species_names = os.path.splitext(self.file_name)[0].replace("_", " ").split("#")
	
		loaded = self.readSpFile(spFilePath, reduced = reduced)
		#print(loaded)
		self.summary = self.loadSection(loaded["SUMMARY"])
		if reduced:
			return
		if purge:
			for i in self.summary:
				self.summary[i] = '0'
		papers = loaded['PAPERS'].split('\n\n')
		self.papers = [self.loadSection(i) for i in papers]
		#print(self.papers)
		if purge:
			for i in self.papers:
				if i == {}:
					continue
				i["TIHT"] = ''
				i["ABHT"] = ""
		self.papers = [i for i in self.papers if i != {}]




	#@profile
	def loadSection(self, section):
		#holder = [i.split("==") for i in section.split('\n') if i != '' and i != '\n']
		#HARDCODING 
		holder = []
		for i in section.split('\n'):
			if i == '' or i == '\n':
				continue
			holder.append((i[:4], i[6:].strip()))
		try:
			result = {i:j.strip() for i,j in holder}
		except ValueError:
			print("ERROR")
			print(holder)
			print(section)
			raise
		return result


	#@profile
	def readSpFile(self, spFilePath, reduced = False):
		if reduced ==True:
			total = ''
			with open(spFilePath) as f:
				while(f.readline()[0] != "@"):
					pass
				total+= f.readline()
				total+= f.readline()
				total+= f.readline()
			# print(total)
			return {"SUMMARY": total}

		holder = {}
		try:
			with open(spFilePath) as f:
				for i in f:
					#find the first section
					if i[0] == '#':
						continue
					if i[0] == '@':
						current = i[1:].strip()
						holder[current] = ''
					else:
						#account for empty lines
						if i == '':
							continue
						#this line is slow, fix it.
						holder[current] += i
		except:
			print("readSpFileError: ", spFilePath)
			raise
		return holder

	#reads the list of papers, converts them into paper tuples
	#@profile
	def loadPapers(self, rawAbstractList):
		holder = []
		res = []
		for i in rawAbstractList:
			if i[0] == ">":
				if holder == []:
					holder = [i[2:]]
				else:
					res.append(holder)
					holder = [i[2:]]
			else:
				holder.append(i)
		return res
	
	def writeSpFile(self, filePath):
		with open(filePath, 'w') as f:
			#handle the summary
			f.write("@SUMMARY\n")
			for i in self.summary:
				f.write('== '.join([i, self.summary[i]]) + '\n')
			f.write("@PAPERS\n")
			for paperDict in self.papers:
				f.write("== ".join(["PMID", paperDict["PMID"]]) + "\n")
				f.write("== ".join(["TI  ", paperDict["TI  "]]) + "\n")
				f.write("== ".join(["AB  ", paperDict["AB  "]]) + "\n")
				f.write("== ".join(["TIHT", paperDict["TIHT"]]) + "\n")
				f.write("== ".join(["ABHT", paperDict["ABHT"]]) + "\n\n")
	def writeSpFileHits(self, filePath):
		with open(filePath, 'w') as f:
			#handle the summary
			f.write("@SUMMARY\n")
			for i in self.summary:
				f.write('== '.join([i, self.summary[i]]) + '\n')
			f.write("@PAPERS\n")
			for paperDict in self.papers:
				if not (paperDict["TIHT"] or paperDict["ABHT"]):
					continue
				f.write("== ".join(["PMID", paperDict["PMID"]]) + "\n")
				f.write("== ".join(["TI  ", paperDict["TI  "]]) + "\n")
				f.write("== ".join(["AB  ", paperDict["AB  "]]) + "\n")
				f.write("== ".join(["TIHT", paperDict["TIHT"]]) + "\n")
				f.write("== ".join(["ABHT", paperDict["ABHT"]]) + "\n\n")
	def export(self):
		print("file_name: ", self.file_name)
		print("SUMMARY: ", self.summary)

#Updated spFile. Use in preference
SpFile_file_pattern = re.compile("\@(\w+)\n")
SpFile_term_pattern = re.compile(r"([\w ]*)==")

"""
SpFile:
	Fundamental storage file for all later processing
	input:
		path to a target json file output by pubcrawl/any minter module
	flags:
		purge
			removes all annotation data
		reduced
			removes all papers


"""

class SpFile():
	#@profile
	def __init__(self, file_path, purge = False, reduced = False):
		self.file_name = os.path.basename(file_path)
		self.species_names = os.path.splitext(self.file_name)[0].replace("_", " ").split("#")
		with open(file_path) as f:
			data = json.load(f)

		self.summary = {i:data["SUMMARY"][i]for i in data["SUMMARY"]}
		self.papers = [i for i in data["PAPERS"]]
		# handle the case of empty TIHT/ABHT
		#remove annotation data from papers if needed
		if purge:
			for i in self.papers:
				i["ABHT"] = []
				i["TIHT"] = []
		else:
			for i in self.papers:
				if not i["ABHT"]:
					i["ABHT"] = []
				if not i["TIHT"]:
					i["TIHT"] = []
				


	def writeSpFile(self, file_path):
		with open(file_path, 'w') as f:
			output = dict()
			output["SUMMARY"] = self.summary
			output["PAPERS"] = self.papers
			json.dump(output, f)
	def writeSpFileHits(self, file_path):
		output = dict()
		output["SUMMARY"] = self.summary
		output["PAPERS"] = []
		for paper in self.papers:
			if paper["TIHT"] or paper["ABHT"]:
				output["PAPERS"].append(paper)
		with open(file_path, "w") as f:
				json.dump(output, f)

	def export(self):
		print("file_name: ", self.file_name)
		print("SUMMARY: ", self.summary)

		

"""
loadSpFileDir(dirPath)
	input
		A path to a directory containing only .sp  Files
	returns
		A list of spFile objects for all spFiles
"""
def loadSpFileDir(dirPath, purge = False):
	files = os.listdir(dirPath)
	if dirPath[-1] != "/":
		dirPath += '/'
	files = [dirPath + i for i in files]
	return [spFile(i, purge = purge) for i in files]





if __name__ == "__main__":
	pass
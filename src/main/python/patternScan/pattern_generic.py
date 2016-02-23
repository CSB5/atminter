#!/usr/bin/env python3
from modules import sent_tokenize as st
from nltk.stem.snowball import SnowballStemmer
from modules import papers
from modules import modfile, initialize
import os
import re
from modules import paperparse as pp
import copy
import itertools


"""
pattern_generic.py
	Takes an abstract, identifies if any pattern exists based on pairwise permutations of a precompiled list of bacterial species

ALL PATTERNS USED

Activity A against B

containing A inhibited B

A decreased B

bacteriocins A inhibit B

A compete B

Antagonistic A on B

A antimicrobial B

A antibacterial B

A antagonistic B

A bacteriocin against B

A inhibit B
"""
"""
GLOBALS
"""
#Word Stemmer
stemmer = SnowballStemmer('english')

#Output Directory
outDir = "output/pattern/"
if not os.path.exists(outDir):
	os.makedirs(outDir)

ini = initialize.execute("quetzalcoatl.ini")
temp = []
with open(ini["ANTIBIOTICS"]) as f:
	for i in f:
		temp.append(i.lower().strip())

antibiotics = "(" + "|".join(temp) + ")"

"""""""""""""""""""""
#####################
#      PATTERNS     #
#####################
"""""""""""""""""""""

#Single-line Patterns
patterns = [
"Activity sjA against sjB",
"containing sjA inhibited sjB",
"sjA decreased sjB",
"bacteriocin sjA against sjB",
"bacteriocin sjA inhibit sjB",
"sjA compet sjB",
"Antagonistic sjA on sjB",
"sjA antimicrobial sjB",
"sjA antibacterial sjB",
"sjA antagonistic sjB",
"sjA bacteriocin sjB",
"sjA inhibit sjB",
"sjA inhibitory effect sjB",
"sjA inhibitory activity sjB",
"inhibit sjA by sjB"
]

#nPatterns
nPatterns = [
["bacteriocins produced by sja","antagonistic effect sjb"],
["bacteriocins produced by sja","inhibit sjb"]
]
#antiPatterns
antiPatterns = [
antibiotics
]


#lowercase them all
patterns = [i.lower() for i in patterns]
nPatterns = [[i.lower() for i in j]for j in nPatterns]
antiPatterns = [i.lower() for i in antiPatterns]


#####################
#      PATTERNS     #
#####################

#Enter in bacterial species here
bacterial_species_base = ["Escherichia coli", "Lactobacillus acidophilus"]
bacterial_species_base = {i.lower() for i in bacterial_species_base}
bacterial_species = {i.lower for i in bacterial_species_base}
for i in bacterial_species_base:
	temp = i.lower().split()
	bacterial_species.add(temp[0][0] + ". " + temp[1])




"""""""""""""""""""""
#####################
#       CLASSES     #
#####################
"""""""""""""""""""""

"""
pattern:
	Takes in a pattern sentence. Establishes a regex from the pattern and the initialization variables and uses it to detect informative patterns
	in the data.

	check(sentence):
		takes in a sentence and, using the precompiled regexes, attempts to detect a pattern. returns True if detected, false otherwise
	Initialize(sja, sjb):
		Compiles multiple regex variations of the pattern sentence from two input species


"""
class Pattern():
	def __init__(self, text):
		self.text = text
		self.regexes = []
	def export(self):
		return self.text

	def initialize(self, sja, sjb):
		#cleanup
		self.regexes = []
		sja, sjb = sja.lower(), sjb.lower()

		sp1 = [sja, abb(sja, regex = 1)]
		sp2 = [sjb, abb(sjb, regex = 1)]
		
		#initialize base regexes
		flags = self.text.split(' ')
		rFlags = copy.deepcopy(flags)
		#create forward match
		for j in sp1:
			for k in sp2:
				for i in range(len(flags)):
					if flags[i] == "sja":
						flags[i] = j
					elif flags[i] == "sjb":
						flags[i] = k
					else:
						flags[i] = flags[i]
				try:
					self.regexes.append(re.compile("(" + ".*".join(flags) + ")"))
					#self.regexes.append(re.compile("(" + "[ -\\.].*".join(flags) + ")"))
				except:
					print("RegexError: ",flags)
					print("sja: ",sja)
					print("sjb: ",sjb)
					raise
				flags = self.text.split(' ')
		#create reverse match
		for j in sp2:
			for k in sp1:
				for i in range(len(flags)):
					if flags[i] == "sja":
						flags[i] = j
					elif flags[i] == "sjb":
						flags[i] = k
					else:
						flags[i] = flags[i]
				try:
					self.regexes.append(re.compile("(" + ".*".join(flags) + ")"))
					#self.regexes.append(re.compile("(" + "[ -\\.].*".join(flags) + ")"))
				except:
					print("RegexError: ",flags)
					print("sja: ",sja)
					print("sjb: ",sjb)
					raise
				flags = self.text.split(' ')

		return

	def check(self, sentence):
		holder = []
		for regex in self.regexes:
			# print("REGEX: ", regex)
			temp = regex.search(sentence)
			if temp:
				holder.append(temp)
				# print("HIT")
		return holder
	
	def pCheck(self, paragraph):
		# print(paragraph)
		# print(self.regexes)
		holder = []
		for sentence in paragraph:
			# print("CHECKING: ", sentence)

			temp = self.check(sentence)
			if temp:
				holder.extend(temp)
		return holder

class nPattern():
	def __init__(self, textList):
		self.patterns = [Pattern(i)	for i in textList]
		self.text = "|||".join([pattern.text for pattern in self.patterns])

	def initialize(self, sja, sjb):
		for pattern in self.patterns:
			pattern.initialize(sja, sjb)

	def pCheck(self, paragraph):
		temp = [i for i in self.patterns]
		enum = enumerate(self.patterns)
		holder = [[] for i in self.patterns]
		for index, pattern in enum:
			checkData = pattern.pCheck(paragraph)
			if checkData:
				holder[index]=checkData[0]
				temp.remove(pattern)

		# print("HOLDER", holder)
		# print(temp)
		if len(temp) == 0:
			return holder
		return []
	def export(self):
		for i in self.patterns:
			print(i.regexes)


"""
getSpecies(abstract, target_bacterial_species)
	Input: 
		abstract text string, target bacterial_species
	Output:
		Intersection of the set of all species in the text (whole names) and the set of all species in target_bacterial_species
"""
def getSpecies(abstract, bact_species):
	text = abstract.lower().split(" ")
	species = set()
	for i in range(len(text)-1):
		word1 = text[i]
		word2 = text[i+1]
		if not word2[-1].isalpha():
			word2 = word2[:-1]
		if " ".join((word1, word2)) in bact_species:
			species.add(" ".join((word1, word2)))
	return species





"""
abb
	Takes in a string of format A B, where A is the genus and B the Species. Returns abbreviated species name
"""

def abb(spec, regex = 0):
	temp = spec.split(' ')
	if regex == True:
		spec =  temp[0][0] + '. ' + temp[1]
		return spec.replace(".", "\.")
	return temp[0][0] + '. ' + temp[1]

"""
makeName
"""

def makeName(sja, sjb):
	sja = '_'.join(sja.split(" "))
	sjb = '_'.join(sjb.split(" "))
	return sja+'#' + sjb + ".sp"
"""
makePatterns(patternStringList):
	takes in a list of pattern strings and processes them (tokenizing, stemming) into Pattern objects
"""
def makePatterns(patternStringList):
	patterns = [st.preprocess(i)[0] for i in patternStringList]
	patterns = [[stemmer.stem(j) for j in i ] for i in patterns]
	patterns = [" ".join(i) for i in patterns]
	return [Pattern(i) for i in patterns]	

def makeNpatterns(nPatternStringList):
	patterns = [[st.preprocess(i)[0] for i in j] for j in nPatternStringList]
	# print(patterns)
	patterns = [[[stemmer.stem(word) for word in sentence ] for sentence in sentenceTup] for sentenceTup in patterns]
	patterns = [[" ".join(i) for i in j] for j in patterns]
	return [nPattern(i) for i in patterns]	

def test(paperObject, patternList):
	for pattern in patternList:
		if pattern.pCheck(paperObject.sTitle) or pattern.pCheck(paperObject.sAbstract):
			return True
	return False


class PatternHolder:
	def __init__(self):
		patterns = dict()
	def check(self, species_tuple):
		if species_tuple in patterns:
			return patterns[species_tuple]
		else:
			patterns[species_tuple] = pa
"""
execute(filePath):
	
"""

def execute(abstract_list, cutoff):
	patternList = makePatterns(patterns)
	patternList += makeNpatterns(nPatterns)
	antiPatternList = makePatterns(antiPatterns)
	
	results = []
	counter = 1
	end = len(abstract_list)
	#MULTIPROCESS THIS
	for abstract in abstract_list:
		print("Processing abstract {}/{}".format(counter, end))
		print(abstract)
		counter+=1 
		abstract = abstract.lower()
		#Generate species pairs from the abstract
		species = getSpecies(abstract, bacterial_species_base)
		species_pairs = {tuple(sorted([i,j])) for i in species for j in species if i != j}

		#Split the abstract into sentences
		abstract = st.preprocess(abstract)
		abstract = [" ".join(i) for i in abstract]

		hits = []
		misses = []
		for pair in species_pairs:
			#initialize the patterns
			for pattern in patternList:
				print(pattern.text)
				pattern.initialize(pair[0], pair[1])
			for pattern in antiPatternList:
				pattern.initialize(pair[0], pair[1])
			#apply patterns to the abstract
			print(pair[0])
			print(pair[1])
			print(patternList[0].regexes)
			print(patternList[0].pCheck(abstract))
			temp_hits = [pattern.pCheck(abstract) for pattern in patternList]
			hits += [i for i in temp_hits if i != []]
			temp_misses = [pattern.pCheck(abstract) for pattern in antiPatternList]
			misses += [i for i in temp_misses if i != []]

		print("hits: ", hits)
		print("misses: ", misses)
		if len(hits) >= cutoff and len(misses) == 0:
			results.append((abstract, len(hits)))
	return results


	


def debug(abstract):
	patternList = makePatterns(patterns)
	test = patternList[0]
	test.initialize("a aaa", "b bbb")
	text = st.preprocess("Activity of a aaa against b bbb. The a aaa against c is.".lower())
	text = [" ".join(i) for i in text]
	print(text)
	print(patternList[0].regexes)
	print(test.pCheck(text))
	print(test.check(text[0]))
	print(test.regexes[0])
	print(text[0])
	print(test.regexes[0].search(text[0]))
	raise



if __name__ == "__main__":

	pp.SpFile("all.sp")
	# abstract = "the power of escherichia coli to kill all lactobacillus acidophilus. escherichia coli. Activity of Escherichia coli against lactobacillus acidophilus."

	# print(getSpecies(abstract, bacterial_species_base))
	# print(execute([abstract], 1))

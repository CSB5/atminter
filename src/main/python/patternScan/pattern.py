#!/usr/bin/env python3
from modules import sent_tokenize as st
from nltk.stem.snowball import SnowballStemmer
import os
import re
from modules import paperparse as pp
import copy

"""
pattern.py
	Takes a json file produced by pubcrawl, checks if any of the preloaded patterns are present. All members of patterns must 
	be present and in order. Patterns may be spaced out

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
Global Constants
"""
#directory locations
script_dir_path = os.path.join(os.path.realpath(__file__),"..")
minter_root = os.path.abspath(os.path.join(script_dir_path, "../../../.."))


#Word Stemmer
stemmer = SnowballStemmer('english')

temp = [i.lower().strip() for i in open(os.path.join(minter_root,"data",  "antibiotics.txt"))]
antibiotics = "(" + "|".join(temp) + ")"

"""
Patterns
"""

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

# nPatterns: Patterns that can be split across multiple sentences
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

"""
Classes
"""

"""
Paper():
	Class representation of a single paper. Contains the title, abstract, and their respective stemmed and tokenized forms
"""
class Paper():
	def __init__(self, spFilePaper, spSet = {}):

		self.spSet = spSet
		try:
			self.title = spFilePaper["TI"]
		except:
			print("ERRORSPFILE: ", spFilePaper)
			raise
		self.abstract = spFilePaper["AB"]
		self.sTitle = self.tokStem(self.title)
		self.sAbstract = self.tokStem(self.abstract)

	def tokStem(self, paragraph):
		temp = st.preprocess(paragraph, self.spSet)
		temp = [[stemmer.stem(i) for i in j] for j in temp]
		return [" ".join(i) for i in temp]

	def export(self):
		print("-------PAPER--------")
		print(self.spSet)
		print(self.title)
		print(self.abstract)
		print(self.sTitle)
		print(self.sAbstract)
		print("-------PAPER--------")

"""
Pair():
	Class contained of paper objects for all papers for a species pair. 
	Takes in a filePath to a set of line-separated, initalizer-tagged papers
	from that pair and packages them into Paper() objects


"""
class Pair():
	def __init__(self, filePath):
		#initalize the species sets
		sja, sjb = pp.getNames(filePath)[0], pp.getNames(filePath)[1]
		self.spSet1 = set(sja)
		self.spSet2 = set(sjb)
		self.spSet = self.spSet1.union(self.spSet2)

		#Load the papers
		self.spFile = pp.SpFile(filePath, purge = True)
		#unified is a tuple: (spFile.papers[i], Paper)
		self.unified = [(i, Paper(i, self.spSet)) for i in self.spFile.papers]

	def test(self, unifiedObject, patternList, antiPatternList):
		flag = 0
		# Make sure at least one pattern passes
		for pattern in patternList:
			titleCheck = pattern.pCheck(unifiedObject[1].sTitle)
			if titleCheck:
				unifiedObject[0]['TIHT'].append([pattern.text, [i for i in titleCheck]])
				flag = 1
			abstractCheck = pattern.pCheck(unifiedObject[1].sAbstract)	
			if abstractCheck:
				unifiedObject[0]['ABHT'].append([pattern.text, [i for i in abstractCheck]])
				flag = 1
		#antiPatternChecker
		for antiPattern in antiPatternList:
			if antiPattern.pCheck(unifiedObject[1].sTitle):
				unifiedObject[0]['TIHT'] = ""
				flag = 0
			if antiPattern.pCheck(unifiedObject[1].sAbstract):
				unifiedObject[0]['ABHT'] = ""
				flag = 0
		return flag
	def testAll(self, patternList, antiPatternList, outPath):
		for unifiedObject in self.unified:
			isTrue = self.test(unifiedObject, patternList, antiPatternList)
			if isTrue:
				self.spFile.summary["INT"] = '1'
				self.spFile.summary["NEG"] = '1'
			self.spFile.writeSpFile(outPath)


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
					self.regexes.append(re.compile("(" + "[ -\\.].*".join(flags) + ")"))
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
					self.regexes.append(re.compile("(" + "[ -\\.].*".join(flags) + ")"))
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
				holder.append(temp.group(0))
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

"""
execute(filePath):
	Summary script. Loads all papers in the filepath and tests them with the preloaded patternStringList.
	TODO:
		allow customization of output folder
"""

def execute(filePath, out_dir = ""):
	
	#Extraction of subject names
	names = pp.getNames(filePath)
	sja, sjb = stemmer.stem(names[0][0]), stemmer.stem(names[1][0])
	
	out_name = "{}#{}.json".format(sja.replace(" ", "_"), sjb.replace(" ", "_"))

	out_path = os.path.join(out_dir, out_name)
	

	patternList = makePatterns(patterns)
	patternList += makeNpatterns(nPatterns)
	antiPatternList = makePatterns(antiPatterns)
	for pattern in patternList:
		pattern.initialize(sja, sjb)
	for pattern in antiPatternList:
		pattern.initialize(sja, sjb)


	pairPapers = Pair(filePath)

	pairPapers.testAll(patternList, antiPatternList, out_path)

def debug(filePath):
	#Extraction of subject names
	names = pp.getNames(filePath)
	sja, sjb = names[0][0], names[1][0]

	patternList = makePatterns(patterns)
	#patternList = makeNpatterns(nPatterns)
	# reverseList = makePatterns(patterns)
	for pattern in patternList:
		pattern.initialize(sja, sjb)
	pairPapers = Pair(filePath)
	print(pairPapers.spFile.papers[0])
	print(pairPapers.unified[0][1].sAbstract)
	print(patternList[11].pCheck(pairPapers.unified[0][1].sAbstract))
	print(patternList[11].text)





if __name__ == "__main__":

	import sys
	target = os.path.join(minter_root, "data/testing_data/lactobacillus_acidophilus#bifidobacterium_longum.moddedjson")
	#target = sys.argv[1]
	debug(target)
	execute(target)
	
#!/usr/bin/env python3
"""
svm_core.py
	Core component of all SVMs used in the @MInter system

	Provides the following core objects for later use
		Purger:
			regex-based string genercizer. Currently used to remove identifying bacterial species names from text
		text_clf:
			SVM-based classifcation pipeline for text data


"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn import svm
from modules import paperparse as pp
from random import shuffle
import re
import os


script_dir_path = os.path.join(os.path.realpath(__file__),"..")
minter_root = os.path.abspath(os.path.join(script_dir_path, "../../../.."))
bact_names_path = os.path.join(minter_root, "data", "DSMZ_bactnames0315.csv")

# Constants
outDir = os.path.join(minter_root, "output", "svm_scan")
if not os.path.exists(outDir):
	os.makedirs(outDir)

# Obtain all bacterial names
bact_names = [" ".join(i.strip().lower().split(",")) for i in open(bact_names_path)][1:]
bact_names = [i for i in bact_names if i[-1] != " "]
all_bact_names = {i for i in bact_names} | {i.split(" ")[0][0] +". " + i.split(" ")[1] for i in bact_names}
#print(all_bact_names)


##########################
#        FUNCTIONS       #
##########################

"""
read(filePath)
	reads a .ann file, converting it into a list of 3Tuples (">T", "TITLE", "ABSTRACT")
"""
def read(filePath):
	with open(filePath) as f:
		temp = [i for i in f]
		temp = [temp[i:i + 3] for i in range(0,len(temp), 3)]

	return temp


##########################
#         CLASSES        #
##########################

"""
Purger()

purge
	takes in a target (string) and a filter (list of strings), removes all instances of filter words from the target, replacing
	them with other_species. Filter uses a " " + filter_word regex to remove them
"""

class Purger():
	def __init__(self, filterList):
		query =  "(" + "|".join([i for i in filterList])+ ")"
		query = query.replace(".", "\.")
		self.regex = re.compile(query)

	def purge(self, string):
		return self.regex.sub("other_species", string)

"""
grade()
	Overview of performacne. Takes in a classifier and two lists: one of test sets and one of the results and scores 
	the performance of the classifier on the list
	input:
		clf:
			Classifier objects
		test:
			abstract vector
		targets:
			targets for abstract vector
		probas = None:
			Enable probability, probability set is 1- cutoff
"""

def grade(clf, test, targets, probas = None):
	test_total = 0
	test_pos = 0
	TP = 0
	FP = 0
	FN = 0
	TN = 0
	for i, j in zip(test, targets):
		test_total += 1
		if j == 1:
			test_pos +=1
			if not probas:
				if clf.predict([i])[0] == True:
					TP +=1
				else:
					FN +=1
			else:
				if clf.predict_proba([i])[0][0] <= probas:
					TP +=1
				else:
					FN +=1

		else:
			if not probas:
				if clf.predict([i])[0] == True:
					FP += 1
				else:
					TN +=1
			else:
				if clf.predict_proba([i])[0][0]<=0.1:
					FP += 1
				else:
					TN +=1


	print("test_total", test_total)
	print("test_pos", test_pos)
	print("TP", TP)
	print("FP", FP)
	print("FN", FN)
	print("TN", TN)
	if TP == 0 and FP == 0:
		recall = 0
	else:
		recall = TP/(TP + FN)
	print("Sensitivity: ", recall)

	if TN == 0 and FP == 0:
		specificity = "N/A: 0 reported positives "
	else:
		specificity = TN/(TN + FP)

	print("Specificity: ", specificity)

	if TP == 0 and FP == 0:
		precision = "N/A: 0 reported positives "
	else:
		precision = TP/(TP + FP)
	print("Precision: ", precision)

	if TP == 0 and FP == 0 and FN == 0 and TN == 0:
		accuracy = "N/A: 0 reported positives "
	else:
		accuracy = (TP + TN)/(TP + FP + TN + FN)
	print("Accuracy", accuracy)
	if TP == 0 and FP == 0 or precision == 0:
		fScore = 0
		print("F-score: N/a: No recorded positives" )	
	else:
		fScore = 2 *(precision*recall)/(precision + recall)
		print("F-score: ", fScore)
	print("---------")
	return [recall, specificity, precision, accuracy]

def score(clf, test, targets):
	t = grade(clf, test, targets)
	print(t)
	return t[0] * t[1]


def make_classifier(C = 1):
	return Pipeline([
	('tfidf', TfidfVectorizer()),
	('clf', svm.SVC(kernel = "linear", C = C, class_weight = "auto", probability = True))
	])		
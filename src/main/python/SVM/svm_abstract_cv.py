#/usr/bin/env python3

import svm_core as sc
import os
import numpy as np
from sklearn import cross_validation
import argparse
import math
import sys

script_dir_path = os.path.join(os.path.realpath(__file__),"..")
minter_root = os.path.abspath(os.path.join(script_dir_path, "../../../.."))
sys.path.append(minter_root+"/lib")

from modules import paperparse as pp

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument( "target", help ="target directory containing annotated .sp files")
	parser.add_argument( "-p", "--probas", help ="Proabibility value cutoff (optional)", type = float, default = None)
	args = parser.parse_args()
	baseFolder = args.target
	
	"""
	Training of the SVM
	"""

	#Folder Setup
	
	baseFolder = "tests/svm_trainer/"
	coreTrain = baseFolder + "Core/lactobacillus_acidophilus#escherichia_coli.ann"
	trainFile = baseFolder + "collated_train.ann"
	files = sc.read(trainFile)
	abstracts = [i[2] for i in files]
	targets = np.array([True if i[0].strip() == ">T" else False for i in files ])

	skf = cross_validation.StratifiedKFold(y = targets, n_folds = 10, shuffle = True)

	scoring = []

	print("DATA SET LENGTH: ", len(targets))
	for train_index, test_index in skf:
		# print(train_index)
		# print(test_index)

		#Training pairs: all pairs containing annotated true-true interactions
		training_set = [abstracts[i] for i in train_index]
		training_set_targets = [targets[i] for i in train_index]
		testing_set = [abstracts[i] for i in test_index]
		testing_set_targets = [targets[i] for i in test_index]
		svm = sc.make_classifier(C=1)
		svm.fit(training_set, training_set_targets)

		scoring.append(sc.grade(svm, testing_set, testing_set_targets, probas = args.probas))

	

	print("-------__RESULTS_____---------")
	for i in scoring:
		print(i)

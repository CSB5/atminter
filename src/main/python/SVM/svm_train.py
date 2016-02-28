#!/usr/bin/env python3

__author__ = "Kenneth Lim"


"""
svm_train.py 
	Core file, trains an SVM off a .ann file or a json file of 
"""

import svm_core as sc
import argparse
import os
import numpy as np
import pickle
import json

script_dir_path = os.path.join(os.path.realpath(__file__),"..")
minter_root = os.path.abspath(os.path.join(script_dir_path, "../../../.."))


if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument( "target", help ="target .ann file to train SVM on")
	parser.add_argument( "-o", "--output", help ="Output path for pickled SVM", default = os.path.join(minter_root, "output", "trained_svms", "trained_svm.pickle"))
	parser.add_argument( "-C", help = "C value of SVM", type = int, default = 1)
	parser.add_argument( "-j", "--json", help = "Use json file (unimplemented", action = "store_true", default = 0)
	args = parser.parse_args()

	if not os.path.exists(os.path.dirname(args.output)):
		os.makedirs(os.path.dirname(args.output))

	clf = sc.make_classifier(args.C)
	if args.json:
		files = json.load(target)
		files = [(i["value"], i["title"], i["abstract"]) for i in files]
	else:
		files = sc.read(args.target)
	
	print(len(files))
	print(files[0])

	abstracts = [i[2] for i in files]
	targets = np.array([True if i[0].strip() == ">T" else False for i in files ])
	print(clf.get_params())
	#Train and dump classfier
	temp = clf.fit(abstracts, targets)
	pickle.dump(clf, open(args.output, "wb"))

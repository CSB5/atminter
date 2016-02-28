#!/usr/bin/env python3
"""
svm_scanner:
	Uses a pickled svm (svm_train)
"""

import pickle
import os
from math import log
import argparse
import sys

script_dir_path = os.path.join(os.path.realpath(__file__),"..")
minter_root = os.path.abspath(os.path.join(script_dir_path, "../../../.."))
sys.path.append(minter_root+"/lib")
from modules import paperparse as pp

parser = argparse.ArgumentParser()
parser.add_argument( "SVM", help ="pickled SVM file")
parser.add_argument( "target", help = "target directory containing spFiles to be scanned")
parser.add_argument( "-o", "--output", help ="output directory", default = os.path.join(minter_root, "output", "svm_scanner"))
parser.add_argument( "-j", "--json", help = "Use json files instead", action = "store_true", default = 1) #change to sp switch
args = parser.parse_args()

print("LOADING SVM: ", args.SVM)
svm = pickle.load(open(args.SVM, "rb"))
print(svm.get_params())
target = args.target
outdir = args.output

if not os.path.exists(outdir):
	os.makedirs(outdir)
targetPaths = [os.path.join(target, i) for i in os.listdir(target)]

cur = 0
total_papers = 0
lower_bound = 0
total_hits = 0

for file_num, targetPath in enumerate(targetPaths):
	print("FILE NUMBER: ", file_num)
	if args.json:
		pair = pp.SpFile(targetPath, purge = True)
	else:
		pair = pp.spFile(targetPath, purge = True)

	hits = 0

	total = len(targetPaths)
	print ("analysing pair " +str(cur) + "/" + str(total))
	print(targetPath)
	cur+=1

	if args.json:
		temp = pp.SpFile(targetPath, reduced = True)
	else:
		temp = pp.spFile(targetPath, reduced = True)
	if temp.summary["NEG"] != "1":
		lower_bound += len(pair.papers)
		# print(pair.papers)
		# print(len(pair.papers))
	total_papers += len(pair.papers)

	paper_count = len(pair.papers)
	for paper_num, paper in enumerate(pair.papers):	
		print("processing paper {}/{}".format(paper_num, paper_count))
		#implement temporary lowers to allow persistance of the original paper
		if paper["AB"]:
			if svm.predict([paper["AB"]]):
				paper["ABHT"] = "1"
				hits += 1
				pair.summary["INT"] = "1"
				pair.summary["NEG"] = "1"
				print("HIT")
				total_hits +=1
		else:
			paper["ABHT"] = "0"
			pair.summary["INT"] = "0"
			pair.summary["NEG"] = "0"

	pair.writeSpFileHits(os.path.join(outdir, os.path.basename(targetPath)))

print("total_papers =", total_papers)
print("lower_bound =", lower_bound)
print("total_hits =", total_hits)

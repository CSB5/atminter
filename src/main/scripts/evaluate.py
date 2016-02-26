#!/usr/bin/env python3
"""
Evaluate.py
	Takes in a two directories of JSON files. One produced by a classifier(svm/pattern Scan) and one with preannotated .sp's.
	Evaluates the negative interaction detection accuraccy (patternScan) or the interaction detection accuracy(svmScan)

"""
from modules import paperparse as pp
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument( "target", help ="Target directory for evaluation")
parser.add_argument( "annotated", help ="Directory containing annotated files")
parser.add_argument( "-o", "--outdir", help ="Override output directory. Default = output/patternscan/evaluate/", default = "output/patternscan/evaluate/")
parser.add_argument( "-s", "--selective", action = 'store_true', help = "remove low information pairs (same species interactions, genus only interactions", default = False)
args = parser.parse_args()


"""
DIRECTORY SETUP
"""
#Check for improperly formatted directory paths
if args.target[-1] != '/':
	args.target += '/'

if args.outdir[-1] != '/':
	args.outdir += '/'

if args.annotated[-1] != '/':
	args.annotated += '/'

outDirs = dict()
outDirNames = [
"INT_TP", "INT_FP", "INT_FN", "INT_TN","POS_TP", "POS_FP", "POS_FN", "POS_TN", "NEG_TP", "NEG_FP", "NEG_FN", "NEG_TN"
]

for i in outDirNames:
	outDirs[i] = args.outdir + i

for i in outDirs:
	if not os.path.exists(outDirs[i]):
		os.makedirs(outDirs[i])


"""
Execution
"""

print("Reading Directory")
tester = [args.target + i for i in sorted(os.listdir(args.target))]
annotated = [args.annotated + i for i in  sorted(os.listdir(args.annotated))]

holder = dict()

for i in tester:
	holder[os.path.basename(i).lower()] = [i]

for i in annotated:
	holder[os.path.basename(i).lower()].append(i)

class Dataset():
	def __init__(self, key):
		self.key = key
		self.TP = 0
		self.FP = 0
		self.TN = 0
		self.FN = 0

	def evaluate(self, annPaper, testedPaper, debug = 0):
		annPaperDict, testedPaperDict = annPaper.summary, testedPaper.summary
		ann, tested = annPaperDict[self.key], testedPaperDict[self.key]
		#TP
		if ann == '1' and tested == '1':
			self.TP +=1
			testedPaper.writeSpFile(outDirs[self.key.strip()+'_'+'TP']+ '/' + testedPaper.fileName)
			# with open(outDirs[self.key.strip()+'_'+'TP']+ '/' +, 'a') as f:
			# 	f.write()
		#TN
		elif ann == '0' and tested == '0':
			self.TN += 1
			testedPaper.writeSpFile(outDirs[self.key.strip()+'_'+'TN']+ '/' + testedPaper.fileName)
		#FP
		elif ann == '0' and tested == '1':
			self.FP += 1
			testedPaper.writeSpFile(outDirs[self.key.strip()+'_'+'FP']+ '/' + testedPaper.fileName)
		#FN
		elif ann == '1' and tested == '0':
			self.FN += 1
			annPaper.writeSpFile(outDirs[self.key.strip()+'_'+'FN']+ '/' + testedPaper.fileName)



	def export(self):
		print("-----------" + self.key + "DATASET:-----------")
		print("TP: ", self.TP)
		print("FP: ", self.FP)
		print("TN: ", self.TN)
		print("FN: ", self.FN)
		if self.TP + self.FN == 0:
			recall = "N/A: 0 reported TP or FN"
		else:
			recall = self.TP/(self.TP + self.FN)
		print("Sensitivity: ", recall)
		print("Specificity: ", self.TN/(self.TN + self.FP))
		if self.TP == 0 and self.FP == 0:
			precision = "N/A: 0 reported positives "
		else:
			precision = self.TP/(self.TP + self.FP)
		print("Precision: ", precision)
		print("Accuracy", (self.TP + self.TN)/(self.TP + self.FP + self.TN + self.FN))
		if self.TP == 0 and self.FP == 0:
			print("F-score: N/a: No recorded positives" )	
		else:
			print("F-score: ", 2 *(precision*recall)/(precision + recall))

INT = Dataset("INT ")
POS = Dataset("POS ")
NEG = Dataset("NEG ")

t= 0
for i in holder:
	temp = holder[i]

	#LOW INFORMATION CHECK
	if args.selective:
		name = os.path.splitext(os.path.basename(temp[0]))[0].split('#')

		#same species
		if i[0] == i[1]:
			print("Skipping duplicate: ", name)
			continue

		#genus only
		if name[0].split('_')[1] == 'sp.':
			print("Skipping genus only: ", name)
			continue
		if name[1].split('_')[1] == 'sp.':
			print("Skipping genus only: ", name)
			continue
	t +=1



	testerPath = pp.SpFile(temp[0])
	annPath = pp.SpFile(temp[1])
	# print(testerPath.summary)
	# print(annPath.summary)
	# print(os.path.basename(temp[0]))
	# print(os.path.basename(temp[1]))

	for dataset in [INT, POS, NEG]:
		dataset.evaluate(annPath, testerPath)

	# print(INT.TN)
	# print(POS.TN)
	# print(NEG.TN)
print("TOTAL PAPERS: ", t)
#raise
INT.export()
POS.export()
NEG.export()

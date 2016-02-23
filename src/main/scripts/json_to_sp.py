#!/usr/bin/env python3

__author__ = "Kenneth Lim"

"""
json_to_sp
converts a json file to the sp file used in earlier @MInter versions
"""

import json
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument( "target", help ="Target json directory")
args = parser.parse_args()

target = os.listdir(args.target)
if not os.path.exists("output"):
	os.makedirs("output")

for file_path in target:
	if file_path[-4:] != "json":
		continue
	full_path = os.path.join(args.target,file_path)
	name = os.path.join("output", full_path[:-4] + "sp")
	with open(full_path) as f:
		data = json.load(f)
	with open(name, "w") as f:
		f.write("@SUMMARY\n")
		f.write("INT == {}\n".format(data["SUMMARY"]["INT"]))
		f.write("NEG == {}\n".format(data["SUMMARY"]["NEG"]))
		f.write("POS == {}\n".format(data["SUMMARY"]["POS"]))
		f.write("@PAPERS\n")
		for paper in data["PAPERS"]:
			f.write("PMID== {}\n".format(paper["PMID"]))
			f.write("TI  == {}\n".format(paper["TI"]))
			f.write("AB  == {}\n".format(paper["AB"]))
			f.write("TIHT== {}\n".format(paper["TIHT"]))
			f.write("ABHT== {}\n\n".format(paper["ABHT"]))


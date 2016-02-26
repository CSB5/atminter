#!/usr/bin/env python3

__author__ = "Kenneth Lim"

"""
json_to_sp
converts a json file to the sp file used in earlier @MInter versions
"""

import json
import argparse
import os
from modules import paperparse as pp

script_dir_path = os.path.join(os.path.realpath(__file__),"..")
minter_root = os.path.abspath(os.path.join(script_dir_path, "../../.."))


parser = argparse.ArgumentParser()
parser.add_argument( "target", help ="Target .sp directory")
parser.add_argument( 
	"-o", "--output",
	help ="Output directory", 
	default = os.path.join(minter_root, "output", "sp_to_json")
	)
args = parser.parse_args()

if not os.path.exists(args.output):
	os.makedirs(args.output)

targets = [i for i in os.listdir(args.target)]
length = len(targets)

for num, file_path in enumerate(targets):
	print("Now processing file {}/{}".format(num+1, length))
	if file_path[-2:] != "sp":
		continue
	full_path = os.path.join(args.target,file_path)
	file_name = os.path.basename(full_path)
	name = os.path.join(args.output, file_name[:-2] + "json")
	data = pp.spFile(full_path)
	result = {"SUMMARY":dict(), "PAPERS":[]}
	for i in data.summary:
		result["SUMMARY"][i] = data.summary[i]
	for paper in data.papers:
		result["PAPERS"].append({i.strip():paper[i] for i in paper})

	json.dump(result, open(name, "w"))





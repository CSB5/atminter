#!/usr/bin/env python3

"""
pubcrawl.py
	PubMed crawler
	input:
		.TSV of word pairs (bacteria). E.g. "Genus_Species_1	Genus_Species_2".
	output:
		Downloads all papers returned by an AND joined query of the word pairs. E.g. "Genus_Species_1" AND 
		"Genus_Species_2". PMIDs, Abstracts and titles of the papers are returned in a json file with title 
		Genus_Species_1#Genus_Species_2.json

"""


from Bio import Entrez, Medline
from time import strftime, sleep
import os
import multiprocessing
import argparse
import json




error_log = "errors.txt"

"""
pubmedSearch
	Main search function. Searches the terms and feeds the result into grabTerm

	Outputs all title-abstract pairs into files.
"""
def pubmedSearch(term1, term2, outDir, retryCount = 0):
	print("Beginning: ", "\t".join([term1, term2]))
	query = "{} AND {}".format(term1, term2)

	try:
		handle = Entrez.esearch(db = "pubmed", term = query , usehistory = "y")	
		record = Entrez.read(handle)
	except:
		if retryCount <3:
			print("Retrying {}, {}".format(term1, term2))
			return pubmedSearch(term1, term2, outDir, retryCount = retryCount +1)
		else:
			print('ERROR: query "{}" failed to query'.format(query))
			return
	

	count = int(record["Count"])
	print("\t".join([term1, term2]) + ": " + str(count))
	batch_size = 10
	out_name = os.path.join(outDir, '_'.join((term1 + '#' + term2).split(' ')) + ".json" )
	holder = []

	#download the papers
	for start in range(0,count, batch_size):
		end = min(count, start+batch_size)
		# print("Going to download record %i to %i" % (start+1, end))
		# print(term1, term2)
		try:
			fetch_handle = Entrez.efetch(db = "pubmed",
											rettype = "medline", retmode= "text",
											retstart = start, retmax = batch_size,
											webenv = record["WebEnv"], query_key = record["QueryKey"] 
											)
		except:
			if retryCount < 3:
				return pubmedSearch(term1, term2, outDir, retryCount = retryCount + 1)
			else:
				print("#ERROR#"+ query+ "FAILED TO DOWNLOAD")
				with open("errors.txt", 'a') as f:
					f.write(query + "\n")
				return

		#Stepwise Raw data preprocessing
		data = Medline.parse(fetch_handle)
		
		data = [i for i in data]

		#[print(i) for i in data]
		
		fetch_handle.close()
		holder.extend(data)
		sleep(0.5)

	# Prepare dictionaries
	output = {"SUMMARY": {"INT":0, "NEG":0, "POS":0}, "PAPERS":[]}
	# Fill with papers
	for paper in holder:
		paper_entry = dict()
		paper_entry["PMID"] = paper["PMID"]
		# Handle missing titles
		if "TI" in paper:
			paper_entry["TI"] = paper["TI"]
		else:
			paper_entry["TI"] = ""
		# Handle missing abstracts
		if "AB" in paper:
			paper_entry["AB"] = paper["AB"]
		else:
			paper_entry["AB"] = ""
		paper_entry["TIHT"] = []
		paper_entry["ABHT"] = []

		output["PAPERS"].append(paper_entry)

	# Dump the json
	with open(out_name, 'w') as f:
		json.dump(output, f)





if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument( "target", help ="Target file. File must be a line-separated list of tab separated term pairs. eg: Escherichia coli  Pseudomonas aeruginosa")
	parser.add_argument( "email", help ="Email address. If pubmed is overloaded by you, warnings will be sent here", type = str)
	parser.add_argument( "-c", "--cores", help ="number of cores", default = 4, type = int)
	parser.add_argument("-o", "--outdir", help ="Choose output directory. Default = output/pubcrawl/$DATETIME", default = "output/pubcrawl/"+ strftime("%Y-%m-%d-%H_%M"))
	args = parser.parse_args()

	# Setup Entrez registered email address
	Entrez.email = args.email


	# Create directory for output if it does not exist
	if not os.path.exists(args.outdir):
		os.makedirs(args.outdir)

	# Prepare data into tuples for analysis
	with open(args.target) as f:
		pairIn = [i.strip().split('\t') + [args.outdir] for i in f if i != '\n']

	pool = multiprocessing.Pool(args.cores)
	mappedRuns = pool.starmap(pubmedSearch, pairIn)
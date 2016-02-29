##The @MInter bacterial interaction detection system.


###1. Core components


__pretrained SVMs__

data/SVMs/core_trained_svm.p
	pickled SVM object for use in svm_scanner.py.
	Trained on only interactions involving Escherichia coli and Lactobacillus acidophilus
data/SVMs/full_trained_svm.p
	pickled SVM object for use in svm_scanner.py.
	Trained on entire corpus

__SVM Tools__

SVM/svm_scanner.py

SVM script. Takes in a directory of JSON files (format in 2.) returns a tagged JSON ("ABHT" field) for each file. 1 == interaction detected, 0 == no interaction detected. Refer to script help for more details.

SVM/svm_train.py

Training script. Takes in an annotated corpus file (.ann), produces a trained, pickled SVM from that corpus. 

__Pattern Scanner__

patternScan/patternScan.py

Pattern Scanner script. Takes in a directory of JSON files (format in 2.) returns a tagged JSON ("ABHT" field) for each file. If an interaction is detected, a list of all patterns signifying the interaction is inserted into the "ABHT" field. Refer to script help for more details.

__Annotated Corpus__

Annotated abstracts/annotations for @SVM training

/data/train_test_data/lactobacillus_acidophilus#escherichia_coli.ann
	Core dataset

/data/train_test_data/collated_train.ann
	Extended dataset: training ready

/data/train_test_data/collated_annotations.tar.gz
	Extended dataset

###2. Quickstart

####2.0 Data acquisiton (Currently undocumented)

#####2.0.1 Acquiring data for processing

Provide a TSV of species 2-tuples of the following format and save.

	Species_1	Species_2
	Species_1	Species_2

Execute /src/main/scripts/pubcrawl.py on TSV

__Sample command__

	./src/main/python/scripts/pubcrawl.py <filepath> <your_email> -c <corecount> -o <output directory>


####2.1 SVM use

#####2.1.1 Using a pretrained SVM

__Sample command__

	./src/main/python/SVM/svm_scanner.py data/svms/full_trained_svm.p data/example/svm_test -o data/example/svm_test_output/

svm_scanner.py uses a pretrained SVM (full_trained_svm.p) to analyze data in data/example/svm_test. Output results to data/example/svm_test_output/ as JSON files.

#####2.1.2 Training an SVM for @MInter

	./src/main/python/SVM/svm_train.py data/example/svm_train/lactobacillus_acidophilus#escherichia_coli.ann -o data/example/svm_train_output/core_svm.p

svm_train.py uses annotated data (lactobacillus_acidophilus#escherichia_coli.ann) to train an SVM. Outputs SVM as data/example/svm_train_output/core_svm.p.

####2.2 Pattern Scanner

#####2.2.1 Pattern Scanner use

	./src/main/python/patternScan/pattern_scan.py data/example/pattern_test -o data/example/pattern_test_output/

pattern_scan.py analyzes data in data/example/pattern_test using precompiled patterns and outputs to data/example/pattern_test_output/

###3. Input format

The @MInter system, as input, uses the following files:

####JSON

**filename:**

Species_1#Species_2.json

**Contents:**

A sample file is included in data/train_test_data/lactobacillus_acidophilus#escherichia_coli.json

	{"SUMMARY":
		{
			"INT": <bool>, #Interaction between the two species
			"NEG": <bool>, #Negative interaction between the two species
			"POS": <bool>, #Positive interaction between the two species
	}
	{"PAPERS":[			#List of paper dictionaries
		{
			"PMID":<str>,	#Paper PMID
			"TI":<str>,		#Paper Title
			"AB":<str>,		#Paper Abstract
			"TIHT":<str>,	#Depreciated
			"ABHT":<str>,	#Sentenced detected if pattern found (Patternscan); Numeric value depending on interaction (SVM)
			}, 
	]}

	}

####Annotation files

**filename:**

Filename.ann

**contents**

File containing annotated abstracts for ML training. Consists of line triplets for each paper with truth value, title text and abstract text on lines i, i+1 and i +2 respectively. 

A sample file is included in data/train_test_data/lactobacillus_acidophilus#escherichia_coli.ann
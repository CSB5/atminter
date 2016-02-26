The @MInter bacterial interaction detection system.


#1. Core components


	pretrained SVMs
		data/SVMs/core_trained_svm.p
			pickled SVM object for use in svm_scanner.py.
			Trained on only interactions involving Escherichia coli and Lactobacillus acidophilus
		data/SVMs/full_trained_svm.p
			pickled SVM object for use in svm_scanner.py.
			Trained on entire corpus


	SVM/svm_scanner.py
		SVM script. Takes in a directory of JSON files (format in 2.) returns a tagged JSON ("ABHT" field) for each file. 1 == interaction detected, 0 == no interaction detected. Refer to script help for more details.
	SVM/svm_train.py
		Training script. Takes in an annotated corpus file (.ann), produces a trained, pickled SVM from that corpus. 

	patternScan/patternScan.py
		Pattern Scanner script. Takes in a directory of JSON files (format in 2.) returns a tagged JSON ("ABHT" field) for each file. If an interaction is detected, a list of all patterns signifying the interaction is inserted into the "ABHT" field. Refer to script help for more details.


	Annotated abstracts/annotations for @SVM training
		/data/train_test_data/lactobacillus_acidophilus#escherichia_coli.ann
			Core dataset

		/data/train_test_data/collated_train.ann
			Extended dataset: training ready

		/data/train_test_data/collated_annotations.tar.gz
			Extended dataset

#2. Input format
	The @MInter system, as input, takes in JSONs of the following format:
	**filename:**

	Species_1#Species_2.json

	**Contents:**

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
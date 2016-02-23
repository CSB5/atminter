#!/usr/env/bin python3
"""
sent_tokenize:
	Modified segtok, attempts correction of incorrectly split species names

"""

import nltk
from segtok.segmenter import split_single as ssplit
import re

sCheck = re.compile(r"( [a-zA-Z]\.)")
sWordCheck = re.compile(r"([a-zA-Z]\.)")

def specJoin(lst, spSet = {}):
	new = []
	i = 0
	while i < len(lst):
		if sCheck.match(lst[i][-3:]) and i < len(lst)-1:
			new.append(lst[i]  + ' '+ lst[i+1])
			i+=1
		elif i < len(lst)-1  and " ".join([lst[i], lst[i+1]]) in spSet:
			new.append(" ".join([lst[i], lst[i+1]]))
			i+=1

		else:
			new.append(lst[i])
		i+=1
	return new

def specWordJoin(lst, spSet = {}):
	# print("BEGINNING WORD JOIN")
	new = []
	i = 0
	while i < len(lst):
		# if i < len(lst)-1:
			# print(" ".join([lst[i], lst[i+1]]))
			# print(" ".join([lst[i], lst[i+1]]) in spSet)
			# print([i for i in spSet])


		if len(lst[i]) == 2 and sWordCheck.match(lst[i]):
			new.append(lst[i] + ' ' + lst[i+1])
			i+=1

		elif i < len(lst)-1  and " ".join([lst[i], lst[i+1]]) in spSet:
			new.append(" ".join([lst[i], lst[i+1]]))
			i+=1

		else:
			new.append(lst[i])
		i+=1
	return new
'''
sentSplit:
	splits a paragraph into sentences

	input: string containing a paragraph
	output: List of sentences
'''
def sentSplit(doc, spSet = {}):
	sent = list(ssplit(doc))
	sent = specJoin(sent, spSet)
	return sent

#Processes a list of sentences
def preprocess(doc, spSet = {}):
	# print("USING FOLLOWING SET")
	# print([i for i in spSet])
	sent = sentSplit(doc, spSet)
	sent = [nltk.word_tokenize(i) for i in sent]
	sent = [specWordJoin(i, spSet) for i in sent]
	return sent

if __name__ == "__main__":
	test = ('the place of molecular genetic methods in the diagnostics of human pathogenic anaerobic bacteria. a minireview.', 'anaerobic infections are common and can cause diseases associated with severe morbidity, but are easily overlooked in clinical settings. both the relatively small number of infections due to exogenous anaerobes and the much larger number of infections involving anaerobic species that are originally members of the normal flora, may lead to a life-threatening situation unless appropriate treatment is instituted. special laboratory procedures are needed for the isolation, identification and susceptibility testing of this diverse group of bacteria. since many anaerobes grow more slowly than the facultative or aerobic bacteria, and particularly since clinical specimens yielding anaerobic bacteria commonly contain several organisms and often very complex mixtures of aerobic and anaerobic bacteria, considerable time may elapse before the laboratory is able to provide a final report. species definition based on phenotypic features is often time-consuming and is not always easy to carry out. molecular genetic methods may help in the everyday clinical microbiological practice in laboratories dealing with the diagnostics of anaerobic infections. methods have been introduced for species diagnostics, such as 16s rrna pcr-rflp profile determination, which can help to distinguish species of bacteroides, prevotella, actinomyces, etc. that are otherwise difficult to differentiate. the use of dna-dna hybridization and the sequencing of special regions of the 16s rrna have revealed fundamental taxonomic changes among anaerobic bacteria. some anaerobic bacteria are extremely slow growing or not cultivatable at all. to detect them in special infections involving flora changes due to oral malignancy or periodontitis, for instance, a pcr-based hybridization technique is used. molecular methods have demonstrated the spread of specific resistance genes among the most important anaerobic bacteria, the members of the bacteroides genus. their detection and investigation of the is elements involved in their expression may facilitate following of the spread of antibiotic resistance among anaerobic bacteria involved in infections and in the normal flora members. molecular methods (a search for toxin genes and ribotyping) may promote a better understanding of the pathogenic features of some anaerobic infections, such as the nosocomial diarrhoea caused by c. difficile and its spread in the hospital environment and the community. the investigation of toxin production at a molecular level helps in the detection of new toxin types. this mini-review surveys some of the results obtained by our group and others using molecular genetic methods in anaerobic diagnostics.')
	print(test[1])
	a = sentSplit(test[1])
	print(a)
	b = preprocess(test[1])
	print(b)

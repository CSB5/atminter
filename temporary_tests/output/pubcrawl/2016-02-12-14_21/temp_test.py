import json
with open("lactobacillus_acidophilus#bifidobacterium_longum.json") as f:
	data = json.load(f)

print([i for i in data["PAPERS"]])

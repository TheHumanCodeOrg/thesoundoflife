import json

with open("../data/dna_key.json") as f:
	dna_key = json.load(f)

codons = dna_key['codons']
ascii2idx = dna_key['ascii2idx']
idx2class = dna_key['idx2class']
angles = dna_key['angles']

def aminoIsStopCodon(aa):
	return aa == "Stop"

def aminoIsStartCodon(aa):
	return aa == 'M'

def aminoAngle(aa):
	return angles[str(ord(aa))]

def aminoToIndex(aa):
	return ascii2idx[str(ord(aa))]

def codonBufferToAmino(buf):
	global codons
	buf = "".join(buf).upper()
	cod = codons[buf]
	return cod
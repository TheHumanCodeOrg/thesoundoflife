# amino_acid.py

"""
Convenience functions for decoding base pair codons, and for converting between different representations
of an amino acid. For example, the amino acid Methionine can be represented as the character 'M', the integer
77 (which is the ascii value of a capital M), or as its index, 10, since it is the 10th amino acid when
they are sorted alphabetically.
"""

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
	"""
	Each amino acid is mapped to an arbitrary angle according to the values in data/dna_key.json. These
	values are NOT based on real physical properties.
	"""
	return angles[str(ord(aa))]

def aminoToIndex(aa):
	"""
	Each amino acid is given a unique index between 0 and 19, inclusive, according to the values in data/dna_key.json
	"""
	return ascii2idx[str(ord(aa))]

def codonBufferToAmino(buf):
	"""
	Given a codon string of length 3 containing only the characters, a, c, g or t, this will return the appropriate amino acid
	"""
	global codons
	buf = "".join(buf).upper()
	cod = codons[buf]
	return cod
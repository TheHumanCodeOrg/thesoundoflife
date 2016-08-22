#!/usr/bin/python

import sys

buf = [0 for x in range(3)]
idx = 0
prot = ''
prot_idx = 0

aa_dict = {
	'ATT': 'I',
	'ATC': 'I',
	'ATA': 'I',
	'CTT': 'L',
	'CTC': 'L',
	'CTA': 'L',
	'CTG': 'L',
	'TTA': 'L',
	'TTG': 'L',
	'GTT': 'V',
	'GTC': 'V',
	'GTA': 'V',
	'GTG': 'V',
	'TTT': 'F',
	'TTC': 'F',
	'ATG': 'M',
	'TGT': 'C',
	'TGC': 'C',
	'GCT': 'A',
	'GCC': 'A',
	'GCA': 'A',
	'GCG': 'A',
	'GGT': 'G',
	'GGC': 'G',
	'GGA': 'G',
	'GGG': 'G',
	'CCT': 'P',
	'CCC': 'P',
	'CCA': 'P',
	'CCG': 'P',
	'ACT': 'T',
	'ACC': 'T',
	'ACA': 'T',
	'ACG': 'T',
	'TCT': 'S',
	'TCC': 'S',
	'TCA': 'S',
	'TCG': 'S',
	'AGT': 'S',
	'AGC': 'S',
	'TAT': 'Y',
	'TAC': 'Y',
	'TGG': 'W',
	'CAA': 'Q',
	'CAG': 'Q',
	'AAT': 'N',
	'AAC': 'N',
	'CAT': 'H',
	'CAC': 'H',
	'GAA': 'E',
	'GAG': 'E',
	'GAT': 'D',
	'GAC': 'D',
	'AAA': 'K',
	'AAG': 'K',
	'CGT': 'R',
	'CGC': 'R',
	'CGA': 'R',
	'CGG': 'R',
	'AGA': 'R',
	'AGG': 'R',
	'TAA': 'Stop',
	'TAG': 'Stop',
	'TGA': 'Stop'
}

def process(buf):
	global prot, prot_idx
	buf = "".join(buf).upper()
	cod = aa_dict[buf]
	if prot:
		if cod is 'Stop':
			if len(prot) > 100:
				with open('protein_' + str(prot_idx) + '.txt', 'w') as o:
					o.write(prot)
			prot = ''
			prot_idx = prot_idx + 1
		else:
			prot = prot + cod
	elif cod is 'M':
		prot = 'M'

## Read in the first argument as a file
with open(sys.argv[1], 'r') as f:
	## Skip the first line
	l = f.readline()

	## Now read everything else and process each 3 byte chunk
	for line in f:
		for c in line:
			if c is 'N':
				idx = 0;
			elif c in 'atcgATCG':
				buf[idx] = c
				idx = idx + 1
				if (idx == 3):
					idx = 0
					process(buf)

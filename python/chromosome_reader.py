#!/usr/bin/env python
# chromosome_reader.py

from amino_acid import *

chunksize = 1000

class ChromosomeReader:
	def __init__(self, filename):
		self.chromosome = open(filename, 'r')
		self.chromosome.readline()
		self.buf = [0 for x in range(3)]
		self.idx = 0
		self.chunkidx = 0
		self.moreComing = True
		self.chunk = None
		self.basePairsRead = 0
		self.aminoAcidsRead = 0
		self.loadNextChunk()

	def getBasePairsRead(self):
		return self.basePairsRead

	def getAminoAcidsRead(self):
		return self.aminoAcidsRead

	def loadChromosomeFile(self, filename):
		if (self.chromosome):
			self.chromosome.close()
		self.chromosome = open(filename, 'r')
		self.chromosome.readline()
		self.buf = [0 for x in range(3)]
		self.idx = 0
		self.chunkidx = 0
		self.moreComing = True
		self.chunk = None
		self.basePairsRead = 0
		self.aminoAcidsRead = 0
		self.loadNextChunk()

	def loadNextChunk(self):
		self.chunk = self.chromosome.read(chunksize)
		self.chunkidx = 0

	def hasNext(self):
		return self.moreComing

	def nextAmino(self):
		termine = False
		while (self.idx < 3):

			## Try to read in the next chunk
			if (self.chunkidx >= len(self.chunk)):
				self.loadNextChunk();
				if (len(self.chunk) == 0):
					termine = True
					break

			ch = self.chunk[self.chunkidx]
			self.basePairsRead += 1
			self.chunkidx += 1
			if (ch is 'N'):
				self.idx = 0
			elif ch in 'CATGcatg':
				self.buf[self.idx] = ch
				self.idx = self.idx + 1
		self.idx = 0
		if not termine:
			self.aminoAcidsRead += 1
			return codonBufferToAmino(self.buf)
		self.moreComing = False
		return None
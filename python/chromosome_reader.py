#!/usr/bin/env python
# chromosome_reader.py

from amino_acid import *
import os

"""
Reads a chromosome file. The file should be in the .fa format. This file contains metadata on
the first line, followed by the characters a,c,t,g,A,C,T,G and N. ChromosomeReader scans through
these files one amino acid at a time. It does not (currently) differentiate between uppercase (coding)
and lowercase (repeating) regions.
"""

chunksize = 1000

class ChromosomeReader:
	def __init__(self, filename):
		self.filename = filename
		self.bytesize = os.path.getsize(filename)
		self.estimatedTotalAminos = self.bytesize / 3
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
		"""
		Get the total number of base pairs read. This INCLUDES the N character.
		"""
		return self.basePairsRead

	def getAminoAcidsRead(self):
		"""
		Get the total number of amino acids read. This will be equal to the number of actgACTG characters
		at before the current file position, divided by 3. Said another way, it does NOT include the N character.
		"""
		return self.aminoAcidsRead

	def loadChromosomeFile(self, filename):
		"""
		Loads a chromosome file for reading, and moves the cursor to the beginning of the file
		"""
		if (self.chromosome):
			self.chromosome.close()
		self.filename = filename
		self.bytesize = os.path.getsize(filename)
		self.estimatedTotalAminos = self.bytesize / 3
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
		print "Loaded chromosome at {}".format(filename)

	def seekPosition(self, position):
		"""
		Jump to the given base pair position in the current chromosome. This does NOT process the amino
		acids between the current position and the new position.
		"""
		self.chromosome.seek(position)
		self.loadNextChunk()

	def loadNextChunk(self):
		"""
		Internal function for streaming files from disk.
		"""
		self.chunk = self.chromosome.read(chunksize)
		self.chunkidx = 0

	def hasNext(self):
		"""
		Returns True if there are more amino acids to be read, False otherwise
		"""
		return self.moreComing

	def nextAmino(self):
		"""
		Advances through the .fa file, until three base pairs are successfully read. Returns the amino
		acid coded for by that base pair sequence, or None if the end of the file is reached. This function
		will skip over regions of N base pairs automatically, and does not differentiate between lowercase 
		and uppercase characters.
		"""
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
from amino_acid import *
from polypeptide import *
from sequence import *
# from graphics import *

polypeptideLimit = 4;

smallSequenceCount = 4;
smallSequenceSize = 16;

class Conductor:
	def __init__(self):
		self.polypeptides = []
		self.isSynthesizingPolypeptide = False
		self.inProgressPolypeptide = None
		self.smallSequences = [None for _ in range(smallSequenceCount)]
		self.smallSequenceIndex = 0;
		# self.win = GraphWin()

	def addAmino(self, aa):
		if self.isSynthesizingPolypeptide:
			if (aminoIsStopCodon(aa)):
				self.polypeptides.append(self.inProgressPolypeptide)
				if (self.inProgressPolypeptide.size() > 90):
					print self.inProgressPolypeptide
					s = Sequence(self.inProgressPolypeptide, 16)
					print s
					self.smallSequences[self.smallSequenceIndex] = s
					self.smallSequenceIndex = (self.smallSequenceIndex + 1)  % smallSequenceCount
				# 	self.inProgressPolypeptide.graphicsDraw(self.win, Point(50, 50))
				self.isSynthesizingPolypeptide = False
				self.inProgressPolypeptide = None
			else:
				self.inProgressPolypeptide.addAmino(aa)
		elif (aminoIsStartCodon(aa)):
			self.isSynthesizingPolypeptide = True
			self.inProgressPolypeptide = Polypeptide()

	def midiEventsForStep(self, step):
		midiEvents = []
		for seqIdx, seq in enumerate(self.smallSequences):
			if seq is not None:
				seqMidiEvents = map(lambda x: x + [(seqIdx+1)], seq.midiEventsForStep(step))
				midiEvents = midiEvents + seqMidiEvents
		return midiEvents

	def reset(self):
		self.polypeptides = []
		self.isSynthesizingPolypeptide = False
		self.inProgressPolypeptide = None
		self.smallSequences = [None for _ in range(smallSequenceCount)]
		self.smallSequenceIndex = 0;
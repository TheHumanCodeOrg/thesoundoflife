from polypeptide import *
from amino_acid import *
from math import floor

maxNoteAge = 3
maxNoteCount = 2

class Sequence:
	def __init__(self, polypeptide, size, options = {}):
		self.polypeptide = polypeptide
		self.size = size
		self.chunks = self.chunksForPolypeptide(polypeptide)
		self.sequenceIndexSet = []
		self.density = 1.0
		self.sequence = self.initializeSequence()
		self.age = 0
		self.mono = options.get("mono", False)
		self.currentNote = None
		self.currentNoteAge = 0
		self.stepRate = options.get("stepRate", 1)
		self.lastStep = 0

	def chunksForPolypeptide(self, polypeptide, minsize=4):
		idx = 0
		prevIx = 0
		chunks = []
		if polypeptide.getAminos():
			while (prevIx < len(polypeptide.getAminos()) and idx < len(polypeptide.getIntersections()) + 1):
				ix = polypeptide.getIntersections()[idx] if idx < len(polypeptide.getIntersections()) else len(polypeptide.getAminos())
				idx = idx + 1
				if (ix-prevIx >= minsize):
					chunk = {
						"aminos": polypeptide.getAminos()[prevIx:ix],
						"offset": ix
					}
					chunks.append(chunk)
				prevIx = ix
		return chunks

	def initializeSequence(self):
		outSequence = {}
		for chunk in self.chunks:
			aidx = aminoToIndex(chunk["aminos"][0])
			offset = chunk["offset"] % self.size
			pitch = aidx
			vel = 127 * len(chunk["aminos"]) / self.size
			seqTrack = outSequence[aidx] if aidx in outSequence else [None for x in range(self.size)]
			for eidx, event in enumerate(seqTrack):
				if ((eidx + offset) % len(chunk["aminos"])) is 0:
					if (event is not None):
						event[1] = min(127, vel + event[1])
					else:
						seqTrack[eidx] = [pitch, vel]
			if aidx not in outSequence:
				self.sequenceIndexSet.append(aidx)
			outSequence[aidx] = seqTrack
		return outSequence

	def midiEventsForStep(self, step, channel):
		step = step / self.stepRate
		if step == self.lastStep:
			return []
		self.lastStep = step
		midiEvents = []
		eidx = step % self.size
		tracksToUse = floor(self.density * len(self.sequenceIndexSet))
		for trackIdx, seqTrackIdx in enumerate(self.sequenceIndexSet):
			if (trackIdx >= tracksToUse):
				break
			seqTrack = self.sequence[seqTrackIdx]
			if seqTrack[eidx] is not None:
				midiEvents.append(seqTrack[eidx] + [channel])
		midiEvents = midiEvents[0:maxNoteCount]

		if self.mono:
			midiEvents.sort(key=lambda x: x[0], reverse=True)
			if self.currentNote is not None:
				if midiEvents:
					self.currentNoteAge += 1
				if self.currentNoteAge > maxNoteAge:
					self.currentNote = midiEvents[0]
					self.currentNoteAge = 0
					midiEvents = [midiEvents[0]]
				else:
					midiEvents = []
			else:
				self.currentNote = midiEvents[0]
				self.currentNoteAge = 0
				midiEvents = [midiEvents[0]]

		return midiEvents

	def setDensity(self, d):
		self.density = d

	def __str__(self):
		os = ""
		for c in self.sequence:
			os = os + str(c) + ": " + ", ".join(map(str, self.sequence[c])) + "\n"
		return os
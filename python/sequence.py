from polypeptide import *
from amino_acid import *
from math import floor

"""
Translates polypeptide chains into MIDI events, and returns the MIDI events that occur at a particular
timestep. 

In order to turn a polypeptide into a MIDI events sequence, the Sequence class uses the method
of Deep Rhythms from Godfriend T. Toussaint. In this method, a measure is divided into some number
of subdivisions. Then, the measure is filled with evenly spaced rhythmic events, until no more events will 
fit into the measure. Here are some examples of deep rhythms:

[ x _ _ x _ _ x _ ] (8 subdivisions, events separated by 3)
[ x _ _ _ _ x _ _ ] (8 subdivisions, events separated by 5)
[ x _ _ _ x _ _ _ x _ _ _ x _ _ _ ] (16 subdivisions, events separated by 4)

To produce inputs for the deep rhythm generator, the polypeptide must be analyzed. First, the we draw
the polypeptide as a line in two dimensions. The line bends at each amino acid, at an angle that depends
on the particular amino acid. These angles are NOT based on real physical properties, but rather on
arbitrary angles stored in the file data/dna_key.json. After the polypeptide is drawn, we look for places
where the polypeptide crosses itself. Each time the polypeptide self-intersects, we divide it at that
intersection. So if a polypeptide were 12 amino acids long, and it crossed itself at amino acid 4, then
it would be divided into two chunks, one from amino acids 1-4 and the other from 5-12

Each of these chunks is then used to generate a deep rhythm. The number of subdivisions is determined by 
the size of the sequence. The separation between events is taken to be the number of amino acids in the
chunk. The particular MIDI note that will be placed in the Sequence is determined by the amino acid at 
the beginning of the chunk. For the time being, no other information is used.

Once the Sequence has been initialized with a polypeptide, it is then possible to retrieve the MIDI events
stored at each timestep. Calling midiEventsForStep will return all of the MIDI events for the given timestep.
Sequences are assumed to repeat, so if a sequence has length n, then all timesteps are taken to be modulo n.
Calling midiEventsForStep on a sequence of length 16 will return the same MIDI events for step 1, 17, 33 etc.

If the value mono is set to True for a sequence, then only one note will play at a time for the sequence. 
Once a note starts playing, it will block other notes until it stops, or until the hardcoded value maxNoteAge
is exceeded.

The hardcoded value maxNoteCount limits the number of notes that can play at once.
"""

maxNoteAge = 3
maxNoteCount = 2

class Sequence:
	def __init__(self, polypeptide, size, options = {}):
		self.polypeptide = polypeptide
		self.size = size
		self.chunks = self.chunksForPolypeptide(polypeptide)
		self.sequenceIndexSet = []
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
		"""
		Returns the midi events at a particular timestep. The result will be a list of length 3n,
		where n is the number of midi events at the given timestep. Each event is comprised of three
		integers, one for each of pitch, velocity and channel. The value of channel will be the same
		as the channel argument.

		args:
			step: Nonnegative integer, the timestep for which MIDI events will be retrieved
			channel: Positive integer, the MIDI channel value for each event
		"""
		step = step / self.stepRate
		if step == self.lastStep:
			return []
		self.lastStep = step
		midiEvents = []
		eidx = step % self.size
		for trackIdx, seqTrackIdx in enumerate(self.sequenceIndexSet):
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

	def __str__(self):
		os = ""
		for c in self.sequence:
			os = os + str(c) + ": " + ", ".join(map(str, self.sequence[c])) + "\n"
		return os
		
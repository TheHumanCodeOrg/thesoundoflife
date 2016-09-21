from amino_acid import *
from polypeptide import *
from sequence import *

"""
Interprets amino acids, generating a MIDI note sequence, and returns the MIDI events bound to a 
particular timestep. In typical use, genome_server will call addAmino in response a /read message.
New amino acids are chained together until a "stop" codon is received. At that point a polypeptide 
(sequence of amino acids) is used to generate a MIDI sequence (an instance of sequence.py). More on
how that process works can be found in the sequence.py file. The genome_server instance will also
call the processStep function in response to a /step message, which should return all of the MIDI events
that occur at that point in time. This is simply a concatenation of the MIDI output of each sequence.

For now, the Conductor owns a fixed number of sequences. Those sequences are divided into small, medium
and large sequence groups. When a polypeptide is completed, it will generate a sequence in one of these
groups depending on its length. Each sequence group can only contain so many sequences. When a new sequence
is generated, it will replace an old sequence if there is no more room in a particular sequence group.
The values defining the cutoff size for each sequence group, the number of sequences per sequence group, and
the number of timesteps in a sequence of each size are all hard-coded, for now, at the top of the conductor.py
file.

Each sequence outputs MIDI events on a unique MIDI channel. The channels are sequential, starting with the 
small sequences. So, if there are four small sequences, two medium sequences and one large sequence, then the
small sequences will have channels 1, 2, 3 and 4, the medium sequences will have channels 5 and 6, and the
large sequence will have channel 7.

smallSequenceCount: The maximum number of sequences in the smallest SequenceGroup
smallSequenceSize: The number of timesteps in a member of the small SequenceGroup
smallSequenceBPSize: The minimum number of amino acids that must constitute a polypeptide for it to
					generate a sequence in the small SequenceGroup
smallSequenceOptions: Currently unused.
"""

smallSequenceCount = 4
smallSequenceSize = 16
smallSequenceBPSize = 90
smallSequenceOptions = {
}
mediumSequenceCount = 2
mediumSequenceSize = 32
mediumSequencesBPSize = 120
mediumSequenceOptions = {
}
largeSequenceCount = 1
largeSequenceSize = 16
largeSequenceBPSize = 150
largeSequenceOptions = {
}

class SequenceGroup:
	def __init__(self, seqCount, size, channelOffset, options={}):
		self.sequences = [None for _ in range(seqCount)]
		self.seqIndex = 0
		self.pendingSequences = []
		self.sequenceIndexesToRemove = []
		self.channelOffset = channelOffset
		self.size = size
		self.maxAge = options.get("maxAge", -1)

	def getSize(self):
		return self.size

	def appendPendingSequence(self, seq):
		self.pendingSequences.append(seq)

	def isDownbeat(self, step):
		return step % self.size == 0

	def flushPendingSequences(self):
		for idx in self.sequenceIndexesToRemove:
			self.sequences[idx] = None
		self.sequenceIndexesToRemove = []
		for s in self.pendingSequences:
			self.sequences[self.seqIndex] = s
			self.seqIndex = (self.seqIndex + 1)  % len(self.sequences)
		self.pendingSequences = []

	def getSequences(self):
		return self.sequences

	def getChannelOffset(self):
		return self.channelOffset

	def removeSequenceAtIndex(self, idx):
		if idx not in self.sequenceIndexesToRemove:
			print "Removing sequence at index {}".format(idx)
			self.sequenceIndexesToRemove.append(idx)

class Conductor:
	def __init__(self):
		self.polypeptides = []
		self.isSynthesizingPolypeptide = False
		self.inProgressPolypeptide = None
		self.aminoAcidCounts = [0 for _ in range(20)]

		self.totalSequences = 0
		self.smallSequences = SequenceGroup(smallSequenceCount, smallSequenceSize, 1 + self.totalSequences, smallSequenceOptions)
		self.totalSequences += smallSequenceCount
		self.mediumSequences = SequenceGroup(mediumSequenceCount, mediumSequenceSize, 1 + self.totalSequences, mediumSequenceOptions)
		self.totalSequences += mediumSequenceCount
		self.largeSequences = SequenceGroup(largeSequenceCount, largeSequenceSize, 1 + self.totalSequences, largeSequenceOptions)
		self.totalSequences += largeSequenceCount

		self.sequenceGroups = [self.smallSequences, self.mediumSequences, self.largeSequences]
		# self.win = GraphWin()

	def addAmino(self, aa):
		"""
		Called from genome_server to add a new amino acid to the conductor. Until a stop codon is reached, each new
		amino acid adds to a growing polypeptide chain. When the chain completes, the polypeptide is used to 
		generate a new Sequence object, which contains MIDI events drawn from an interpretation of the polypeptide.
		Depending on the length of the polypeptide, the generated sequence will go into one of the small, medium
		or large SequenceGroups. Polypeptides that are smaller than the minimum size necessary to generate a 
		Sequence could be used somehow, perhaps to create some kind of atmospheric sound or texture, but we do not
		currently make use of them.

		In addition to using the amino acids to make a Sequence, this class also keeps count of how many amino acids
		of each kind it has encountered. This can be used to drive Low Frequency Oscillators, which might affect
		filters and other effects in the Live set.
		"""
		if self.isSynthesizingPolypeptide:
			if (aminoIsStopCodon(aa)):
				# self.polypeptides.append(self.inProgressPolypeptide)

				if (self.inProgressPolypeptide.size() > largeSequenceBPSize):
					s = Sequence(self.inProgressPolypeptide, largeSequenceSize, {"stepRate": 32})
					self.largeSequences.appendPendingSequence(s)
					print "New large sequence"
				elif (self.inProgressPolypeptide.size() > mediumSequencesBPSize):
					s = Sequence(self.inProgressPolypeptide, mediumSequenceSize, {"stepRate": 2})
					self.mediumSequences.appendPendingSequence(s)
					print "New medium sequence"
				elif (self.inProgressPolypeptide.size() > smallSequenceBPSize):
					s = Sequence(self.inProgressPolypeptide, smallSequenceSize)
					self.smallSequences.appendPendingSequence(s)
					print "New small sequence"
				
				## TODO Handle incidental polypeptides like this

				# 	self.inProgressPolypeptide.graphicsDraw(self.win, Point(50, 50))
				self.isSynthesizingPolypeptide = False
				self.inProgressPolypeptide = None
			else:
				self.inProgressPolypeptide.addAmino(aa)
		elif (aminoIsStartCodon(aa)):
			self.isSynthesizingPolypeptide = True
			self.inProgressPolypeptide = Polypeptide()

		## Count the amino for LFO's
		if not aminoIsStopCodon(aa):
			aa_idx = aminoToIndex(aa)
			self.aminoAcidCounts[aa_idx] = (self.aminoAcidCounts[aa_idx] + 1)

	def processStep(self, step):
		"""
		Called from genome_server to collect all of the MIDI events for a particular timestep.
		In the current implementation, this simply collects all of the MIDI events from each
		Sequence object and concatenates them together. The returned list of midi events will contain
		three integers for each MIDI event, defining the pitch, velocity and channel of each event.
		"""
		## On a downbeat, there may be pending sequences that should be added to the set of 
		## currently active sequences
		for sg in self.sequenceGroups:
			if (sg.isDownbeat(step)):
				sg.flushPendingSequences()
			for sidx, seq in enumerate(sg.getSequences()):
				if seq is not None:
					seq.age += 1
					if sg.maxAge > -1:
						if seq.age > sg.maxAge:
							sg.removeSequenceAtIndex(sidx)

		# Now collect the MIDI events from each Sequence, append and return them
		midiEvents = []
		for sg in self.sequenceGroups:
			for seqIdx, seq in enumerate(sg.getSequences()):
				if seq is not None:
					seqMidiEvents = seq.midiEventsForStep(step, sg.getChannelOffset() + seqIdx)
					midiEvents = midiEvents + seqMidiEvents
		return midiEvents

	def reset(self):
		"""
		Clears out all of the Sequences and SequenceGroups, and sets the count of each amino acid to zero
		"""
		self.polypeptides = []
		self.isSynthesizingPolypeptide = False
		self.inProgressPolypeptide = None
		self.aminoAcidCounts = [0 for _ in range(20)]
		
		self.totalSequences = 0
		self.smallSequences = SequenceGroup(smallSequenceCount, smallSequenceSize, 1 + self.totalSequences)
		self.totalSequences += smallSequenceCount
		self.mediumSequences = SequenceGroup(mediumSequenceCount, mediumSequenceSize, 1 + self.totalSequences)
		self.totalSequences += mediumSequenceCount
		self.largeSequences = SequenceGroup(largeSequenceCount, largeSequenceSize, 1 + self.totalSequences)
		self.totalSequences += largeSequenceCount

		self.sequenceGroups = [self.smallSequences, self.mediumSequences, self.largeSequences]

	def getAminoAcidCounts(self):
		"""
		Returns the current count of each amino acid (sorted alphabetically)
		"""
		return self.aminoAcidCounts

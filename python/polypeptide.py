from amino_acid import *
from math import pi, cos, sin
from graphics import *


"""
Polypeptide stores a list of amino acids. Typical use involves calling addAmino with a sequence of amino
acids, until a stop codon is reached. Then, one can call getIntersections to get all of the indexes where
the polypeptide intersects itself. Sequence uses this method to divide the polypeptide into chunks.

If a graphics context exists, one can call graphicsDraw to draw the polypeptide. Not used or supported, but
useful for debugging.
"""

class Polypeptide:
	def __init__(self):
		self.aminos = []
		self.points = [(0, 0)]
		self.intersections = []

	def addAmino(self, aa):
		"""
		Appends the amino acids to the polypeptide chain. If the amino acid intersects the current protein,
		then its index will be appended to self.intersections as well.

		The amino acid should be a single capital character that maps to an amino acid. See data/dna_key.json
		for valid characters. 
		"""
		self.aminos.append(aa)
		lastPoint = self.points[-1]
		angle = aminoAngle(aa)
		nextPoint = (lastPoint[0] + cos(angle * pi * 2), lastPoint[1] + sin(angle * pi * 2))
		self.points.append(nextPoint)
		thisSegment = (self.points[-2], self.points[-1])
		for i in range(len(self.aminos)-1):
			otherSegment = (self.points[i], self.points[i+1])
			if self.segmentsIntersect(thisSegment, otherSegment):
				self.intersections.append(len(self.aminos) - 1)
				break

	def getIntersections(self):
		"""
		Returns a list of each index where an amino acid intersects the rest of the protein chain.
		"""
		return self.intersections

	def getAminos(self):
		"""
		Returns the amino acids in the protein as a list. Each amino acid is a single capital character
		"""
		return self.aminos

	def segmentsIntersect(self, seg1, seg2):
		"""
		Utility method for determining if two two-dimensional segments intersect. Each seg argument is assumed
		to be a list of two lists of length two. AKA a two-by-two array.
		"""
		s1_x = seg1[1][0] - seg1[0][0]
		s1_y = seg1[1][1] - seg1[0][1]
		s2_x = seg2[1][0] - seg2[0][0]
		s2_y = seg2[1][1] - seg2[0][1]

		denom = -s2_x * s1_y + s1_x * s2_y

		if (denom > 1e-10):
			s = (-s1_y * (seg2[0][0] - seg1[0][0]) + s1_x * (seg2[0][1] - seg1[0][1])) / (-s2_x * s1_y + s1_x * s2_y)
			t = ( s2_x * (seg2[0][1] - seg1[0][1]) - s2_y * (seg2[0][0] - seg1[0][0])) / (-s2_x * s1_y + s1_x * s2_y)
			return (s >= 0 and s <= 1 and t >= 0 and t <= 1)
		else:
			return False

	def graphicsDraw(self, win, center):
		"""
		Will draw the amino acid at center, given a window to draw in. See graphics.py for more.
		"""
		lastPoint = None
		for p in self.points:
			thisPoint = Point(p[0] + center.x, p[1] + center.y)
			if lastPoint is not None:
				line = Line(lastPoint, thisPoint)
				line.draw(win)
			lastPoint = thisPoint

	def size(self):
		"""
		The number of amino acids in the chain
		"""
		return (len(self.aminos))

	def __str__(self):
		return "-".join(self.aminos) + "\n" + "-".join(map(str, self.intersections))
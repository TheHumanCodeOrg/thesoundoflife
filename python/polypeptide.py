from amino_acid import *
from math import pi, cos, sin
from graphics import *

class Polypeptide:
	def __init__(self):
		self.aminos = []
		self.points = [(0, 0)]
		self.intersections = []

	def addAmino(self, aa):
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
		return self.intersections

	def getAminos(self):
		return self.aminos

	def segmentsIntersect(self, seg1, seg2):
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
		lastPoint = None
		for p in self.points:
			thisPoint = Point(p[0] + center.x, p[1] + center.y)
			if lastPoint is not None:
				line = Line(lastPoint, thisPoint)
				line.draw(win)
			lastPoint = thisPoint

	def size(self):
		return (len(self.aminos))

	def __str__(self):
		return "-".join(self.aminos) + "\n" + "-".join(map(str, self.intersections))
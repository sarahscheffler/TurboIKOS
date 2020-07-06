"""
a construction of which gates wer will be using. This file is purely for writing functions in the form of logic gates. no data will be stored here)
"""

class gate:
	#input: 2 inputs, 3 triples/ 0's
	def __init__(self, input1, input2, triple1, triple2, triple3):	
		self.x = input1
		self.y = input2
		self.a = triple1
		self.b = triple2
		self.c = triple3
		self.z = 0
	#Assigns z = a + b
	def add(self):
		pass
	#Assigns z = a*b
	def mult(self):
		pass

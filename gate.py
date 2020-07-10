"""
a construction of which gates wer will be using. This file is purely for writing functions in the form of logic gates. no data will be stored here)
"""
import Value
import wire
class gate:
	#input: 2 inputs, 3 triples/ 0's
	def __init__(self, input1, input2, output, triple1, triple2, triple3):	
		self.x = input1
		self.y = input2
		self.a = triple1
		self.b = triple2
		self.c = triple3
		self.z = output
	#Assigns z = x + y
	def add(self):
		z = Value.wrapAdd(wire.acceess_wire(self.x), wire.acceess_wire( self.y))
		wire.insert_wire(self.z, z)
	
	#Assigns z = x*y
	def mult(self):
		z = Value.wrapMul(wire.acceess_wire(self.x), wire.acceess_wire(self.y))
		wire.insert_wire(self.z, z) 

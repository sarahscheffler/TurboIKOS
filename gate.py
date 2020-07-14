"""
a construction of which gates wer will be using. This file is purely for writing functions in the form of logic gates. no data will be stored here)
"""
#import Value
#import wire
import circuit
class gate:
	#input: 2 inputs, 3 triples/ 0's
	def __init__(self, input1, input2, output,*, triple1=None, triple2 = None, triple3 = None, operation = None):	
		self.x = input1
		self.y = input2
		self.z = output
		if operation == 'AND' or 'MUL':
			self.a = triple1
			self.b = triple2
			self.c = triple3
		if operation == 'XOR' or 'ADD':
			self.a = None
			self.b = None
			self.c = None

	#Assigns v values z = x + y for each party
	#Assign e value on output wire
	def add(self):
		for i in range(circuit.n_parties):
			x_v = Value.Value(wire.acceess_wire(self.x, v, i)
			y_v = wire.acceess_wire(self.y, v, i)
			z_v = x_v.add(y_v)
			wire.insert_wire(self.z, z,v,i)
		z_e = x_e + y_e
		wire.insert_wire(self.z, z_e) 

	#Assigns v values  z = x*y for each party
	#assign e value on output wire
	#return e share for broadcast
	def mult(self):
		e_broadcast = []*circuit.n_parties
		e = 0
		for i in range(circuit.n_parties):
			x_e = Value.Value(wire.acceess_wire(self.x, e))
			y_e = Value.Value(wire.acceess_wire(self.y, e))
			xy_e = Value.Value(x_e*y_e)
			ay_e = Value.Value(y_e.mul(self.a[i]))
			bx_e = Value.Value(x_e.mul(self.b[i]))
			c = Value.Value(self.c[i])
			z = xy_e - ay_e - bx_e + c
			wire.insert_wire(self.z, z,v,i)
			e_broadcast[i] = z + wire.acceess_wire(self.z, lambda, i)
			e = e + e_broadcast[i]
		wire.insert_wire(self,z, e)
		return e_broadcast
			


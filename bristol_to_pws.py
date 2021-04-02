#!/usr/bin/python3

# Convert bristol fashion circuit to PWS format

import getopt
import sys

opt_str = 'i:o:'
(opts, _) = getopt.getopt(sys.argv[1:], opt_str)
no_i = True
no_o = True
for (o, a) in opts:
    if o=='-i':
        in_filename = a
        no_i = False
    elif o=='-o':
        out_filename = a
        no_o = False
    else:
        assert False, "Unknown option '%s'" % o
assert not no_i and not no_o, "Input or output file not specified"

### Read Bristol

with open(in_filename, 'r') as in_f:
    in_lines = in_f.readlines()
while in_lines[-1]=="\n":
    in_lines = in_lines[:-1] # strip off empty lines at end
if in_lines[3] == "\n":
    in_lines = in_lines[:3] + in_lines[4:]
assert len(in_lines) >= 3, "Input file hast <3 lines"

try:
    (n_gates, n_wires) = tuple(map(int, in_lines[0].split()))
except:
    assert False, "First line formatted incorrectly"
assert n_gates == len(in_lines[3:]), "Wrong number of gates in circuit"

try:
    n_iv = int(in_lines[1].split()[0])
    n_iw_i = []
    for i in range(1, n_iv+1):
        n_iw_i.append(int(in_lines[1].split()[i]))
except:
    assert False, "Second line formatted incorrectly"

try:
    n_ov = int(in_lines[2].split()[0])
    n_ow_i = []
    for i in range(1, n_ov+1):
        n_ow_i.append(int(in_lines[2].split()[i]))
except:
    assert False, "Third line formatted incorrectly"

gates = []
for g in range(n_gates):
    gates.append({})
    gateline = in_lines[3 + g].split()
    gates[g]["g_n_iw"] = int(gateline[0])
    gates[g]["g_n_ow"] = int(gateline[1])
    gates[g]["g_iw_i"] = []
    gates[g]["g_ow_i"] = []
    for i in range(2, gates[g]["g_n_iw"]+2):
        gates[g]["g_iw_i"].append(int(gateline[i]))
    for i in range(2+gates[g]["g_n_iw"], 2+gates[g]["g_n_iw"]+gates[g]["g_n_ow"]):
        gates[g]["g_ow_i"].append(int(gateline[i]))
    gates[g]["g_op"] = gateline[-1]
    
### Write PWS

def format_input_line(wire):
    return "P V%d = I%d E\n" % (wire, wire)
def format_and_line(gate, vo):
    return "P %s%d = V%d * V%d E\n" % (vo, gate["g_ow_i"][0], gate["g_iw_i"][0], gate["g_iw_i"][1])
def format_inv_line(gate, vo):
    return "P %s%d = V%d NOT V%d E\n" % (vo, gate["g_ow_i"][0], gate["g_iw_i"][0], gate["g_iw_i"][0])
def format_xor_line(gate, vo):
    return "P %s%d = V%d XOR V%d E\n" % (vo, gate["g_ow_i"][0], gate["g_iw_i"][0], gate["g_iw_i"][1])
def format_gate(gate):
    vo = "O" if gate["g_ow_i"][0] >= n_wires - sum(n_ow_i) else "V"
    if gate["g_op"] == "AND":
        return format_and_line(gate, vo)
    elif gate["g_op"] == "INV":
        return format_inv_line(gate, vo)
    elif gate["g_op"] == "XOR":
        return format_xor_line(gate, vo)
    else:
        assert False, "Bad gate operation: %s" % g_op

to_write = []
for i in range(sum(n_iw_i)):
    to_write.append(format_input_line(i))
for gate in gates:
    to_write.append(format_gate(gate))
assert len(to_write) == n_wires, "Size of output (%d) did not match n_wires (%d)" % (len(to_write), n_wires)

# Reorder so they go in order of wires instead of gates
reordered = []
for i in range(n_wires):
    for j in range(len(to_write)):
        if i == int(to_write[j].split()[1][1:]):
            reordered.append(to_write[j])
            to_write = to_write[:j] + to_write[j+1:]
            break

with open(out_filename, 'w') as out_f:
    out_f.writelines(reordered)



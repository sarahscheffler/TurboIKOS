
import pickle
from Value import Value
import Value as v
import gmpy2

byte_len = round(v.get_bits()/8)

#serializing using pickle for Value objects

def serial(info): 
    flatten = b''
    for i in range(len(info)):
        if type(info[i]) == list:
            for j in range(len(info[i])):
                temp = gmpy2.to_binary(info[i][j].value)
                if len(temp[2:]) != byte_len:
                    padding = byte_len - len(temp[2:])
                    new_temp = temp[2:] + (b'\x00')*padding
                else:
                    new_temp = temp[2:]
                flatten += new_temp
        else: 
            temp = gmpy2.to_binary(info[i].value)
            if len(temp[2:]) != byte_len:
                padding = byte_len - len(temp[2:])
                new_temp = temp[2:] + (b'\x00')*padding
            else:
                new_temp = temp[2:]
            flatten += new_temp
    return flatten

def deserial(info, c_info): 
    seperate = []
    for i in range(0, len(info), byte_len):
        countzeros = 0
        for j in info[i:i+byte_len]: 
            if j == b'\x00':
                countzeros += 1
        convert = Value(gmpy2.from_binary(b'\x01\x01'+info[i+countzeros:i+16]))
        seperate += [convert]
    mult_gate, num_inputs, output_num, n_parties = c_info['n_mul'], c_info['n_input'], c_info['n_output'], c_info['n_parties']
    e_inputs = [seperate[i] for i in range(0, num_inputs)]
    e_z = [seperate[i] for i in range(num_inputs, num_inputs+mult_gate)]
    var = num_inputs+mult_gate
    ez_hat = [seperate[i] for i in range(var, var+mult_gate)]
    var = var+mult_gate
    output_shares = [seperate[i] for i in range(var, var+n_parties)]
    var = var+n_parties
    zeta = [seperate[i] for i in range(var, var+n_parties)] 
    var = var+n_parties
    little_alpha = [seperate[i] for i in range(var, var+mult_gate)]
    var = var+mult_gate
    big_alpha = [seperate[i] for i in range(var, var+n_parties)]
    return [e_inputs, e_z, ez_hat, output_shares, zeta, little_alpha, big_alpha]
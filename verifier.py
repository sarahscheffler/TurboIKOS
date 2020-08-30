from secrets import token_bytes

import sys
import hashlib
from Value import Value
from Crypto.Util.number import bytes_to_long, long_to_bytes


def check_commitments(views, committed_views, broadcast, committed_broadcast):
    """NOTE: include the r value later, not sure how it's going to be given"""
    #check that information from round 1 was not tampered with (views to committed_views)
    round_1_check = b''
    input_str = b''
    input_lam_str = b''
    lam_z_str = b''
    lam_y_hat_str = b''
    lam_z_hat_str = b''
    for party in view:
        for item in party:
            if item == 'input':
                for item_value in item:
                    input_str += long_to_bytes(item_value.value)
            if item == 'input lambda':
                for item_value in item:
                    input_lam_str += long_to_bytes(item_value.value)
            if item == 'lambda z':
                for item_value in item:
                    lam_z_str += long_to_bytes(item_value.value)
            if item == 'lambda y hat':
                for item_value in item:
                    lam_y_hat_str += long_to_bytes(item_value.value)
            if item == 'lambda z hat':
                for item_value in item:
                    lam_z_hat_str += long_to_bytes(item_value.value)
    round_1_check = input_str + input_lam_str + lam_z_str + lam_y_hat_str + lam_z_hat_str
            

    #check that information from round 3 was not tampered with (views to committed_views)
    round_3_check = b''
    for item in broadcast:
        if item == 'alpha':
            alpha_array = broadcast['alpha']
            n = len(alpha_array)
            m = len(alpha_array[0])
            for i in range(n):
                for j in range(m):
                    round_3_check += long_to_bytes(alpha_array[i][j].value)
        else:
            for item_value in item:
                round_3_check += long_to_bytes(item_value.value)

    """NOTE: i need to initialize variable r in line below before"""
    assert(hashlib.sha256(r+round_1_check).hexdigest() == committed_views) and (hashlib.sha256(r+round_3_check).hexdigest() == committed_broadcast)
    return 1

def check_zeta(broadcast): 
    #check \zeta == 0
    check_zero = Value(0)
    zeta = broadcast['zeta']
    assert(sum(zeta) == check_zero)
    return 1 

def recompute(n_parties, n_gate, n_input, circuit, wire, alpha, zeta, views, broadcast):
    #round 1
    test_views = [None]*n_parties

    for j in range(n_parties):
        pass

    assert (test_views == views) 

    pass

def check_recompute():
    pass

def check_ouput():
    pass


def verifier():
    pass


# d = {'r': ['1', '2', '3'], 'e z': [0, 12, 3]}
# print(d['r'][0])
# for item in d:
#     for thing in d[item]:
#         print(item, thing)
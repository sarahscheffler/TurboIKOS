import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from math import log2, ceil
import sys

from soundness import *

matplotlib.rcParams['figure.figsize'] = (8, 7)

# Turn on or off the (N-1)/N trick.
def PARTY_OFFSET(parties):
    return (parties-1)/parties
    #return 1

kkw_options = {128: {4: (218, 65), 8: (252, 44), 16: (352, 33), 32: (462, 27), 64: (631, 23), 128: (916, 20), 31: (397, 28)},
        256: {4: (456, 129), 8: (533, 87), 16: (781, 65), 32: (1024, 53), 64: (1662, 44), 128: (2540, 38), 31: (784, 56)},
        192: {8: (321, 69), 16: (419, 52), 31: (591, 42), 32: (578, 42)}}

TI_ZC_REPS = int(sys.argv[1])
#TI_ZC_REPS = 4

# AES-128
#testin = 200
#INPUTSIZE = int(128/8)
#SOUNDNESS = int(128/8) # measured in bytes
# AES-128
testin = 416
INPUTSIZE = int(192/8)
SOUNDNESS = int(192/8) # measured in bytes
# AES-256
#testin = 500
#INPUTSIZE = int(256/8)
#SOUNDNESS = int(256/8) # measured in bytes

PARTIES = 32
do_kkw = True
HASHLEN = 2*SOUNDNESS
SDLEN = SOUNDNESS
COMLEN = 2*SOUNDNESS
FIELD = int(8/8)
REPS = ceil((SOUNDNESS*8)/log2(PARTIES)) + 1
TI_REPS = zc_reps_to_ti_reps(TI_ZC_REPS, PARTIES, SOUNDNESS*8, FIELD)
if do_kkw:
    KKW_PP_REPS = kkw_options[SOUNDNESS*8][PARTIES][0]
    KKW_REPS = kkw_options[SOUNDNESS*8][PARTIES][1]
print("TI reps: ", TI_REPS)
print("TI ZC reps: ", TI_ZC_REPS)
if do_kkw:
    print("KKW reps: ", KKW_REPS)
    print("KKW PP reps: ", KKW_PP_REPS)
print("BN reps: ", REPS)
leaveearly = True
SQGATES = 0


# KKW ia.cr/2018/475 page 12
def kkw_equation(soundness, kkw_reps, pp_reps, parties, mulgates, inputsize, field):
    return 2*soundness + \
            kkw_reps*3*soundness*(log2(pp_reps / kkw_reps)) + \
            PARTY_OFFSET(parties)*kkw_reps*field*(1*mulgates + inputsize) + \
            kkw_reps*field*mulgates + \
            kkw_reps*(3*soundness + soundness*ceil(log2(parties)))

# BN ia.cr/2019/532 page 20
def bn_equation(hashlen, sdlen, comlen, reps, parties, mulgates, sqgates, inputsize, field):
    return 2*hashlen + sdlen*(2 + reps*log2(parties)) + comlen*reps + \
            reps*field*PARTY_OFFSET(parties)*(2*mulgates + 2*sqgates + inputsize) + \
            reps*field*(2*mulgates + sqgates + 2)

def turboikos_equation(hashlen, sdlen, reps, parties, mulgates, inputsize, field, ti_zc_reps):
    return 2*hashlen + \
            reps*field*PARTY_OFFSET(parties)*(inputsize + mulgates) + \
            reps*field*1*mulgates + \
            reps*sdlen*(ceil(log2(parties)) + 1) + \
            reps*((parties-1)*ti_zc_reps*field + hashlen)


if do_kkw:
    def kkw_eq(mulgates, inputsize=INPUTSIZE):
        return kkw_equation(SOUNDNESS, KKW_REPS, KKW_PP_REPS, PARTIES, 
                mulgates, inputsize, FIELD)

def bn_eq(mulgates, sqgates=SQGATES, inputsize=INPUTSIZE):
    return bn_equation(HASHLEN, SDLEN, COMLEN, REPS, PARTIES, 
            mulgates, sqgates, inputsize, FIELD)
def ti_eq(mulgates, inputsize=INPUTSIZE):
    return turboikos_equation(HASHLEN, SDLEN, TI_REPS, PARTIES, 
            mulgates, inputsize, FIELD, TI_ZC_REPS)


# Print an example just to compare one thing easily
if do_kkw:
    print("KKW: ", kkw_eq(testin))
print(" BN: ", bn_eq(testin))
print(" TI: ", ti_eq(testin))


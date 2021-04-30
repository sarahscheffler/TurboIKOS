import csv
from soundness import *
from compare_eqns import turboikos_equation
from math import ceil

filename = "data/best_turboikos_aes128.csv"
with open(filename, "a",newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["parties","ti_reps","ti_zc_reps","proof_size"])

ti_xs = range(3, 129)
def get_best_turboikos(parties):
    soundness = int(128/8)
    field = 1
    (mulgates, inputsize) = (200, int(128/8))
    attempts = []
    zc_repss = list(range(1,16))
    ti_repss = []
    for zc_reps in zc_repss:
        ti_reps = zc_reps_to_ti_reps(zc_reps, parties, soundness*8, field)
        ti_repss.append(ti_reps)
        attempts.append(turboikos_equation(2*soundness, soundness, ti_reps, parties,
            mulgates, inputsize, field, zc_reps)) 
    rind = attempts.index((min(attempts)))
    with open(filename, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([parties, ti_repss[rind], zc_repss[rind], ceil(attempts[rind])])
    return ceil(min(attempts))

for p in ti_xs:
    get_best_turboikos(p)

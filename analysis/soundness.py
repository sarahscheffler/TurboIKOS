from scipy.stats import binom
from math import log

def cdfRighttail(n, k, p):
    values = [binom.pmf(v, n, p) for v in range(k, n+1)]
    return sum(values)

def lg(value):
    return log(value, 2)

def costFunc(numParties,fieldSize,reps, prob):
    logCosts = [lg(1.0/cdfRighttail(reps, T, prob) + numParties ** (reps-T)) for T in range(0, reps+1)]
    return min(logCosts)

def zc_reps_to_ti_reps(zc_reps, numParties, soundness, fieldbytes):
    fieldSize = 256**fieldbytes
    p = 1.0/(fieldSize**zc_reps) # prob that Prover doesn't have to break alpha/Zeta in one iteration
    for numReps in range(16,soundness+2):
        currentCostFunc = costFunc(numParties,fieldSize,numReps,p)
        #print(zc_reps, numReps, "(and the soundness achieved:)", currentCostFunc)
        if(currentCostFunc >= soundness):
            return numReps






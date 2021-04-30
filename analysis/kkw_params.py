from math import comb, log2, ceil

def inside_max(k, M, n, t):
    return (comb(k, M-t)) / (comb(M, M-t)*n**(k-M+t))

def the_soundness(M, n, t):
    options = [inside_max(k, M, n, t) for k in range(M-t, M+1)]
    return log2(max(options))

def PARTY_OFFSET(parties):
    return (parties-1)/parties

def kkw_equation(soundness, kkw_reps, pp_reps, parties, mulgates, inputsize, field):
    return 2*soundness + \
            kkw_reps*3*soundness*(log2(pp_reps / kkw_reps)) + \
            PARTY_OFFSET(parties)*kkw_reps*field*(1*mulgates + inputsize) + \
            kkw_reps*field*mulgates + \
            kkw_reps*(3*soundness + soundness*ceil(log2(parties)))

def s(M,t):
    return int(-the_soundness(M,N,t)) # should round down

def find_best(N):
    best = (200000000, 0, 0)
    for Mopt in range(570, 571):
        for topt in range(39, 40):
            soundness = s(Mopt, topt)
            #print(soundness)
            if soundness < 192:
                continue
            size = kkw_equation(soundness, topt, Mopt, N, 416, int(192/8), 1)
            if size < best[0]:
                best = (size, Mopt, topt)
                #print(best)
    #print(best)
    return best

for N in range(3, 100):
    temp = find_best(N)
    if temp[0] < 200000000:
        print(N)
        break


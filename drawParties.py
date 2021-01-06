import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import math
from benchmarking import benchmarking


p = []
v = []
s = []
m = []
r = []
num_parties = [3, 10, 100, 1000, 10000, 100000]
for i in num_parties:
    tempP, tempV, tempS, tempM, rep = benchmarking(i)
    p.append(tempP)
    v.append(tempV)
    s.append(tempS/(10**6))
    m.append(tempM/(10**6))
    r.append(rep)

# 2x2 x-y plot
def plotTable():
    fig, axs = plt.subplots(2, 2, constrained_layout=True)
    plotSize(axs[0, 0],num_parties,s)
    plotMemory(axs[0, 1],num_parties,m)
    plotPTime(axs[1, 0],num_parties,p)
    plotVTime(axs[1, 1],num_parties,v)
    plt.savefig('graph/test.jpg')
    #  plt.show()


def plotSize(ax, x, y):
    ax.plot(x, y, label = 'proof size')
    ax.plot(x, r, label = '# repetitions')
    ax.set_xlabel('number of parties', fontsize=12)
    ax.set_ylabel('proof size (in MB)/# reps', fontsize=12)
    ax.set_title('Proof Size', fontsize=14)
    ax.legend()


def plotMemory(ax, x, y):
    ax.plot(x, y)
    ax.set_xlabel('number of parties', fontsize=12)
    ax.set_ylabel('memory usage (in MB)', fontsize=12)
    ax.set_title('Memory Usage', fontsize=14)

    
def plotPTime(ax, x, y):
    ax.plot(x, y)
    ax.set_xlabel('number of parties', fontsize=12)
    ax.set_ylabel('prover time (in s)', fontsize=12)
    ax.set_title('Prover Time', fontsize=14)


def plotVTime(ax, x, y):
    ax.plot(x, y)
    ax.set_xlabel('number of parties', fontsize=12)
    ax.set_ylabel('verifier time (in s)', fontsize=12)
    ax.set_title('Verifier Time', fontsize=14)

   
# other methods
def log2arr(arr):
    ret = []
    for i in arr:
        ret.append(math.log(i, 2))
    return ret


plotTable()

"""
# comparision table
def tableCompare(circuit_size, p_time, v_time, memory):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    row = ['Proof Size', 'Prover Time', 'Verifier Time', 'Memory Used']
    col = ['libSNARK','This work']
    values=[['0.13KB', circuit_size+'MB'],
            ['360s', p_time+'s'],
            ['0.002s', v_time+'s'],
            ['\u2265 10GB', memory+'MB']]
    table = plt.table(cellText = values,
                      rowLabels = row,
                      colLabels = col,
                      loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(0.5, 3)
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
    for pos in ['right','top','bottom','left']:
        plt.gca().spines[pos].set_visible(False)
    # plt.savefig('matplotlib-table.png', bbox_inches='tight', pad_inches=0.05)
    plt.show()

    
# comparison histogram
def plotHist():   
    labels = ['naive', 'Turbospdz', 'pseudor', 'alpha val']
    old_means = [20, 34, 30, 35]
    new_means = [25, 32, 34, 20]

    x = np.arange(len(labels))  # the label locations
    width = 0.4  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, old_means, width, label='Old')
    rects2 = ax.bar(x + width/2, new_means, width, label='New')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Space')
    ax.set_title('Space comparison for each optimization made')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()


    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')


    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()
    plt.show()
"""


DATA = "/data/dave/"
import os, re
import scipy as sp
from everySNAKE.utils import sigsmooth as ss
from numpy import *

loop_fa = os.path.join(DATA,"stemloop1.fa")
hotair_ss = os.path.join(DATA, "sfold/hotair/probprof/sstrand.out")
fendrr_ss = os.path.join(DATA, "sfold/fendrr/probprof/sstrand.out")

def run0():
    from matplotlib import pyplot as plt
    with open(fendrr_ss) as f:
        prbs = [float(re.compile("\s+").split(row)[4]) for row in f.readlines()]
    plt.clf()
    f = plt.figure(1)
    ax = f.add_subplot(111)
    ax.set_xlabel("base")
    ax.set_ylabel("pairing probability smoothed 100bp")
    ax.set_title("fendrr pairing probability")

    n = len(prbs)
    print n

    plt.plot(arange(n),prbs,alpha=.2);
    
    sm = 50
    plt.plot(arange(sm,n-sm),ss.smooth(array(prbs),sm)[sm:n-sm], lw=5);

    sm = 100
    plt.plot(arange(sm,n-sm),ss.smooth(array(prbs),sm)[sm:n-sm], lw=10, color = "red");

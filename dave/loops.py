'''
Analysis of the RNA stem loops in fendrr, NoRC pRNA, MBDSL, and HOTAIR
'''

from everySNAKE.utils import muscle
from Bio import SeqIO
import os

DATA = "/data/dave/loops"
DATA_OUT = os.path.join(DATA,"out")
if not os.path.isdir(DATA_OUT):
    os.makedirs(DATA_OUT)

loop_fa = os.path.join(DATA,"stemloop1.fa")
loops6_fa = os.path.join(DATA, "MS2-6x.fa")
fendrr_fa = os.path.join(DATA,"fendrr.fa")
hotair_gb = os.path.join(DATA,"hotair.gb")
msl_draper_fa = os.path.join(DATA,"msl_draper.fa")
msl_lim_fa = os.path.join(DATA,"msl_lim.fa")


loop = SeqIO.read(loop_fa,"fasta")
loops6 = SeqIO.read(loops6_fa,"fasta")
fendrr = SeqIO.read(fendrr_fa,"fasta")
hotair = SeqIO.read(hotair_gb,"genbank")
msl_draper = SeqIO.read(msl_draper_fa,"fasta")
msl_lim = SeqIO.read(msl_lim_fa,"fasta")

def run0():
    '''analyzes MSL stem loop potential in a slew of lncRNAs'''
    
    names = "msl_lim","fendrr"
    ali = muscle.align([globals()[n] for n in names])
    with open(os.path.join(DATA_OUT, "run0_ali_{0}".format("x".join(sorted(names)))),"w") as f:
        f.write(ali.format("fasta"))

    return ali




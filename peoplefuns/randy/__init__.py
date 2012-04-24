lookups = {'mouse':'/data/blast/test_m_est.fa.gz'}

#Biopython module SeqIO will handle parsing.
import Bio.SeqIO as sio
import gzip
import everySNAKE.utils.memo as mem

def parse(libname):
    fpath = lookups[libname]
    handle = gzip.open(fpath)
    seqs = sio.parse(handle, 'fasta')

    counts = {}
    k = 8
    for s in seqs:
        for i in range(0,len(s )- k):
            window = ''.join(s[i:i+k])
            counts[window] = counts.get(window, 0) + 1
        break
    return counts

def getKMERsForName(libname):
    def setKMERsForName(**kwargs):
        lname = kwargs['libname']
        return parse(libname)

    return mem.getOrSet(setKMERsForName, 
                        libname = libname,
                        name = libname)

def view(libname):
    pass

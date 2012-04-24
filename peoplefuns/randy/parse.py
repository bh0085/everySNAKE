lookups = {'mouse':'/data/blast/test_m_est.fa.gz'}

#Biopython module SeqIO will handle parsing.
import Bio.SeqIO as sio
import gzip, json, re
import everySNAKE.utils.memo as mem

k = 8
translation = {'A':0.,'T':1.,'G':2.,'C':3.};

def parse(libname = 'mouse',tissue_term = None, **kwargs):
    '''Parse the file specified by libname. If a tissue term is provided, only catalog matching records'''
    global k
    fpath = lookups[libname]
    handle = gzip.open(fpath)
    seqs = sio.parse(handle, 'fasta')

    counts = {}
    max_count = 1000000
    added = 0 ;
    tt_re = None if tissue_term == None else re.compile(tissue_term, re.I)
    for j, s in enumerate(seqs):
        if tissue_term != None:
            if tt_re.search(s.description) == None:
                continue
        
        added+= 1;
        for i in range(0,len(s )- k):
            
            window = ''.join(s[i:i+k])
            counts[window] = counts.get(window, 0) + 1
        
        if added > max_count: break
        if added % 1000 == 0: print "Completion: {0}".format(float(added) / max_count)
    return counts

def getKMERsForName(libname = 'mouse',tissue_term = None, **kwargs):
    '''
Calls "parse" on the fasta file referred to as libname.

Optionally, specify a tissue term that will serve as a regex filter on the 
FASTA record descriptors. Specifying a term such as "brain" will do
a case insensitive search on records in the library to return only kmers
from records matching "term".
'''
    def setKMERsForName(**kwargs):
        lname = kwargs['libname']
        return parse( **kwargs)

    
    name = libname if tissue_term ==None \
        else '{0}_tissue={1}'.format(libname,tissue_term) 

    return mem.getOrSet(setKMERsForName, 
                        **mem.rc(kwargs,
                                 libname = libname,
                                 tissue_term = tissue_term,
                                 name = name))

def getTranslatedForName(libname, **kwargs):
    '''Translate kMERs to a numerical array for downstream analysis.'''
    def setTranslatedForName(**kwargs):
        global k
        global translation
        libname = kwargs.get('libname')
        o = getKMERsForName( **mem.sr(kwargs, libname = libname))
        translated = zeros((len(o),k))
        idxed_mers = dict([(i,k) for i,k in enumerate(o.keys())])
        occurrences=array([ o[idxed_mers[i]] for i in range(len(translated))])
        d = translation
        for i in idxed_mers.keys():
            translated[i] = [d.get(l,4) for  l in idxed_mers[i]]
        return idxed_mers,translated, occurrences
    tissue_term = kwargs.get('tissue_term', None)
    name = libname if tissue_term ==None \
        else '{0}_tissue={1}'.format(libname,tissue_term) 

    return mem.getOrSet(setTranslatedForName, 
                        **mem.rc(kwargs,
                                 libname = libname,
                                 name = name))


def writeResultsToJSON(libname, tissue_term = None):
    '''Write computed kmer for lib name.'''
    kmers = getKMERsForName(libname, tissue_term = tissue_term)
    f = open('{0}mers_tt={1}.json'.format(k,tissue_term),'w')
    f.write(json.dumps(kmers))
    f.close()

from numpy import *
import numpy as np
def view(libname):
    import matplotlib.pyplot as plt
    import scipy.stats as ss
    f1= plt.figure(1)
    f2= plt.figure(2)
    f3= plt.figure(3)
    f4= plt.figure(4)
    f1.clear(); f2.clear(); f3.clear(); f4.clear();
    ax1 = f1.add_subplot(111)
    ax2 = f2.add_subplot(111)
    ax3 = f3.add_subplot(111)
    ax4 = f4.add_subplot(111)

    ax1.set_title("Histogram of log frequency of {0}mer occurrence".format(k))
    ax1.set_xlabel('log frequency')
    ax1.set_ylabel('# of mers in frequency bin')

    ax2.set_title("Frequency skew towards low entropy kmers")
    ax2.set_xlabel("Occurrences")
    ax2.set_ylabel("Entropy")
    
    ax3.set_title("Frequency skew vs. GC content")
    ax4.set_title("Frequency skew vs. A content. Colored by GC.")
    ax3.set_xlabel("Occurrences")
    ax4.set_xlabel("Occurrences")
    ax3.set_xlabel("GC%")
    ax4.set_xlabel("A%")

    
    idxed_mers,translated, occurrences = getTranslatedForName(libname)
    skip = 50
    entropies =array([ ss.entropy(row) for row in translated[::skip]])
    gc = np.sum(equal(translated,2)+equal(translated,3),1)
    a = np.sum(equal(translated,0),1)

    ax1.hist(log(occurrences[::skip]))
    ax2.scatter(log(occurrences[::skip]), entropies, 20,alpha = .3)
    ax3.scatter(log(occurrences[::skip]), gc[::skip], 20, alpha=.3)
    ax4.scatter(log(occurrences[::skip]), a[::skip],20,
                color = array([1.,0.,0.])[newaxis,:] * (a[::skip,newaxis] / max(a))) 
    
    
    for i, f in enumerate([f1,f2,f3,f4]):
        f.savefig( 'fig{0}_{1}_skip={2}.pdf'.format(i,libname,skip))
                    

import everySNAKE.config as cfg, everySNAKE.utils.memo as mem
import track
from numpy import *
import os
import numpy as np
mousefile = cfg.dataPath('silvana/mouse_genes.bed')
peakfile = cfg.dataPath('silvana/dhs.narrowPeak')


def getTrackChrPromoters(**kwargs):
    '''
Get all of the forward promoter from a bed file
on a given chromosome>

kwargs
num:   chromosome number 
fname: bedfile path

returns
a list of the coordinates of each forward promoter.
'''
    def setTrackChrPromoters(**kwargs):
        fname = kwargs.get('fname', mousefile)
        num = kwargs.get('num', 1)
        t = track.load(fname);
        chromosome_data = t.read('chr{0}'.format(num))
        rows = [dict(zip(r.keys(),r.data)) for r in iter(chromosome_data)]
        fwd_genes = [e for e in rows if e['strand'] == 1]
        fwd_starts =dict([(e['name'],e['start']) for e in fwd_genes])
        fwd_promoters= dict([(k, [v - 2000, v - 100])
                             for k,v in fwd_starts.iteritems()])
        return fwd_promoters
    
    return mem.getOrSet(setTrackChrPromoters,
                        onfail = 'compute',
                        name = '{0}_{1}'.format(kwargs.get('fname',os.path.basename(mousefile)),
                                                kwargs.get('num', 1)))


def getTrackChrGenes(**kwargs):
    '''
Get all of th genes from a bed file
on a given chromosome.

kwargs
num:   chromosome number 
fname: bedfile path

returns
a list of attributes for every gene.
'''
    def setTrackChrGenes(**kwargs):
        fname = kwargs.get('fname', mousefile)
        num = kwargs.get('num', 1)
        t = track.load(fname);
        chromosome_data = t.read('chr{0}'.format(num))
        rows = [dict(zip(r.keys(),r.data)) for r in iter(chromosome_data)]
        return rows
    
    return mem.getOrSet(setTrackChrGenes,
                        **mem.rc( kwargs,
                                  onfail = 'compute',
                                  name = '{0}_{1}'.format(kwargs.get('fname',os.path.basename(mousefile)),
                                                          kwargs.get('num', 1))
                                  ))



def getPeaks():
    '''
Get all of peaks from a narrowpeak file 
on all chromosomes.

kwargs
none:

returns
a list of peaks.
'''
    def setPeaks(**kwargs):
        peaks = {}
        with open(peakfile) as pf:
            for l in pf.readlines():
                grps = l.split('\t')
                cols = ['chrom',
                    'start',
                    'end',
                    'name',
                    'score',
                    'strand',
                    'signalValue',
                    'pValue',
                    'qValue',
                    'peak']

            #note, peak is a zero based offset from start
                hit = dict(zip(cols[1:],grps[1:]))
                hit['start'] = int(hit['start'])
                hit['end'] = int(hit['end'])
                hit['peak'] = int(hit['peak'])
                
                if not peaks.has_key(grps[0]):
                    peaks[grps[0]] = []
                peaks[grps[0]].append(hit)

        return peaks
    return mem.getOrSet(setPeaks,
                        onfail = 'compute')


def mapAllGenes(**kwargs):
    def setAllGenes(**kwargs):
       allPeaks = getPeaks()
       all_results = {}
       for num in range(1,20) + ['X']:
           print 'Parsing Chromosome: chr{0}'.format(num)
           genes_dict = {}
           all_results['chr{0}'.format(num)] = genes_dict
           chrgenes = getTrackChrGenes(**mem.sr(kwargs, num = num))

           peaks = allPeaks['chr{0}'.format(num)]
           for i, g in enumerate(chrgenes):
               name = g['name']
               startpos = g['start'] if g['strand'] == 1 else g['end']
               hits = []
               for p in peaks:
                   stranded_offset =array([ g['strand'] * (p['start']  - startpos),
                                           g['strand'] * (p['end'] - startpos)])
                   if( np.min(abs(stranded_offset)) < 2000 \
                           or np.prod(stranded_offset) < 0):
                       stranded_offset.sort()
                       hits.append({'peak_info':p,
                                  'peak_stranded_offset':stranded_offset})
               
               hits = sorted(hits,key = lambda x: x['peak_stranded_offset'][0])
               gene_object = {
                   'dnase_peaks':hits,
                   'name':name,
                   'gene_info':g,
                   'start':g['start'],
                   'end':g['end'],
                   'strand':g['strand']
                   }
               genes_dict[name] = gene_object

               if (mod(i,100) == 0):
                   print 'Gene {0}: {1}, {2} hits'.format(i, g['name'], len(hits))
       
       return all_results;
    return mem.getOrSet(setAllGenes, **kwargs)
        

def plotPeaks(num = 1):
    import cb.utils.plots as myplots

    def setHist(**kwargs):
     peaks = getPeaks()['chr{0}'.format(num)]
     proms = getTrackChrPromoters(num = num)
     
     all_hits = zeros(20)
     for k,v in proms.iteritems():
         mid =(v[0] + v[1]) / 2
         deltas = []
         for p in peaks:
             pmid = (p['start'] + p['end'])/2
             if abs(pmid - mid) < 5000:
                 deltas.append(pmid - mid)
         hits, bin_offsets = histogram(deltas, 20, [-5000,5000])
         all_hits += hits;
     return bin_offsets, all_hits;
    bin_offsets, hits = mem.getOrSet(setHist, 
                                     num = num)
    f = myplots.fignum(1)
    ax = f.add_subplot(111)
    ax.set_xlabel('distance from promoter')
    #ax.set_xticks(bin_offsets)
    #ax.set_xticklabels(['{0}'.format(e) for e in bin_offsets])
    ax.set_ylabel('counts')
    ax.plot(bin_offsets[:-1],hits)
    

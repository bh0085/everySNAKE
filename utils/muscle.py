from Bio import SeqIO
import subprocess
import sys
from Bio.Align.Applications import MuscleCommandline
from Bio import AlignIO

def align(records):  
  '''Then we create the MUSCLE command line, leaving the input and 
  output to their defaults (stdin and stdout). I'm also going to 
  ask for strict ClustalW format as for the output.'''
  
  muscle_cline = MuscleCommandline(clwstrict=True)
  print muscle_cline
  
  '''
  Now comes the clever bit using the subprocess module, stdin and stdout:
  '''
  
  child = subprocess.Popen(str(muscle_cline),
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           shell=(sys.platform!="win32"))                     
  '''
  That should start MUSCLE, but it will be sitting waiting for 
  its FASTA input sequences, which we must supply via its stdin handle:
  '''
  
  SeqIO.write(records, child.stdin, "fasta")
  child.stdin.close()
  
  '''
  After writing the six sequences to the handle, MUSCLE will still be waiting to see if that is all the FASTA sequences or not - so we must signal that this is all the input data by closing the handle. At that point MUSCLE should start to run, and we can ask for the output:
  '''

  align = AlignIO.read(child.stdout, "clustal")
  for idx, r in enumerate(records):
    align[idx].name = r.name
  return align

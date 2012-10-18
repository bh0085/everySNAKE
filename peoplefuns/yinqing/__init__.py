import gzip, os

path = "/data/yinqing/"
fname = os.path.join(path, "mouse_chr1.fa.gz")
fopen = gzip.open(fname)

for i in range(100):
    content = fopen.read(size = 10000)
    #read back 1000
    fopen.seek(fopen.tell() - 1000)

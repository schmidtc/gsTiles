import time
shp = '/Users/charlie/Documents/data/Seattle/parcel2000_city_resbldg99clean.shp'
BLOCK = 4096

def timeit(func):
    t0 = time.time()
    ret = func()
    t1 = time.time()
    print (t1-t0)*1000, (t1-t0)*1000 / 166941.

def oneshot():
    f = open(shp,'rb', 20*BLOCK)
    dat = f.read()
def chunked(chunksize=1024):
    def func():
        f = open(shp,'rb', 20*BLOCK)
        dat = f.read(chunksize)
        while dat:
            dat = f.read(chunksize)
    return func
def chunked2(chunksize=1024):
    def func():
        f = open(shp,'rb', 20*BLOCK)
        dat = f.read(chunksize)
        while dat:
            dat = f.read(chunksize)[100:]
    return func
def seekandread(chunksize=20*4096):
    f = open(shp,'rb', 20*BLOCK)
    dat = f.read(chunksize)
    offset = 100
    while dat:
        #f.seek(offset)
        f.seek(100,1)
        dat = f.read(chunksize)
        offset += (100 + chunksize)
def seekandread_bak():
    f = open(shp,'rb')
    offset = 100
    for x in xrange(166941):
        f.seek(offset)
        dat = f.read(40)
        offset += 100

if __name__=='__main__':
    timeit(oneshot)
    #for i in xrange(1,100):
    #    f = chunked(BLOCK * i)
    #    print '\t',i,BLOCK * i
    #    timeit(f)
    #for i in xrange(1,20):
    #    f = chunked(BLOCK * i + 1)
    #    print '\t',i,BLOCK * i + 1
    #    timeit(f)
    #timeit(chunked())
    #timeit(chunked(20*BLOCK))
    timeit(chunked2(20*BLOCK))
    #timeit(chunked(8192))
    #timeit(chunked(4096*10))
    timeit(seekandread)
    #timeit(seekandread_bak)

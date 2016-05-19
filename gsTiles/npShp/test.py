import time
from pysal.core.util.shapefile import shp_file
from shpReader import shapeFile
import pysal

#shp = '/Users/charlie/Documents/data/Seattle/parcel2000_city_resbldg99clean.shp'
shp = '/Users/charlie/Documents/data/blkgrps/blkgrps.gmerc.shp'

def timeit(func):
    t0 = time.time()
    ret = func()
    t1 = time.time()
    print func.__name__, t1-t0, (t1-t0)*1000 / 166941.

def baseline():
    f = open(shp,'rb')
    dat = f.read(1024)
    while dat:
        dat = f.read(1024)

def npShape():
    f = shapeFile(shp)
    for record in f.shapes():
        pass

def pythonShape():
    f = shp_file(shp,'r')
    for record in f:
        pass

def pysalShape():
    f = pysal.open(shp,'r')
    for record in f:
        pass
def pysalDBF():
    f = pysal.open(shp[:-3]+'dbf','r')
    for record in f:
        pass



if __name__=='__main__':
    timeit(baseline)
    timeit(baseline)
    timeit(npShape)
    #timeit(pythonShape)
    #timeit(pysalShape)
    #timeit(pysalDBF)

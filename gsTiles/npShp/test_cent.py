import time
from pysal.core.util.shapefile import shp_file
from shpReader import shapeFile, point_in_polygon
import numpy
import pysal

#shp = '/Users/charlie/Documents/data/Seattle/parcel2000_city_resbldg99clean.shp'
#shp = '/Users/charlie/Documents/data/blkgrps/blkgrps.gmerc.shp'
#shp = '/Users/charlie/Documents/data/stl_hom/stl_hom.shp'
shp = '/Users/charlie/Documents/data/usa/usa.gmerc.shp'
s = shapeFile(shp)
boxes = s.allboxes()
pts = numpy.zeros((boxes.shape[0], 2))
pts[:,0] = boxes[:,2]+boxes[:,0]
pts[:,1] = boxes[:,3]+boxes[:,1]
pts = pts * 0.5
polys = list(s.shapes())

f = pysal.open(shp,'r')
polys2 = f.read()
pts2 = pts.tolist()

def profileit(log_file=None, sortby='time', callers=True, callees=False):
    """
    See: http://stackoverflow.com/questions/5375624/a-decorator-that-profiles-a-method-call-and-logs    -the-profiling-result
    """
    def _profiler(func):
        def _wrapper(*args, **kwargs):
            import cProfile, pstats, time, sys
            prof = cProfile.Profile()
            retval = prof.runcall(func, *args, **kwargs)
            stats = pstats.Stats(prof)
            #"calls"     : "call count"
            #"cumulative": "cumulative time"
            #"file"      : "file name"
            #"line"      : "line number"
            #"module"    : "file name"
            #"name"      : "function name"
            #"nfl"       : "name/file/line"
            #"pcalls"    : "call count"
            #"stdname"   : "standard name"
            #"time"      : "internal time"
            stats.sort_stats(sortby)
            if log_file:
                stats.stream = open(log_file,'w')
            else:
                stats.stream = sys.stdout
            stats.print_stats()
            if callers:
                stats.print_callers()
            if callees:
                stats.print_callees()
            if log_file:
                stats.stream.close()
            #prof.dump_stats(log_file)
            return retval
        return _wrapper
    return _profiler

def timeit(func):
    t0 = time.time()
    ret = func()
    t1 = time.time()
    print func.__name__, t1-t0, (t1-t0)*1000 / 166941.

#@profileit()
def npShape():
    return [point_in_polygon(pt, poly) for pt,poly in zip(pts, polys)]

#@profileit()
def pysalShape():
    return [poly.contains_point(pt) for pt,poly in zip(pts2, polys2)]

if __name__=='__main__':

    #npShape()
    #pysalShape()

    #timeit(baseline)
    #timeit(baseline)
    timeit(npShape)
    #timeit(pythonShape)
    timeit(pysalShape)
    #timeit(pysalDBF)

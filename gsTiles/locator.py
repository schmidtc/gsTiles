import time
import rtree
from simple import simple


class BBoxLocator(object):
    """
    contains_point() will return a list of areas whose bonding boxes contain the point, and is much faster 
        -- benchmark: query 74001 centroids: 5.7439 seconds (13,000 queries per second)
    """
    def __init__(self, source):
        self.source = source

        idx = rtree.index.Index()
        if hasattr(source,'boxes'):
            def f():
                for i,bb in enumerate(source.allboxes()):
                    yield (i, bb, None)
            idx = rtree.index.Index(f())
            #for i,bb in enumerate(source.boxes()):
            #    idx.insert(i, bb)
        else:
            for i,rec in enumerate(source):
                idx.insert(i, rec.bbox)
        self.idx = idx
    def clone(self):
        import copy
        other = copy.copy(self)
        other.source = self.source.clone()
        return other
    @property
    def extent(self):
        return self.source.bbox
    def overlapping(self,rect, zoom=-1):
        # prevents a memory leak...
        # rtree doesn't release the memory until we've 
        # accessed all elements in the generator
        offsets = list(self.idx.intersection(rect))
        s = self.source
        if zoom > -1:
            for o in offsets:
                yield o,simple(s.get(o), zoom)
        else:
            for o in offsets:
                yield o,s.get(o)

if __name__=='__main__':
    import time
    import pysal
    from npShp.shpReader import shapeFile
    
    shp_fname = '/Users/charlie/Documents/data/usa/usa.gmerc.shp'
    #shp_fname = '/Users/charlie/Documents/data/blkgrps/blkgrps.gmerc.shp'
    #shp = pysal.open(shp_fname,'r')
    shp = shapeFile(shp_fname)
    loc = BBoxLocator(shp)

    #getbb = lambda p: p.bbox
    #bbox_centroid = lambda b: (b[0]+b[2]/2., b[1]+b[3]/2.)
    #test_data = shp.allboxes().tolist()
    #import random
    #random.shuffle(test_data)

    #t0 = time.time()
    #for rect in test_data:
    #    loc.overlapping(rect)
    #t1 = time.time()
    #print "BBOX: (n, seconds)", len(test_data) , t1-t0


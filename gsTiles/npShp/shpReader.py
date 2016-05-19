"""
A Numpy Python ShapeFile Reader and Writer

Contact:
Charles Schmidt
"""
__author__ = "Charles R Schmidt <schmidtc@gmail.com>"
import numpy
from itertools import izip

HEADERSTRUCT = numpy.dtype([ # Starts At
    ('filecode', '>i4'),     # Byte 0
    ('unused', '(5,)>i4'),   # Byte 4
    ('File Length', '>i4'),   # Byte 24
    ('version', '<i4'),      # Byte 28
    ('Shape Type', '<i4'),      # Byte 32
    ('bbox', '<f8', 4),      # Byte 36
    ('Zrng', '<f8', 2),      # Byte 68
    ('Mrng', '<f8', 2)       # Byte 84
])
POLYGON_HEADER = numpy.dtype([('Shape Type','<i4'),('bbox','<4d8'),('NumParts','<i4'),('NumPoints','<i4')])
i2s = lambda i: numpy.array([i],  '<i4').tostring()
NULL = i2s(0)

def mean_pt(ring):
    return ring.mean(0)

def point_in_polygon(pt, poly):
    """
    Example:
    >>> part = numpy.array([(10,10), (10,-10), (-10,-10), (-10,10), (10,10)])
    >>> hole = numpy.array([(1,1), (-1,1), (-1,-1), (1,-1), (1,1)])
    >>> poly = [part, hole]
    >>> pt = numpy.array([(0,0)])
    >>> point_in_polygon(pt, poly)
    False
    >>> pt = numpy.array([(5,5)])
    >>> point_in_polygon(pt, poly)
    True
    """
    w = 0
    for ring in poly:
        w += point_in_ring2(pt, ring)
    return w != 0
def point_in_ring(pt, ring):
    """
    pt = numpy.ndarray (2,1)
    ring = numpy.ndarray (2, n)

    REF: http://www.engr.colostate.edu/~dga/dga/papers/point_in_polygon.pdf

    returns w -> {-n, 0, +n}
        0 : pt is not in ring
        +n: ring winds around pt n times in the counterclockwise direction
        -n: ring winds around pt n times in the clockwise direction

    >>> ring = numpy.array([(1,1), (1,-1), (-1,-1), (-1,1), (1,1)])
    >>> pt = numpy.array([(0,0)])
    >>> point_in_ring2(pt, ring)
    -1
    >>> ring = numpy.array([(1,1), (1,-1), (-1,-1), (-1,1), (1,1)][::-1])
    >>> point_in_ring2(pt, ring)
    1
    >>> ring = numpy.array([(1,1), (1,0),(1,-1), (-1,-1), (-1,1), (1,1)])
    >>> point_in_ring2(pt, ring)
    -1.0
    >>> ring = numpy.array([(1,1), (1,0), (2,0),(1,-1), (-1,-1), (-1,1), (1,1)])
    >>> point_in_ring2(pt, ring)
    -1.0
    """
    # Translate the polygon such that pt is the origin.
    # Algo Step 0.
    C = ring-pt

    # Algo Step 1
    w = 0

    # Algo Step 2
    # if y_i * y_i+1 < 0:
    #     y_i and y_i+1 have difference signs
    #     as such the segment crosses the x-axis
    xcross = (C[:-1, 1] * C[1:, 1]) < 0
    idx, = xcross.nonzero()
    for i in idx:
        r = C[i,0] + ((C[i,1] * (C[i+1,0] - C[i,0])) / (C[i,1] - C[i+1, 1]))
        if r > 0:
            if C[i,1] < 0:
                w +=  1
            else:
                w -=  1

        # r = x_i + ((y_i * (x_i+1 - x_i)) / (y_i - y_i+1))
        #r = C[idx,0] + ((C[idx,1] * (C[idx+1,0] - C[idx,0])) / (C[idx,1] - C[idx+1,1]))
        #return 0

    #if xcross.any(): # some segments cross the x-axis
        #i = C[:-1,:][xcross]
        #i1 = C[1:,:][xcross]
        # r == the x coord where the segment crosses the x-axis
        # r = x_i + ((y_i * (x_i+1 - x_i)) / (y_i - y_i+1))
        #r = i[:,0] + ((i[:,1] * (i1[:,0] - i[:,0])) / (i[:,1] - i1[:,1]))
        #ycoord_before_x_intersection = C[idx,1][r > 0]
        #w += (ycoord_before_x_intersection < 0).sum() # crosses from below (counter-clockwise)
        #w -= (ycoord_before_x_intersection > 0).sum() # crosses from below (counter-clockwise)
    on_x = C[:,1] == 0
    idx, = on_x.nonzero()
    for i in idx:
        if C[i+1,1] == 0:
            pass
        elif C[i,0] > 0:
            if C[i+1,1] > 0:
                w+=.5
            else:
                w-=.5
        elif C[i+1,0] > 0:
            if C[i+1,1] < 0:
                w+=.5
            else:
                w-=.5
            
    return w
    on_x = (C[:,1] == 0) & (C[:,0] > 0) # y_i is on the x-axis
    #edge case, vert is on the x-axis
    if on_x.any():
        # drop segments where both endpoints are on the x-axis
        yi_on_x  = on_x[:-1] & (on_x[:-1] ^ on_x[1:])
        yi1_on_x = on_x[1:]  & (on_x[:-1] ^ on_x[1:])

        y_i1 = C[1:,1][yi_on_x]  #grab the y-values after the y-values that fall on x
        w += (y_i1 > 0).sum() / 2.
        w -= (y_i1 <= 0).sum() / 2.

        y_i = C[:-1,1][yi1_on_x]  #grab the y-values after the y-values that fall on x
        w += (y_i < 0).sum() / 2.
        w -= (y_i >= 0).sum() / 2.

    return w

def point_in_ring2(pt, ring):
    C = ring-pt
    X = C[:,0]
    Y = C[:,1]
    w = 0
    y0 = Y == 0
    idx, = (((Y[:-1] * Y[1:]) < 0) | y0[:-1] | y0[1:]).nonzero()
    #idx, = (((Y[:-1] * Y[1:]) < 0) | (Y[:-1] == 0) | (Y[1:] == 0)).nonzero()

    for i in idx:
        if Y[i]*Y[i+1] < 0:
            r = X[i] + ((Y[i] * (X[i+1] - X[i])) / (Y[i] - Y[i+1]))
            # r = x_i + ((y_i * (x_i+1 - x_i)) / (y_i - y_i+1))
            if r>0:
                w += 1 if Y[i] < 0 else -1
        elif Y[i] == 0 and Y[i+1] == 0:
            # This step is missing from the algorithm in the paper,
            # but is mentioned earlier in the paper
            pass
        elif Y[i] == 0 and X[i] > 0:
            w += 0.5 if Y[i+1] > 0 else -0.5
        elif Y[i+1] == 0 and X[i+1] > 0:
            w += 0.5 if Y[i] < 0 else -0.5
    return w

class shapeFile(object):
    def __init__(self, filename):
        with open(filename[:-3]+'shx', 'rb') as f:
            self.head = numpy.fromstring(f.read(100), HEADERSTRUCT)
            # Shapefiles lengths and sizes are messured in 16bit words, multiple by 2 to get bytes
            # Index contains ('Offset', 'Content Length')
            self.index = 2 * numpy.fromfile(f, '2>i')
        self.f = open(filename,'rb')
        self._data = {}
        self.polyIndex()
    def clone(self):
        import copy
        other = copy.copy(self)
        other.f = open(self.f.name,'rb')
        return other
    @property
    def n(self):
        return self.index.shape[0]
    @property
    def bbox(self):
        return self.head['bbox'].tolist()[0]
    def polyIndex(self):
        """
        Much fast to read this uniform strucuted data in one shot.
        Uses more memory, but worth the speed up.
        Memory in bytes is n * 44.

        1million polygons ~ 40mb


        index fields:
            Shape Type - int (4 bytes)
            bbox - floats (32) - [minx, miny, maxx, maxy]
            NumParts - int (4)
            NumPoints - int (4)
        """
        if 'polyIndex' in self._data:
            return self._data['polyIndex']
        f = self.f
        offsets = (self.index[:,0]+8).tolist() 
        s = ''
        for rec in offsets:
            f.seek(rec)
            dat = f.read(44)
            if dat[:4] == NULL:
                s += '\x00'*44
            else:
                s += dat
        self._data['polyIndex'] = pidx = numpy.fromstring(s, POLYGON_HEADER)
        self.offsets  = (self.index[:,0] + 52).tolist()
        self.ps = (pidx['NumParts'] * 4).tolist()
        self.size = (pidx['NumParts']*4 + pidx['NumPoints']*16).tolist()
        self.ptype = numpy.dtype('uint8,2float')
        self.pt = numpy.dtype('<i4')
        self.vt = numpy.dtype('<2d8')
        s = pidx['NumPoints'].tostring()
        self.npts = [s[i:i+4] for i in xrange(0,len(s),4)]
        self.nprts = pidx['NumParts'].tolist()
        return self._data['polyIndex']
        
    def get(self,oid):
        d = self._data
        self.f.seek(self.offsets[oid])
        dat = self.f.read(self.size[oid])
        ps = self.ps[oid]
        parts = numpy.fromstring(dat[:ps] + self.npts[oid], self.pt)
        verts = numpy.fromstring(dat[ps:], self.vt)
        rec = []
        for j in xrange(self.nprts[oid]):
            rec.append(verts[parts[j]:parts[j+1]])
        return rec
    
    def shapes(self): #for Polygons only.
        f = self.f
        start = self.offsets
        sizes = self.size
        partSizes = self.ps
        npts = self.npts
        nprts = self.nprts
        
        pt = self.pt
        vt = self.vt
        ptype = self.ptype
        for i, (offset,size,ps,nparts) in enumerate(izip(start,sizes, partSizes, nprts)):
            f.seek(offset)
            dat = f.read(size)
            parts = numpy.fromstring(dat[:ps] + npts[i], pt)
            verts = numpy.fromstring(dat[ps:], vt)
            #rec = []
            yield [verts[parts[j]:parts[j+1]] for j in xrange(nparts)]
            #for j in xrange(nparts):
            #    rec.append(verts[parts[j]:parts[j+1]])
            #yield rec
            #TODO: test that the next line produces the same results as the previous 4
            #yield [verts[parts[j]:parts[j+1]] for j in xrange(nparts)]
        
    def boxes(self):
        for bb in self.polyIndex()['bbox']:
            yield bb
    def allboxes(self):
        return self.polyIndex()['bbox']
    def bbox_centroid(self):
        boxes = self.allboxes()
        pt = numpy.empty((boxes.shape[0], 2))
        pt[:, 0] = (boxes[:,0] + boxes[:,2]) / 2.0
        pt[:, 1] = (boxes[:,1] + boxes[:,3]) / 2.0
        return pt

if __name__ == '__main__':
    shp = '/Users/charlie/Documents/data/blkgrps/blkgrps.gmerc.shp'
    shx = '/Users/charlie/Documents/data/blkgrps/blkgrps.gmerc.shx'
    #shp = '/Users/charlie/Documents/data/Seattle/parcel2000_city_resbldg99clean.shp'
    #shx = '/Users/charlie/Documents/data/Seattle/parcel2000_city_resbldg99clean.shx'
    #shp = '/Users/charlie/Documents/data/usa/usa.gmerc.shp'
    #shx = '/Users/charlie/Documents/data/usa/usa.gmerc.shx'
    #shp = '/Users/charlie/Documents/data/Illinois_BlockGrps/chicago_blocks.shp'
    #shx = '/Users/charlie/Documents/data/Illinois_BlockGrps/chicago_blocks.shx'
    #f = open(shx,'rb')
    #head = numpy.fromstring(f.read(100), HEADERSTRUCT)
    #index = 2 * numpy.fromfile(f, '2>i')
    import time

    t0 = time.time()
    s= shapeFile(shp)
    t1 = time.time()
    print 'load',(t1-t0) * 1000, ((t1-t0) * 1000) / s.n

    t0 = time.time()
    c = 0
    for p in s.shapes():
        c+=1
    t1 = time.time()
    print 'read.shp ',(t1-t0) * 1000, ((t1-t0) * 1000) / s.n, c

    #import random
    #ids = range(s.n)
    #random.shuffle(ids)
    #t0 = time.time()
    #c=0
    #for i in ids:
    #    c+=1
    #    s.get(i)
    #t1 = time.time()
    #print 'read.shp2 ',(t1-t0) * 1000, ((t1-t0) * 1000) / s.n, c

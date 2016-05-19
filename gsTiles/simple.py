from npShp.shpReader import shapeFile
import numpy

SPHEREMERC_GROUND_SIZE = (20037508.34*2)
WIDTH=256
HEIGHT=256

def simplering(ring, zoom):
    numtiles = 2**zoom
    #scale to number of pixels in the current zoom
    ring = (ring / SPHEREMERC_GROUND_SIZE) * (numtiles*256.)
    #To Round or Floor?
    ring = ring.round().astype(int)

    # Remove Duplicate Points, as they will be marked as collinear
    # even if they are needed.
    ring = ring[numpy.hstack(((ring[:-1] != ring[1:]).any(1), [True]))]
    if ring.shape[0] < 3:
        return ring

    # Find and remove Collinear Points
    a = ring[:-2]
    b = ring[1:-1]
    c = ring[2:]
    ring = ring[numpy.hstack(([True], numpy.cross(a-b,c-b) != 0, [True]))]

    # Scale back to original coodirnate system.
    ring = (ring / (numtiles*256.)) * SPHEREMERC_GROUND_SIZE
    return ring
def simple(poly, zoom):
    return [simplering(ring, zoom) for ring in poly]
    #return [r for r in poly if r.shape[0] > 2]


if __name__ == '__main__':
    #shp = '/Users/charlie/Documents/data/usa/usa.gmerc.shp'
    shp = '/Users/charlie/Documents/data/blkgrps/blkgrps.gmerc.shp'
    s = shapeFile(shp)
    #z0 = [simple(poly, 9) for poly in s.shapes()]

    import pysal
    out = pysal.open(shp[:-4]+'_z20.shp','w')
    for poly in s.shapes():
        poly = simple(poly, 20)
        ctest = map(pysal.cg.is_clockwise, poly)
        ctest[0] = True
        p = pysal.cg.Polygon([r for r,c in zip(poly,ctest) if c], [r for r,c in zip(poly,ctest) if not c])
        out.write(p)
    out.close()
        


from locator import BBoxLocator
from preRender import renderTile
from preRender import renderQuad
from optTile import optTile
import math
from tileDB import TileDB
import time
import sys

SPHEREMERC_GROUND_SIZE = (20037508.34*2)

class Tiler:
    def __init__(self,polys, db):
        self.polys = polys
        self.db = db
        
    def gTileBounds(self,zoom=0):
        """ gTileBounds returns the bounds of the map in the gTile scheme. 
            note: gtBounds[4] should contain the zoom
        """
        zoomfactor = 2**zoom
        tilesize = SPHEREMERC_GROUND_SIZE / zoomfactor
        minx, miny, maxx, maxy = self.polys.extent

        ## Left X
        leftx = math.floor((minx + (SPHEREMERC_GROUND_SIZE / 2.0)) / tilesize)
        ## Bottom Y .... Y's count up as you go south!
        boty = math.ceil(((-1 * (miny - (SPHEREMERC_GROUND_SIZE / 2.0))) / tilesize) - 1)
        ## Right X
        rightx = math.ceil(((maxx + (SPHEREMERC_GROUND_SIZE / 2.0)) / tilesize) - 1)
        ## Top Y .... Top Y is 0!
        topy = math.floor((-1 * (maxy - (SPHEREMERC_GROUND_SIZE / 2.0))) / tilesize)

        #print "\t - ",zoom,"\t#tiles: ",int((rightx+1-leftx)*(boty+1-topy))
        return map(int,[leftx,boty,rightx,topy,zoom])
    def zoomLevelDraw(self,zoom=0, minZoom = 0):
        #isLeaf = self.db.parentIsLeaf
        #exists = self.db.exists
        missing = self.db.missing
        gQuadDraw = self.gQuadDraw

        leftx,boty,rightx,topy,zoom = self.gTileBounds(zoom=zoom)
        expected = int((rightx+1-leftx)*(boty+1-topy))
        estimated = self.db.count_branch_nodes(zoom-1)*4
        actual = 0
        print "Expected:", expected
        print "Estimated:", estimated
        t0 = time.time()
        for (x,y) in self.toRender(zoom, force=zoom <= minZoom):
            if missing(x,y,zoom) or zoom <= minZoom:
                gQuadDraw(x,y,zoom)
                actual += 4
            if actual % 50 == 0 or zoom<=6:
                rate = (time.time() - t0) / (actual+1) # seconds per tile
                sys.stdout.write("Actual: %d, remaining: %0.2fs, rate:%0.5fms/t         \r"%(actual, (estimated-actual)*rate, 1000*rate))
                sys.stdout.flush()
        rate = (time.time() - t0) / (actual+1) # seconds per tile
        print "Actual: %d, took:      %0.2fs, rate:%0.5fms/t         "%(actual, time.time()-t0, 1000*rate)
    def toRender(self, zoom, force=False):
        """find the quads to render in current zoom
            parent zoom must have been fully rendered!
            only top left coordinate if returned,
            render all for tiles one shot yield 4x speedup.
        """
        if zoom == 0:
            yield (0,0)
        elif force:
            leftx,boty,rightx,topy,zoom = self.gTileBounds(zoom=zoom-1)
            for x in xrange(leftx,rightx+1):
                for y in xrange(topy,boty+1):
                    yield (x<<1, y<<1)
        else:
            for x,y in self.db.branch_nodes(zoom-1).fetchall():
                x = x<<1
                y = y<<1
                yield (x + 0, y + 0)
                # Render Quad only requires the top left tile in the quad.
                #yield (x + 1, y + 0)
                #yield (x + 0, y + 1)
                #yield (x + 1, y + 1)
    def fullRender(self, maxZoom = 21, minZoom = 5):
        start = int(self.db.get_prop('max_zoom') or -1) + 1
        for z in xrange(start, maxZoom+1):
            print "Zoom:", z
            self.zoomLevelDraw(z, minZoom)
            self.db.conn.commit()
            self.db.set_prop('max_zoom', z)
            print
        
    def gTileDraw(self,x,y,z):
        a,b = renderTile(x,y,z, self.polys)
        typ, dat = optTile(a)
        btyp, bdat = optTile(b)
        self.db.addTile(x, y, z, typ, dat, btyp+bdat)

    def gQuadDraw(self,x,y,z):
        a,b = renderQuad(x,y,z, self.polys)
        a.shape = (512,512)
        b.shape = (512,512)

        for qx,qy in [(0,0), (1,0), (0,1), (1,1)]:
            typ,  dat  = optTile(a[256 * qy: 256 + 256 * qy, 256 * qx: 256 + 256 * qx])
            btyp, bdat = optTile(b[256 * qy: 256 + 256 * qy, 256 * qx: 256 + 256 * qx])
            try:
                self.db.addTile(x+qx, y+qy, z, typ, dat, btyp+bdat)
            except:
                print "Exception: ", x+qx, y+qy, "zoom:", z

if __name__=='__main__':
    from npShp.shpReader import shapeFile
    #fname = '/Users/charlie/Documents/data/usa/usa.gmerc.shp'
    fname = '/Users/charlie/Documents/data/blkgrps/blkgrps.gmerc.shp'
    dbname = fname.split('.')[0]+'.gsTiles.sqlite'
    shp = shapeFile(fname)
    db = TileDB(dbname)
    db.setup()
    polys = BBoxLocator(shp)
    t = Tiler(polys, db)
    t.fullRender(15)
    #t.zoomLevelDraw(14)
    db.close()

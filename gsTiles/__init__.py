"""
#gsTiles

"""
from tileDB import TileDB
from tileMaker import Tiler
from npShp.shpReader import shapeFile
from locator import BBoxLocator


def create_source(fname, max_zoom = 12):
    """
    Creates a gsTiles file from the given shapefile.
    pre-rendering upto max_zoom.
    """
    shp = shapeFile(fname)
    dbname = fname.rsplit('.', 1)[0]+'.gsTiles.sqlite'
    db = TileDB(dbname)
    db.setup()
    polys = BBoxLocator(shp)
    t = Tiler(polys, db)
    t.fullRender(max_zoom)
    db.close()

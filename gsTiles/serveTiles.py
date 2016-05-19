import base64
import cherrypy
from npShp.shpReader import shapeFile
from locator import BBoxLocator
from tileDB import TileDB
from preRender import renderTile
from optTile import optTile

class TileSet(object):
    def __init__(self, gstile_path, shp_path):
        cherrypy.engine.subscribe('start_thread', self.connect)
        self.gstile_path = gstile_path
        self.shp_path = shp_path
        self._polys = BBoxLocator(shapeFile(shp_path))
        self.exposed = True
    @property
    def db(self):
        if self.gstile_path not in cherrypy.thread_data.db_connections:
            cherrypy.thread_data.db_connections[self.gstile_path] = TileDB(self.gstile_path)
        return cherrypy.thread_data.db_connections[self.gstile_path]
    @property
    def polys(self):
        # 2bit hack...
        # shape reader is not thead safe
        # rtree probably is 
        if self.shp_path not in cherrypy.thread_data.polygons:
            cherrypy.thread_data.polygons[self.shp_path] = self._polys.clone()
        return cherrypy.thread_data.polygons[self.shp_path]
    def connect(self, thread_index):
        """
        Non thread safe stuff goes here.
        This get's called for each thread.

        Ref:
            http://tools.cherrypy.org/wiki/Databases
        """
        print "Connect:", thread_index, self.gstile_path
        cherrypy.thread_data.db_connections = {}
        cherrypy.thread_data.polygons = {}
            
    @cherrypy.tools.json_out()
    def GET(self, x, y, z, b=0, **kqargs):
        b = int(b)
        db = self.db
        tile = db.getTile(x,y,z)
        if tile:
            t, dat, bdat = tile
            if b!=0:
                t = bdat[0]
                dat = bdat[1:]
            return {'typ': t, 'dat':base64.b64encode(dat), 'version': 2}
        else: #Tile not found, could be blank, or just not yet rendered...
            z = int(z)
            if z > int(db.get_prop('max_zoom')): #this level hasn't been preRendered
                x, y, b = int(x), int(y), bool(b)
                tile, btile = renderTile(x,y,z, self.polys)
                if b!=0:
                    tile = btile
                t,dat = optTile(tile)
                return {'typ': t, 'dat':base64.b64encode(dat), 'version': 2}
            return {'typ': 'A', 'dat':'AA==', 'version': 2}

class TileServer(object):
    def __init__(self):
        self.tileSets = {}
        self.exposed = True
    def addTileSet(self, path, tileset):
        if hasattr(self, path):
            raise ValueError, "%s already exisits!"%path
        setattr(self, path, tileset)
        self.tileSets[path] = tileset
    def GET(self):
        return str(self.tileSets.keys())
    


if __name__=='__main__':
    root = TileServer()
    root.maps = root

    dbname = '/Users/charlie/Documents/data/usa/usa.gsTiles.sqlite'
    shpname = '/Users/charlie/Documents/data/usa/usa.gmerc.shp'
    root.addTileSet('usa', TileSet(dbname, shpname))

    conf = { 
        'global': {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 8170
        },
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'response.headers.Access-Control-Allow-Origin':'*'
        }
    }
    #cherrypy.config.update({'server.thread_pool_max': 3, 'server.thread_pool':3})
    cherrypy.quickstart(root, '/', conf)

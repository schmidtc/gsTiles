import sqlite3
import pysal
from npShp import shpReader
import json

class TileDB:
    def __init__(self, path):
        self.path = path
        self.connect()
    @classmethod
    def create(cls, path):
        i = cls(path)
        i.setup()
    def connect(self):
        self.conn = sqlite3.connect(self.path)
        cur = self.conn.cursor()
        cur.execute("""PRAGMA synchronous=0""")
        #cur.execute("""PRAGMA locking_mode=EXCLUSIVE""")
        cur.execute("""PRAGMA journal_mode=MEMORY""")
        #cur.execute("""PRAGMA page_size=65536""")
        self.cur = cur

    def set_geom_from_shp(self, shp):
        """
        Creates data columns to store the bbox and centroid of each shape.
        """
        shp = shpReader.shapeFile(shp,'r')
        bb = shp.allboxes()
        self.set_prop('boxes', json.dumps(bb.tolist()))
        cent = shp.bbox_centroid()
        self.set_prop('centroids', json.dumps(cent.tolist()))
        
    def set_ids_from_dbf(self, dbf, name):
        """
        set_ids_from_dbf

        Copy column from dbf into metadata to return as orded json list.
        """
        db = pysal.open(dbf,'r')
        col = db.by_col[name]
        self.set_prop('id:%s'%name, json.dumps(col))
    def get_ids(self, name):
        """
        Return the ids of the given name.
        """
        return self.get_prop('id:%s'%name)
    def set_prop(self, name, value):
        q = "INSERT OR REPLACE INTO metadata (name, value) VALUES (?, ?)"
        self.cur.execute(q, (name, value))
        self.conn.commit()
    def get_prop(self, name):
        """
        mbtiles spec requires...
        name -- string
        type -- 'overlay' or 'baselayer'
        version -- int
        description -- string
        format -- 'png' or 'jpg'

        suggests...
        bounds -- left, bottom, right, top
        attribution -- str
        """
        r = self.cur.execute("SELECT value FROM metadata WHERE name=? limit 1", (name,)).fetchone()
        if r:
            return r[0]
    def close(self):
        self.conn.close()

    def setup(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS tiles( zoom integer, x integer, y integer, typ char, data blob, borders blob);")
        self.cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS tile_index on tiles (zoom, x, y);")
        self.cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS type_index on tiles (zoom, x, y, typ);")

        self.cur.execute("CREATE TABLE IF NOT EXISTS metadata (name text, value text);")
        self.cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS name ON metadata (name);");

    def addTile(self, x, y, z, typ, dat, border):
        q = "insert into tiles (zoom, x, y, typ, data, borders) values (?, ?, ?, ?, ?, ?);"
        self.cur.execute(q, (z,x,y,typ,buffer(dat),buffer(border)))
        #self.conn.commit()
    def getTile(self, x, y, z):
        q = "select typ,data,borders from tiles where zoom=? and x=? and y=? limit 1;"
        res = self.cur.execute(q, (z,x,y)).fetchone()
        if not res:
            z = int(z)
            return self.getParent(int(x),int(y),z)
        t,d,b = res
        return t,str(d),str(b)
    def count_branch_nodes(self, zoom):
        q = "select count(typ) from tiles where zoom=? and (typ = 'C' or typ = 'D');"
        return self.cur.execute(q, (zoom,)).fetchone()[0]
    def branch_nodes(self, zoom):
        q = "select x,y from tiles where zoom=? and (typ = 'C' or typ = 'D');"
        return self.cur.execute(q, (zoom,))
    def missing(self, x, y, z):
        """
        Return true if the tile does not exists and it's parent is not a leaf.
        """
        q = "select typ from tiles where zoom=? and x=? and y=? limit 1;"
        res = self.cur.execute(q, (z,x,y)).fetchone()
        if res:
            return False
        while not res and z > 0:
            x, y, z = x>>1, y>>1, z-1
            res = self.cur.execute(q, (z,x,y)).fetchone()
        if res:
            typ = res[0]
            if typ=='A' or typ=='B':
                return False
        return True
    def exists(self, x, y, z):
        q = "select count(typ) from tiles where zoom=? and x=? and y=? limit 1;"
        return bool(self.cur.execute(q, (z,x,y)).fetchone()[0])
    def getParent(self, x, y, z):
        q = "select typ,data,borders from tiles where zoom=? and x=? and y=? limit 1;"
        res = None
        while not res and z > 0:
            x, y, z = x>>1, y>>1, z-1
            res = self.cur.execute(q, (z,x,y)).fetchone()
        if res:
            typ,dat,b= res
            if typ=='A' or typ=='B':
                return (typ,dat,b)
        return False
            
    def parentIsLeaf(self, x, y, z):
        q = "select typ from tiles where zoom=? and x=? and y=? limit 1;"
        res = None
        while not res and z > 0:
            x, y, z = x>>1, y>>1, z-1
            res = self.cur.execute(q, (z,x,y)).fetchone()
        if res:
            typ = res[0]
            if typ=='A' or typ=='B':
                return True
        return False
            

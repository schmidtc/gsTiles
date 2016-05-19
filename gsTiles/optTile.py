"""
Filename: optTile.py
Use: Optimzes Tiles for gsTiles

determines the best format to store the raster.
Outputs are: singleton, plte, full raster.

Usage:
> tileType,strTile = optTile(png)
"""
import numpy
import zlib
#import lz4
from base64 import b64encode,b64decode
from sys import byteorder
if byteorder == 'little':
    SYSTEM_BYTEORDER = '\x00'
elif byteorder == 'big':
    SYSTEM_BYTEORDER = '\x01'
else:
    raise TypeError,"Unknown endian: %s"%byteorder
from array import array
UNSIGNED_ITEM_TYPES = {array('B').itemsize:'B', array('H').itemsize:'H', array('I').itemsize:'I', array('L').itemsize:'L'}
from struct import pack,unpack
from zlib import crc32

BLANKTILE = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x03\x00\x00\x00%\xdbV\xca\x00\x00\x00\x03PLTE\xff\xff\xff\xa7\xc4\x1b\xc8\x00\x00\x00\x01tRNS\x00@\xe6\xd8f\x00\x00\x00\x12IDATx^\x05\xc0\x81\x08\x00\x00\x00\x00\xa0\xfd\xa9\x8f\x00\x02\x00\x01t;RG\x00\x00\x00\x00IEND\xaeB`\x82'

BLANK_ID = 'A'
SINGLETON_ID = 'B'
INTERGER_RASTER_ID = 'C'
PLTE_ID = 'D'


class Singleton: #a sole region
    def __init__(self,regionId):
        self.regionId = regionId
    def __call__(self):
        return str(self.regionId)
class IntegerRaster:
    """ Pack an intRaster with 2 byte header into a base64 string
        byte 0: (byteOrder) \x00==little, \x01==big
        byte 1: (dtype) \x00=='?' unsigned 2byte int, \x01 == '?' unsigned 4byte int
    """
    def __init__(self,intRaster,maxID):
        self.intRaster = intRaster
        self.maxID = maxID
    def __call__(self):
        if self.maxID < 2**16:
            dtype = 'uint16' #UNSIGNED_ITEM_TYPES[2] #UNSIGNED_2_BYTE_INT
            DTYPE = '\x00'
        else:
            dtype = 'uint32' #UNSIGNED_ITEM_TYPES[4] #UNSIGNED_4_BYTE_INT
            DTYPE = '\x01'
        a = self.intRaster.astype(dtype)
        #return SYSTEM_BYTEORDER+DTYPE+zlib.compress(a.tostring())
        return SYSTEM_BYTEORDER+DTYPE+zlib.compress(numpy.getbuffer(a))
        
class PLTE: # an indexed palette
    """ Palletizes an intRaster and packs it into a base64 encoded string.
        9 byte header:
        byte0 = ByteOrder
        byte1:4 = in "!" network byte order len of IDAT
        byte4:8 = in "!" network byte order len of PLTE
        byte9:n = ready to go IDAT (in network (big) byteorder)
        byten:  = cPLTE
    
        Raises IOError is raster has too many regions (>256)
    """
    def __init__(self,intRaster,regions,n,width=None):
        #regions -- numpy.unique -- sorted array
        if n > 256:
            raise IOError, "%r Too large for PLTE coloring, try using Raster format"%(n)
        self.plte = regions
        plteMap = numpy.empty(regions.max()+1,'uint8')
        plteMap[regions] = numpy.arange(intRaster.size, dtype='uint8')
        idRaster = plteMap[intRaster]
        #rows = len(idRaster)/width
        idRaster.shape = (256,256)
        idRaster = numpy.concatenate((numpy.zeros((256,1), 'uint8'), idRaster), 1)
        #delta = width+1
        #c = 0
        #for i in xrange(rows):
        #    idRaster.insert(c,0) #add filter codes
        #    c+=delta
        #assert [PLTE[id] for id in idRaster] == intRaster
        self.idRaster = idRaster
        self.width = width
    def __call__(self):
        plte = self.plte
        a = self.idRaster
        #a = array('B') #unsigned 1byte int
        #a.fromlist(idRaster)
        ### Why is this here? byteswap has no effect on 'uint8'
        #if SYSTEM_BYTEORDER == '\x00': #little
        #    a.byteswap() #to big (network)

        # This is used directly in the final PNG, must be zlib.
        cIdRaster = zlib.compress(numpy.getbuffer(a))
        size = pack('!I',len(cIdRaster))
        crc = pack('!I',crc32('IDAT'+cIdRaster) & 0xFFFFFFFF)
        idat = size+'IDAT'+cIdRaster+crc

        #b = array(UNSIGNED_ITEM_TYPES[4]) #unsigned 4byte int
        #b.fromlist(plte)
        #cPLTE = zlib.compress(plte.tostring())
        cPLTE = zlib.compress(numpy.getbuffer(plte))

        s = SYSTEM_BYTEORDER + pack('!LL',len(idat),len(cPLTE)) # 9bytes <--- ByteOrder(1byte), len of idat(4bytes), len of cPLTE(4bytes)
        s = s+idat+cPLTE
        return s

def optTile(intRaster):
        regions = numpy.unique(intRaster)
        n = len(regions)
        if n > 256:
            return INTERGER_RASTER_ID,IntegerRaster(intRaster,intRaster.max())()
        elif n > 1:
            return PLTE_ID,PLTE(intRaster,regions,n,width=256)()
        else:
            rid = regions[0]
            if rid == 0:
                return BLANK_ID,'\x00'
            return SINGLETON_ID,Singleton(rid)()


if __name__=='__main__':
    #C = numpy.zeros(256*256,'uint32')
    #C[:2500] = numpy.arange(2500)
    #D = numpy.zeros(256*256,'uint32')
    #D[:23] = numpy.arange(50,500,20)
    C = numpy.array([10000000+x%500 for x in xrange(256*256)], 'uint32')
    D = numpy.array([10000000+x%50 for x in xrange(256*256)], 'uint32')

    for i in xrange(100):
        optTile(C)
        #optTile(D)
        #regions = numpy.unique(D) #result is sorted!
        #n = len(regions)
        #plteMap = numpy.empty(regions.max()+1,'uint8')
        #plteMap[regions] = numpy.arange(D.size, dtype='uint8')
        #idRaster = plteMap[D]
        #dPlte = dict(zip(regions,range(n)))
        #assert (idRaster == [dPlte[x] for x in D]).all()
    

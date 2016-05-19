#!/usr/bin/env python

import cairo
import numpy
from locator import BBoxLocator
from optTile import optTile
from simple import simple

WIDTH, HEIGHT = 256, 256
SPHEREMERC_GROUND_SIZE = (20037508.34*2)
ID_OFFSET = 2 # 0 = Background, 1 = Borders (unused)
MAX_OFFSET = 2**24

def getColor(offset):
    i = offset + ID_OFFSET
    if i > MAX_OFFSET:
        raise ValueError, "offset exceeds MAX_OFFSET"
    # There are 256 posible values within 1 byte,
    # dividing by 255. results scales these values from 0 to 1
    # dividing by 256. results in to many values
    r =  ((i >> 16) & 0xff) / 255.
    g =  ((i >> 8) & 0xff) / 255.
    b =  (i & 0xff) / 255.
    return r,g,b

def getContext(surface, tx, ty, zoom):
    """
    getContext -- Preps a cairo context for a tile

    """
    ctx = cairo.Context(surface)
    ctx.set_antialias(cairo.ANTIALIAS_NONE)
    ctx.set_line_join(cairo.LINE_JOIN_BEVEL)

    numtiles = 2**zoom
    meters_per_tile = SPHEREMERC_GROUND_SIZE / numtiles

    #3rd
    ctx.translate(-WIDTH*tx, -HEIGHT*ty) #shift to tile coords
    #2nd
    ctx.scale(WIDTH / meters_per_tile, -HEIGHT / meters_per_tile) #scale to pixels
    #1st
    ctx.translate(SPHEREMERC_GROUND_SIZE/2.0, -SPHEREMERC_GROUND_SIZE/2.0) #shift origin.
    return ctx

def drawPoly(ctx, ctx2, polygon, pid):
    r,g,b = getColor(pid)
    ctx.set_source_rgb(r,g,b)
    ctx2.set_source_rgb(r,g,b)
    for part in polygon:#TODO don't ignore holes
        ctx.move_to(*part[0])
        X = part[1:,0]
        Y = part[1:,1]
        map(ctx.line_to, X, Y)
    ctx2.append_path(ctx.copy_path())
    ctx.fill()
    ctx2.fill_preserve()
    ctx2.set_source_rgb(0.0,0.0,1./256.)
    ctx2.set_line_width(1./ctx2.get_matrix()[0])
    ctx2.stroke()

def renderQuad(tx, ty, zoom, polygons, borders = True):
    return renderTile(tx, ty, zoom, polygons, borders, 512, 512)
def renderTile(tx, ty, zoom, polygons, borders = True, width = 256, height = 256):
    """
    renderTile -- return a numpy array of uint32
    
    tx -- tile x coord
    ty -- tile y coord
    zoom -- tile zoom
    polygon -- a polygon locator
    """
    # FORMAT_ARGB32 is premultiplied, which results in loss of precision and thus cannot be used.
    # FORMAT_RGB30 offers up 30bits, (1 billion uniques), 
    #               but isn't available until 1.12 (we have 1.10)
    # FORMAT_RGB24 will have to be used.
    # Another option would be to render a 2nd channel with the alpha info.
    #borders = False
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
    ctx = getContext(surface, tx, ty, zoom)
    bsurface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
    ctx2 = getContext(bsurface, tx, ty, zoom)
    simple_level = zoom if zoom < 10 else -1
    extents = ctx.clip_extents()
    for pid,polygon in polygons.overlapping(extents, simple_level):
        drawPoly(ctx, ctx2, polygon, pid)
    #if borders:
    #    for width in range(10,0,-1):
    #        ctx2.set_source_rgb(0.0,0.0,width/256.)
    #        width = width/ctx2.get_matrix()[0]
    #        ctx2.set_line_width(width)
    #        ctx2.stroke_preserve()
    surface.flush() #make sure operations are finished
    #surface.write_to_png ("example.png") # Output to PNG
    a = numpy.frombuffer(surface.get_data(), 'uint32') & 0x00ffffff
    surface.finish()
    if borders:
        bsurface.flush()
        b = numpy.frombuffer(bsurface.get_data(), 'uint32') & 0x00ffffff
        #bsurface.write_to_png ("example2.png") # Output to PNG
        bsurface.finish()
        return a,b
    # get_data returns buffer
    # FORMAT_RGB24 consists of 32bit pixel in system byteorder
    # as A,R,G,B values.
    # The Alpha channel is present but unused, however
    # it still contains data and must be zeroed.
    return a,None


if __name__=='__main__':
    import pysal
    shp = pysal.open('/Users/charlie/Documents/data/usa/usa.gmerc.shp','r')
    polys = BBoxLocator(shp)
    #a,b = renderTile(127>>3,196>>3,6, polys, True)
    a,b = renderTile(8<<2,13<<2,5+2, polys, True)



from preRender import getColor, drawPoly
import cairo
#import cairocffi as cairo
import numpy
import optTile


def getContext(surface, tx=0, ty=0, zoom=0):
    ctx = cairo.Context(surface)
    ctx.set_antialias(cairo.ANTIALIAS_NONE)
    ctx.set_line_join(cairo.LINE_JOIN_BEVEL)
    return ctx


if __name__=='__main__':
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, 10, 10)
    ctx = getContext(surface)
    bsurface = cairo.ImageSurface(cairo.FORMAT_RGB24, 10, 10)
    ctx2 = getContext(bsurface)

    polygon = [numpy.array([(0,0),(0,500),(500,500),(500,0),(0,0)])]
    
    
    for i in range(50000):
        drawPoly(ctx, ctx2, polygon, i) 
        surface.flush()
        a = numpy.frombuffer(surface.get_data(), 'uint32') & 0x00ffffff
        #bsurface.flush()
        #b = numpy.frombuffer(bsurface.get_data(), 'uint32') & 0x00ffffff
        assert i+2 == a.min()
        

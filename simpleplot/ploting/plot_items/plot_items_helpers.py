from PyQt5 import QtGui, QtCore
import numpy as np

Colors = {
    'b': QtGui.QColor(0,0,255,255),
    'g': QtGui.QColor(0,255,0,255),
    'r': QtGui.QColor(255,0,0,255),
    'c': QtGui.QColor(0,255,255,255),
    'm': QtGui.QColor(255,0,255,255),
    'y': QtGui.QColor(255,255,0,255),
    'k': QtGui.QColor(0,0,0,255),
    'w': QtGui.QColor(255,255,255,255),
    'd': QtGui.QColor(150,150,150,255),
    'l': QtGui.QColor(200,200,200,255),
    's': QtGui.QColor(100,100,150,255),
}  

def mkPen(*args, **kargs):
    """
    Convenience function for constructing QPen. 
    
    Examples::
    
        mkPen(color)
        mkPen(color, width=2)
        mkPen(cosmetic=False, width=4.5, color='r')
        mkPen({'color': "FF0", width: 2})
        mkPen(None)   # (no pen)
    
    In these examples, *color* may be replaced with any arguments accepted by :func:`mkColor() <pyqtgraph.mkColor>`    """
    
    color = kargs.get('color', None)
    width = kargs.get('width', 1)
    style = kargs.get('style', None)
    dash = kargs.get('dash', None)
    cosmetic = kargs.get('cosmetic', True)
    hsv = kargs.get('hsv', None)
    
    if len(args) == 1:
        arg = args[0]
        if isinstance(arg, dict):
            return mkPen(**arg)
        if isinstance(arg, QtGui.QPen):
            return QtGui.QPen(arg)  ## return a copy of this pen
        elif arg is None:
            style = QtCore.Qt.NoPen
        else:
            color = arg
    if len(args) > 1:
        color = args
        
    if color is None:
        color = mkColor('l')
    if hsv is not None:
        color = hsvColor(*hsv)
    else:
        color = mkColor(color)
        
    pen = QtGui.QPen(QtGui.QBrush(color), width)
    pen.setCosmetic(cosmetic)
    if style is not None:
        pen.setStyle(style)
    if dash is not None:
        pen.setDashPattern(dash)
    return pen


def mkBrush(*args, **kwds):
    """
    | Convenience function for constructing Brush.
    | This function always constructs a solid brush and accepts the same arguments as :func:`mkColor() <pyqtgraph.mkColor>`
    | Calling mkBrush(None) returns an invisible brush.
    """
    if 'color' in kwds:
        color = kwds['color']
    elif len(args) == 1:
        arg = args[0]
        if arg is None:
            return QtGui.QBrush(QtCore.Qt.NoBrush)
        elif isinstance(arg, QtGui.QBrush):
            return QtGui.QBrush(arg)
        else:
            color = arg
    elif len(args) > 1:
        color = args
    return QtGui.QBrush(mkColor(color))


def mkColor(*args):
    """
    Convenience function for constructing QColor from a variety of argument types. Accepted arguments are:
    
    ================ ================================================
     'c'             one of: r, g, b, c, m, y, k, w                      
     R, G, B, [A]    integers 0-255
     (R, G, B, [A])  tuple of integers 0-255
     float           greyscale, 0.0-1.0
     int             see :func:`intColor() <pyqtgraph.intColor>`
     (int, hues)     see :func:`intColor() <pyqtgraph.intColor>`
     "RGB"           hexadecimal strings; may begin with '#'
     "RGBA"          
     "RRGGBB"       
     "RRGGBBAA"     
     QColor          QColor instance; makes a copy.
    ================ ================================================
    """
    err = 'Not sure how to make a color from "%s"' % str(args)
    if len(args) == 1:
        if isinstance(args[0], str):
            c = args[0]
            if c[0] == '#':
                c = c[1:]
            if len(c) == 1:
                try:
                    return Colors[c]
                except KeyError:
                    raise ValueError('No color named "%s"' % c)
            if len(c) == 3:
                r = int(c[0]*2, 16)
                g = int(c[1]*2, 16)
                b = int(c[2]*2, 16)
                a = 255
            elif len(c) == 4:
                r = int(c[0]*2, 16)
                g = int(c[1]*2, 16)
                b = int(c[2]*2, 16)
                a = int(c[3]*2, 16)
            elif len(c) == 6:
                r = int(c[0:2], 16)
                g = int(c[2:4], 16)
                b = int(c[4:6], 16)
                a = 255
            elif len(c) == 8:
                r = int(c[0:2], 16)
                g = int(c[2:4], 16)
                b = int(c[4:6], 16)
                a = int(c[6:8], 16)
        elif isinstance(args[0], QtGui.QColor):
            return QtGui.QColor(args[0])
        elif isinstance(args[0], float):
            r = g = b = int(args[0] * 255)
            a = 255
        elif hasattr(args[0], '__len__'):
            if len(args[0]) == 3:
                (r, g, b) = args[0]
                a = 255
            elif len(args[0]) == 4:
                (r, g, b, a) = args[0]
            elif len(args[0]) == 2:
                return intColor(*args[0])
            else:
                raise TypeError(err)
        elif type(args[0]) == int:
            return intColor(args[0])
        else:
            raise TypeError(err)
    elif len(args) == 3:
        (r, g, b) = args
        a = 255
    elif len(args) == 4:
        (r, g, b, a) = args
    else:
        raise TypeError(err)
    
    args = [r,g,b,a]
    args = [0 if np.isnan(a) or np.isinf(a) else a for a in args]
    args = list(map(int, args))
    return QtGui.QColor(*args)


def hsvColor(hue, sat=1.0, val=1.0, alpha=1.0):
    """Generate a QColor from HSVa values. (all arguments are float 0.0-1.0)"""
    c = QtGui.QColor()
    c.setHsvF(hue, sat, val, alpha)
    return c

    
def colorTuple(c):
    """Return a tuple (R,G,B,A) from a QColor"""
    return (c.red(), c.green(), c.blue(), c.alpha())


def colorStr(c):
    """Generate a hex string code from a QColor"""
    return ('%02x'*4) % colorTuple(c)


def intColor(index, hues=9, values=1, maxValue=255, minValue=150, maxHue=360, minHue=0, sat=255, alpha=255):
    """
    Creates a QColor from a single index. Useful for stepping through a predefined list of colors.
    
    The argument *index* determines which color from the set will be returned. All other arguments determine what the set of predefined colors will be
     
    Colors are chosen by cycling across hues while varying the value (brightness). 
    By default, this selects from a list of 9 hues."""
    hues = int(hues)
    values = int(values)
    ind = int(index) % (hues * values)
    indh = ind % hues
    indv = ind // hues
    if values > 1:
        v = minValue + indv * ((maxValue-minValue) / (values-1))
    else:
        v = maxValue
    h = minHue + (indh * (maxHue-minHue)) / hues
    
    c = QtGui.QColor()
    c.setHsv(h, sat, v)
    c.setAlpha(alpha)
    return c
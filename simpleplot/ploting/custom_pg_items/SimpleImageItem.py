#  -*- coding: utf-8 -*-
# *****************************************************************************
# Copyright (c) 2017 by the NSE analysis contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Alexander Schober <alex.schober@mac.com>
#
# *****************************************************************************

from PyQt5 import QtCore, QtGui

from ...pyqtgraph import pyqtgraph as pg
from ...pyqtgraph.pyqtgraph import Point
from ...pyqtgraph.pyqtgraph import debug as debug
from ...pyqtgraph.pyqtgraph import functions as fn

import numpy as np
import collections

class SimpleImageItem(pg.ImageItem):
    def __init__(self, **kargs):
        super().__init__(**kargs)
        self.x = None
        self.y = None
        self._rectangles = []

    def width(self):
        if self.image is None:
            return None
        axis = 0 if self.axisOrder == 'col-major' else 1
        return self.image.shape[axis]
        
    def height(self):
        if self.image is None:
            return None
        axis = 1 if self.axisOrder == 'col-major' else 0
        return self.image.shape[axis]

    def boundingRect(self):
        if self.image is None:
            return QtCore.QRectF(0., 0., 0., 0.)
        return QtCore.QRectF(
            np.amin(self.x),np.amin(self.y),
            np.amax(self.x) - np.amin(self.x),np.amax(self.y) - np.amin(self.y))

    def render(self):
        # Convert data to QImage for display.
        profile = debug.Profiler()
        if self.image is None or self.image.size == 0:
            return
        
        # Request a lookup table if this image has only one channel
        if self.image.ndim == 2 or self.image.shape[2] == 1:
            if isinstance(self.lut, collections.Callable):
                lut = self.lut(self.image)
            else:
                lut = self.lut
        else:
            lut = None

        if self.autoDownsample:
            # reduce dimensions of image based on screen resolution
            o = self.mapToDevice(QtCore.QPointF(0,0))
            x = self.mapToDevice(QtCore.QPointF(1,0))
            y = self.mapToDevice(QtCore.QPointF(0,1))

            # Check if graphics view is too small to render anything
            if o is None or x is None or y is None:
                return

            w = Point(x-o).length()
            h = Point(y-o).length()
            if w == 0 or h == 0:
                self.qimage = None
                return
            xds = max(1, int(1.0 / w))
            yds = max(1, int(1.0 / h))
            axes = [1, 0] if self.axisOrder == 'row-major' else [0, 1]
            image = fn.downsample(self.image, xds, axis=axes[0])
            image = fn.downsample(image, yds, axis=axes[1])
            self._lastDownsample = (xds, yds)
            
            # Check if downsampling reduced the image size to zero due to inf values.
            if image.size == 0:
                return
        else:
            image = self.image

        # if the image data is a small int, then we can combine levels + lut
        # into a single lut for better performance
        levels = self.levels
        if levels is not None and levels.ndim == 1 and image.dtype in (np.ubyte, np.uint16):
            if self._effectiveLut is None:
                eflsize = 2**(image.itemsize*8)
                ind = np.arange(eflsize)
                minlev, maxlev = levels
                levdiff = maxlev - minlev
                levdiff = 1 if levdiff == 0 else levdiff  # don't allow division by 0
                if lut is None:
                    efflut = fn.rescaleData(ind, scale=255./levdiff, 
                                            offset=minlev, dtype=np.ubyte)
                else:
                    lutdtype = np.min_scalar_type(lut.shape[0]-1)
                    efflut = fn.rescaleData(ind, scale=(lut.shape[0]-1)/levdiff,
                                            offset=minlev, dtype=lutdtype, clip=(0, lut.shape[0]-1))
                    efflut = lut[efflut]
                
                self._effectiveLut = efflut
            lut = self._effectiveLut
            levels = None
        
        # Convert single-channel image to 2D array
        if image.ndim == 3 and image.shape[-1] == 1:
            image = image[..., 0]
        
        # Assume images are in column-major order for backward compatibility
        # (most images are in row-major order)
        if self.axisOrder == 'col-major':
            image = image.transpose((1, 0, 2)[:image.ndim])
        
        argb, alpha = fn.makeARGB(image, lut=lut, levels=levels)
        self.qimage = fn.makeQImage(argb, alpha, transpose=False)
        self.bufferDraw()

        # pix_map = QtGui.QPixmap(1,1)
        # p = QtGui.QPainter(pix_map)
        # self.liveDraw(p)
        # self.qimage = pix_map

    def bufferDraw(self):
        '''
        This method is set to allow the draw of 
        the elements live if necessary
        '''
        self._rectangles = []

        for i,j in [(i,j) for i in range(self.x.shape[0]) for j in range(self.y.shape[0])]:
            if i == 0:
                w   = self.x[1] - self.x[0]
                x_0 = self.x[0] - w/2
            elif i == self.x.shape[0] - 1:
                x_0 = self.x[i]-(self.x[i]-self.x[i-1])/2
                w   = (self.x[i]-self.x[i-1])
            else:
                x_0 = self.x[i]-(self.x[i]-self.x[i-1])/2
                w   = (self.x[i]-self.x[i-1])/2 + (self.x[i+1]-self.x[i])/2

            if j == 0:
                h   = self.y[1]-self.y[0]
                y_0 = -h/2.
            elif j == self.y.shape[0] - 1:
                y_0 = self.y[j]-(self.y[j]-self.y[j-1])/2
                h   = (self.y[j]-self.y[j-1])
            else:
                y_0 = self.y[j]-(self.y[j]-self.y[j-1])/2
                h   = (self.y[j]-self.y[j-1])/2 + (self.y[j+1]-self.y[j])/2

            self._rectangles.append([
                QtCore.QRectF(x_0,y_0,w,h),
                QtCore.Qt.transparent,
                QtGui.QBrush(self.qimage.pixelColor(i,j))])

    def paint(self, p, *args):
        

        profile = debug.Profiler()
        if self.image is None:
            return
        if self.qimage is None:
            self.render()
            if self.qimage is None:
                return
            profile('render QImage')
        if self.paintMode is not None:
            p.setCompositionMode(self.paintMode)
            profile('set comp mode')

        for rectangle in self._rectangles:
            p.setPen(rectangle[1])
            p.setBrush(rectangle[2])
            p.drawRect(rectangle[0])

        # profile('p.drawImage')
        if self.border is not None:
            p.setPen(self.border)
            p.drawRect(self.boundingRect())

    def setImage(self, data=None, autoLevels=None, **kargs):
        """
        Update the image displayed by this item. For more information on how the image
        is processed before displaying, see :func:`makeARGB <pyqtgraph.makeARGB>`
        
        =================  =========================================================================
        **Arguments:**
        image              (numpy array) Specifies the image data. May be 2D (width, height) or 
                           3D (width, height, RGBa). The array dtype must be integer or floating
                           point of any bit depth. For 3D arrays, the third dimension must
                           be of length 3 (RGB) or 4 (RGBA). See *notes* below.
        autoLevels         (bool) If True, this forces the image to automatically select 
                           levels based on the maximum and minimum values in the data.
                           By default, this argument is true unless the levels argument is
                           given.
        lut                (numpy array) The color lookup table to use when displaying the image.
                           See :func:`setLookupTable <pyqtgraph.ImageItem.setLookupTable>`.
        levels             (min, max) The minimum and maximum values to use when rescaling the image
                           data. By default, this will be set to the minimum and maximum values 
                           in the image. If the image array has dtype uint8, no rescaling is necessary.
        opacity            (float 0.0-1.0)
        compositionMode    See :func:`setCompositionMode <pyqtgraph.ImageItem.setCompositionMode>`
        border             Sets the pen used when drawing the image border. Default is None.
        autoDownsample     (bool) If True, the image is automatically downsampled to match the
                           screen resolution. This improves performance for large images and 
                           reduces aliasing. If autoDownsample is not specified, then ImageItem will
                           choose whether to downsample the image based on its size.
        =================  =========================================================================
        
        
        **Notes:**        
        
        For backward compatibility, image data is assumed to be in column-major order (column, row).
        However, most image data is stored in row-major order (row, column) and will need to be
        transposed before calling setImage()::
        
            imageitem.setImage(imagedata.T)
            
        This requirement can be changed by calling ``image.setOpts(axisOrder='row-major')`` or
        by changing the ``imageAxisOrder`` :ref:`global configuration option <apiref_config>`.
        
        
        """
        profile = debug.Profiler()

        gotNewData = False
        if data is None:
            if self.image is None:
                return
        else:
            gotNewData = True
            shapeChanged = (self.image is None or data[2].shape != self.image.shape)
            image = data[2].view(np.ndarray)
            if self.image is None or data[2].dtype != self.image.dtype:
                self._effectiveLut = None

            self.image = data[2]
            self.x = data[0]
            self.y = data[1]

            if self.image.shape[0] > 2**15-1 or self.image.shape[1] > 2**15-1:
                if 'autoDownsample' not in kargs:
                    kargs['autoDownsample'] = True
            if shapeChanged:
                self.prepareGeometryChange()
                self.informViewBoundsChanged()

        profile()

        if autoLevels is None:
            if 'levels' in kargs:
                autoLevels = False
            else:
                autoLevels = True
        if autoLevels:
            img = self.image
            while img.size > 2**16:
                img = img[::2, ::2]
            mn, mx = np.nanmin(img), np.nanmax(img)
            # mn and mx can still be NaN if the data is all-NaN
            if mn == mx or np.isnan(mn) or np.isnan(mx):
                mn = 0
                mx = 255
            kargs['levels'] = [mn,mx]

        profile()

        self.setOpts(update=False, **kargs)

        profile()

        self.qimage = None
        self.update()

        profile()

        if gotNewData:
            self.sigImageChanged.emit()


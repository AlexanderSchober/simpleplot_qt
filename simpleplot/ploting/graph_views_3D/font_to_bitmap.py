import os
import sys
import time

import freetype
import numpy as np
from PIL import Image
from PyQt5.QtCore import QStandardPaths
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication


class Font(object):
    def __init__(self, filename, size):
        self.face = freetype.Face(filename)
        self.face.set_pixel_sizes(0, size)
        self.size = size
        self.glyph_buffer = {}
        self._initBuffer()

    def _initBuffer(self):
        # Do the space separately
        self.face.load_char(chr(2000))
        rows = self.face.glyph.bitmap.rows
        width = self.face.glyph.bitmap.width
        top = self.face.glyph.bitmap_top
        self.glyph_buffer[chr(32)] = {
            'bitmap': np.zeros((rows, width), dtype=np.uint8),
            'height': rows,
            'width': width,
            'top': top,
            'descent': max(0, rows - top),
            'ascent': max(0, max(top, rows) - max(0, rows - top)),
            'unicode_idx': 0
        }

        # Do all the others
        for i, uni_i in enumerate([j for j in range(33, 127)]):
            self.face.load_char(chr(uni_i))
            rows = self.face.glyph.bitmap.rows
            width = self.face.glyph.bitmap.width
            top = self.face.glyph.bitmap_top
            self.glyph_buffer[chr(uni_i)] = {
                'bitmap': np.fromiter(self.face.glyph.bitmap.buffer, dtype=np.uint8).reshape((rows, width)),
                'height': rows,
                'width': width,
                'top': top,
                'descent': max(0, rows - top),
                'ascent': max(0, max(top, rows) - max(0, rows - top)),
                'unicode_idx': i + 1
            }

        self.generateNumpyBitmap(self.glyph_buffer)

    def generateNumpyBitmap(self, glyph_buffer):
        max_width = 10 * self.size

        current_width_indent = 0
        current_row_indent = 0
        for i, key in enumerate(glyph_buffer.keys()):
            # Go back to the line if we have reached the limit
            if current_width_indent + glyph_buffer[key]['width'] > max_width:
                current_row_indent += self.size
                current_width_indent = 0

            # Set the values
            glyph_buffer[key]['width_pos'] = current_width_indent
            glyph_buffer[key]['row_pos'] = current_row_indent

            # Advance
            current_width_indent += glyph_buffer[key]['width']

        baseline = max([glyph_buffer[key]['ascent'] for key in glyph_buffer.keys()])
        self._numpy_bitmap = np.zeros((current_row_indent + self.size, max_width), dtype=np.uint8)
        for key in glyph_buffer.keys():
            x_0 = glyph_buffer[key]['row_pos'] + baseline - glyph_buffer[key]['ascent']
            x_1 = glyph_buffer[key]['row_pos'] + baseline - glyph_buffer[key]['ascent'] + glyph_buffer[key]['height']
            y_0 = glyph_buffer[key]['width_pos']
            y_1 = glyph_buffer[key]['width_pos'] + glyph_buffer[key]['width']
            self._numpy_bitmap[x_0:x_1, y_0:y_1] = glyph_buffer[key]['bitmap']

        self._positions_rows = np.zeros(len(glyph_buffer), dtype=np.uint16)
        self._positions_width = np.zeros(len(glyph_buffer), dtype=np.uint16)
        self._char_width = np.zeros(len(glyph_buffer), dtype=np.uint16)
        for key in glyph_buffer.keys():
            self._positions_rows[glyph_buffer[key]['unicode_idx']] = glyph_buffer[key]['row_pos']
            self._positions_width[glyph_buffer[key]['unicode_idx']] = glyph_buffer[key]['width_pos']
            self._char_width[glyph_buffer[key]['unicode_idx']] = glyph_buffer[key]['width']

    def render_text(self, text):
        """

        """
        output_dict = {
            'bitmap': self._numpy_bitmap,
            'positions_rows': self._positions_rows,
            'positions_width': self._positions_width,
            'char_width': self._char_width
        }

        char_index = np.zeros(len(text), dtype=np.uint16)
        for i, char in enumerate(text):
            char_index[i] = self.glyph_buffer[char]['unicode_idx']
        output_dict['char_index'] = char_index

        return output_dict


def getFontPaths():
    font_paths = QStandardPaths.standardLocations(QStandardPaths.FontsLocation)
    accounted = []
    unloadable = []
    family_to_path = {}

    db = QFontDatabase()
    for fpath in font_paths:  # go through all font paths
        for filename in os.listdir(fpath):  # go through all files at each path
            path = os.path.join(fpath, filename)
            idx = db.addApplicationFont(path)  # add font path
            if idx < 0:
                unloadable.append(path)  # font wasn't loaded if idx is -1
            else:
                names = db.applicationFontFamilies(idx)  # load back font family name
                for n in names:
                    if n in family_to_path:
                        accounted.append((n, path))
                    else:
                        family_to_path[n] = path
    return family_to_path


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Be sure to place 'helvetica.ttf' (or any other ttf / otf font file) in the working directory.
    family_to_path = getFontPaths()
    start = time.time_ns()
    fnt = Font(family_to_path['Courier New'], 100)
    end = time.time_ns()
    print(1e-9 * (end - start))

    # Choosing the baseline correctly
    start = time.time_ns()
    print(fnt.render_text('No Title'))
    end = time.time_ns()
    print(1e-9 * (end - start))

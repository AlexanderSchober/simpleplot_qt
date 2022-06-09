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

import decimal

import numpy as np

SI_PREFIXES = str('yzafpnµm kMGTPEZY')
SI_PREFIXES_ASCII = 'yzafpnum kMGTPEZY'


def tickValues(min_value, max_value, size, scale):
    """
    Return the values and spacing of ticks to draw::

        [
            (spacing, [major ticks]),
            (spacing, [minor ticks]),
            ...
        ]

    By default, this method calls tickSpacing to determine the correct tick locations.
    This is a good method to override in subclasses.
    """
    min_value, max_value = sorted((min_value, max_value))

    ticks = []
    tick_level = tickSpacing(min_value, max_value, size, scale)
    all_values = np.array([])
    for i in range(len(tick_level)):
        spacing, offset = tick_level[i]
        spacing /= scale
        start = (np.ceil((min_value - offset) / spacing) * spacing) + offset
        num = int((max_value - start) / spacing) + 1
        values = (np.arange(num) * spacing + start) / scale
        values = list(filter(lambda x: all(np.abs(all_values - x) > spacing * 0.01), values))
        all_values = np.concatenate([all_values, values])
        ticks.append((spacing / scale, values))
    return all_values, tick_level


def tickSpacing(min_value, max_value, size, scale):
    """
    Return values describing the desired spacing and offset of ticks.

    This method is called whenever the axis needs to be redrawn and is a 
    good method to override in subclasses that require control over tick locations.

    The return value must be a list of tuples, one for each set of ticks::

        [
            (major tick spacing, offset),
            (minor tick spacing, offset),
            (sub-minor tick spacing, offset),
            ...
        ]
    """
    min_value *= scale
    max_value *= scale
    size *= scale

    dif = abs(max_value - min_value)
    if dif == 0:
        return []

    # decide optimal minor tick spacing in pixels (this is just aesthetics)
    optimal_tick_count = max(6., np.log(max(size, 1e-8)))
    # optimal minor tick spacing 
    optimal_spacing = dif / optimal_tick_count
    # the largest power-of-10 spacing which is smaller than optimal
    p10unit = 10 ** np.floor(np.log10(optimal_spacing))
    # Determine major/minor tick spacings which flank the optimal spacing.
    intervals = np.array([1., 2., 5., 10., 20., 50., 100.]) * p10unit
    minor_index = 0
    while intervals[minor_index + 1] <= optimal_spacing:
        minor_index += 1

    levels = [
        (intervals[minor_index], 0)
        # (intervals[minor_index], 0)    # Pretty, but eats up CPU
    ]
    # decide whether to include the last level of ticks
    # min_spacing = min(size / 20., 30.)
    # max_tick_count = size / min_spacing
    # if dif / intervals[minor_index] <= max_tick_count:
    #     levels.append((intervals[minor_index], 0))
    return levels


def updateAutoSIPrefix(min_value, max_val):
    return siScale(max(abs(min_value), abs(max_val)))[0]


def siScale(x, min_value=1e-25, allow_unicode=True):
    """
    Return the recommended scale factor and SI prefix string for x.

    Example::

    siScale(0.0001)   # returns (1e6, 'μ')
    # This indicates that the number 0.0001 is best represented as 0.0001 * 1e6 = 100 μUnits
    """

    if isinstance(x, decimal.Decimal):
        x = float(x)

    try:
        if np.isnan(x) or np.isinf(x):
            return 1, ''
    except:
        print(x, type(x))
        raise
    if abs(x) < min_value:
        m = 0
        x = 0
    else:
        m = int(np.clip(np.floor(np.log(abs(x)) / np.log(1000)), -9.0, 9.0))

    if m == 0:
        pref = ''
    elif m < -8 or m > 8:
        pref = 'e%d' % (m * 3)
    else:
        if allow_unicode:
            pref = SI_PREFIXES[m + 8]
        else:
            pref = SI_PREFIXES_ASCII[m + 8]
    p = .001 ** m

    return p, pref

def tickStrings(values):
    """Return the strings that should be placed next to ticks. This method is called
    when redrawing the axis and is a good method to override in subclasses.
    The method is called with a list of tick values, a scaling factor (see below), and the
    spacing between ticks (this is required since, in some instances, there may be only
    one tick and thus no other way to determine the tick spacing)

    The scale argument is used when the axis label is displaying units which may have an SI scaling prefix.
    When determining the text to display, use value*scale to correctly account for this prefix.
    For example, if the axis label's units are set to 'V', then a tick value of 0.001 might
    be accompanied by a scale value of 1000. This indicates that the label is displaying 'mV', and
    thus the tick should display 0.001 * 1000 = 1.
    """
    strings = []
    for v in values:
        strings.append("%g" % v)
    return strings

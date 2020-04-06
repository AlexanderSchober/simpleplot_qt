#  -*- coding: utf-8 -*-
# *****************************************************************************
# Copyright (c) 2017 by the mieze analysis contributors (see AUTHORS)
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

from setuptools import setup, find_packages
import simpleplot
import os

def change_permissions_recursive(path, mode):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir_path in [os.path.join(root,d) for d in dirs]:
            os.chmod(dir_path, mode)
        for file_path in [os.path.join(root, f) for f in files]:
            os.chmod(file_path, mode)

installation = setup(
    name = 'SimplePlot',
    version =simpleplot.__version__,
    license = 'GPL',
    author = 'Alexander Schober',
    author_email = 'alex.schober@mac.com',
    description = 'Ploting package',
    packages = find_packages(),
    package_data = {'simpleplot': ['RELEASE-VERSION'],
                    'simpleplot.gui.ressources': ['*.jpg']},
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'License :: OSI Approved :: GPL License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces'
    ],
)

import site
import glob
site_package_path = site.getsitepackages()[0]
search = os.path.sep.join(site_package_path.split(os.path.sep)+['SimplePlot*'])
simpleplot_package_path = glob.glob(search)[0]
os.mkdir(os.path.sep.join([simpleplot_package_path] + ['simpleplot'] + ['ressources'] + ['settings']))

os.mkdir(os.path.sep.join([simpleplot_package_path] + ['simpleplot'] + ['ressources'] + ['settings'] + ['canvas']))
os.mkdir(os.path.sep.join([simpleplot_package_path] + ['simpleplot'] + ['ressources'] + ['settings'] + ['canvas'] + ['default']))
os.mkdir(os.path.sep.join([simpleplot_package_path] + ['simpleplot'] + ['ressources'] + ['settings'] + ['canvas'] + ['user_defined']))

os.mkdir(os.path.sep.join([simpleplot_package_path] + ['simpleplot'] + ['ressources'] + ['settings'] + ['plot'] ))
os.mkdir(os.path.sep.join([simpleplot_package_path] + ['simpleplot'] + ['ressources'] + ['settings'] + ['plot'] + ['default']))
os.mkdir(os.path.sep.join([simpleplot_package_path] + ['simpleplot'] + ['ressources'] + ['settings'] + ['plot'] + ['user_defined']))

change_permissions_recursive(os.path.sep.join([simpleplot_package_path] +['simpleplot']+ ['ressources'] + ['settings'] ), 0o777)

#  -*- coding: utf-8 -*-
# *****************************************************************************
# Copyright (c) 2017 by Alexander Schober 
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


from .fit_worker import FitWorker
from .function_library import FunctionLibrary

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import numpy as np

class FitHandler(QtCore.QObject, FunctionLibrary):
    '''
    This will be the main fit handler that will 
    contain all the fit properties of the current 
    environment. It is fed the environnement as a
    a data source. 

    Input is the environment containing the dataclass
    '''
    progress_int        = QtCore.pyqtSignal(int)
    progress_str        = QtCore.pyqtSignal(str)
    progress_finished   = QtCore.pyqtSignal()

    def __init__(self, data_link, gui = False):
        QtCore.QObject.__init__(self)
        FunctionLibrary.__init__(self)

        self._data_link = data_link
        self._max_rays = self._data_link.getVariableAxes()
        self.current_idx = 0

        if not gui:
            self.openDummyApp()
            self.gui = False
        else:
            self.gui = True

        self.initialize()
        self.connect()

    def openDummyApp(self):
        '''
        In the event that the app is run through the
        terminal the user still needs the QThreads
        signaling. This is why a dummy is created
        and left running until completion.        
        '''
        self.app = QtWidgets.QApplication(sys.argv)

    def initialize(self):
        '''
        Initialise the class by instating the worker 
        and setting up it's environment. 
        '''
        self.fit_thread = QtCore.QThread()
        self.fit_worker = FitWorker()
        self.fit_worker.moveToThread(self.fit_thread)
        self.fit_thread.started.connect(self.fit_worker.run)
        self.fit_worker.finished.connect(self.finishedFit)
        self.fit_worker.fitter.progress_int.connect(self.reportProgressInt)
        self.fit_worker.fitter.progress_str.connect(self.reportProgressStr)
        
        self.importFunctions()
        self.current_ray = [
            0 for e in range(len(self._data_link.getVariableAxes()))]

    def connect(self):
        '''
        Connect all relevant slots and signals to their
        method. Note that the app has to be running in
        order for this to work. 
        '''
        self.fit_worker.my_event.connect(self.finishedFit)

    def performFit(self):        
        '''
        The main fitting routine routine that is called
        as soon as all the parameters have been set.
        '''
        self.prepareFit()
        self.fit_thread.start()

    def reportProgressInt(self, percentage):
        '''
        propagate the signals for the gui
        '''
        self.progress_int.emit(percentage)
        
    def reportProgressStr(self, message):
        '''
        propagate the signals for the gui
        '''
        self.progress_str.emit(message)

    def finishedFit(self):
        '''
        The fitting function at the end. We can now retrieve
        the fit elements from the worker if necessary.
        '''
        self.cloneFromWorker()
        self.fit_thread.quit()

    def prepareFit(self):
        '''
        This function will grab all the elements from
        different subclasses and set them in the
        worker. This includes ranges properties and 
        parameters. 
        '''
        self.fit_worker.setXY(
            self._data_link.getFitAxes(),
            self._data_link.getData(self.current_ray))
        self.cloneToWorker()
        self.fit_worker.setParameters([0,1,2,3],1e10,10)

    def cloneToWorker(self):
        '''
        Clone the local content to the worker so he
        can proceed with the fit. This allows the 
        local component to clean.
        '''
        self.fit_worker.resetDictionary()

        for key in self.func_dict.keys():
            for element in self.func_dict[key][2]:
                self.fit_worker.addFunction(
                    element[self.current_idx].info.name,
                    source = element[self.current_idx])

    def cloneFromWorker(self):
        '''
        Clone back the data from the worker to the main
        thread that will then do the visual parts.
        '''
        for key in self.func_dict.keys():
            for i, element in enumerate(self.func_dict[key][2]):
                element[self.current_idx].clone(
                    self.fit_worker.func_dict[key][2][i])

        self.progress_finished.emit()
                
    def setCurrentRay(self, ray):
        '''
        Allow external interface to set the ray
        '''
        self.current_ray = list(ray)
        self.current_idx = self.getCurrentIdx()

    def getCurrentIdx(self):
        '''
        Get the current idx for the function library
        '''
        return int(np.sum(
            np.array(self.current_ray)
            *np.array([1.]+[
                np.prod(self._max_rays[0:i])
                for i in range(1, len(self.current_ray)-1)
            ])))

    def getFunctionX(self):
        '''
        Get the current idx for the function library
        '''
        return np.linspace(
            np.amin(self._data_link.getFitAxes()), 
            np.amax(self._data_link.getFitAxes()),
            10000)

    def getDataX(self):
        '''
        Get the current idx for the function library
        '''
        return np.array(self._data_link.getFitAxes()[0])

    def getDataY(self):
        '''
        Get the current idx for the function library
        '''
        return np.array(self._data_link.getData(self.current_ray))

    def getFitSumY(self):
        '''
        Get the current idx for the function library
        '''
        x = self.getDataX()
        output = x*0.
        for key in self.func_dict.keys():
            for i, element in enumerate(self.func_dict[key][2]):
                output += element[self.current_idx].returnData(x)
        return output
        
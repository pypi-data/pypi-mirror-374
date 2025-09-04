#!/usr/bin/env python3
"""Plotting package for EPICS PVs, ADO and LITE parameters.
"""
__version__ = 'v1.2.3 2024-07-29'# fix: process configuration file
#TODO: if backend times out the gui is not responsive
#TODO: move Add Dataset to Dataset options
#TODO: add dataset arithmetics

import sys, os, time, datetime
timer = time.perf_counter
import numpy as np
from qtpy import QtWidgets as QW, QtGui, QtCore
from qtpy.QtWidgets import QApplication, QMainWindow, QGridLayout
import pyqtgraph as pg
from pyqtgraph.graphicsItems.ViewBox.ViewBoxMenu import ViewBoxMenu
from pyqtgraph import dockarea
from functools import partial
from collections import deque
import traceback
from importlib import import_module

#````````````````````````````Constants````````````````````````````````````````
X,Y = 0,1
Scale,Units = 0,1
#````````````````````````````Helper methods```````````````````````````````````
def printTime(): return time.strftime("%m%d:%H%M%S")
def printi(msg): print((f'INFO_PVP@{printTime()}: '+msg))
def printw(msg): print((f'WARN_PVP@{printTime()}: '+msg))
def printe(msg): print((f'ERR_PVP@{printTime()}: '+msg))
def _printv(msg, level=0):
    if PVPlot.pargs.verbose > level:
        print((f'DBG{level}_PVP@{printTime()}: '+msg))
def printv(msg):   _printv(msg, 0)
def printvv(msg):  _printv(msg, 1)

def croppedText(txt, limit=200):
    if len(txt) > limit:
        txt = txt[:limit]+'...'
    return txt
def prettyDict(rDict, lineLimit=75):
    r=''
    for dev,devVals in rDict.items():
        r += dev+'\n'
        for par, parVals in devVals.items():
            r += '  '+par+':'
            if isinstance(parVals,dict):
                r += '\n'
                for attr, attrVal in parVals.items():
                    r += croppedText(f'    {attr}: {attrVal}',lineLimit)+'\n'
            else:
                r += croppedText(f' {parVals}',lineLimit)+'\n'
    return r

try:    from cad_epics import epics as EPICSAccess
except Exception as e:
    EPICSAccess = None 
    printw(f'EPICS devices are not supported on this host: {e}')
try:
    import liteaccess as liteAccess 
    LITEAccess = liteAccess.Access
    print(f'liteAccess {liteAccess.__version__}')
except Exception as e:
    printw(f'LITE devices are not supported on this host: {e}')
    LITEAccess = None
try:    
    from cad_io import adoaccess
    ADOAccess = adoaccess.IORequest()
except Exception as e:
    printw(f'ADO devices are not supported on this host: {e}')
    ADOAccess = None

def cprint(msg): 
    print('cprint:'+msg)

def get_pv(adopar:str, prop='value'):
    #print(f'>get_pv {adopar}')
    adopar, vslice = split_slice(adopar)
    access = PVPlot.access.get(adopar[:2], (ADOAccess,0))
    access,prefixLength = PVPlot.access.get(adopar[:2], (ADOAccess,0))
    if access is None:
        printe(f'No access method for `{adopar}`')
        sys.exit(1)

    pvTuple = tuple(adopar[prefixLength:].rsplit(':',1))
    rd = access.get(pvTuple)[pvTuple]
    val = rd['value']
    try:
        shape = val.shape
        if len(shape) > 2:
            printe(f'2+dimensional arrays not supported for {dev,par}')
            return None
    except:
        # val does not have attribute shape
        pass
    try:
        ts = rd['timestamp']# EPICS and LITE
    except: # ADO
        ts = rd['timestampSeconds'] + rd['timestampNanoSeconds']*1.e-9

    #printv(f"get_pv {adopar}: {rd['value']} {vslice}")
    if vslice is not None:
        val = val[vslice[0]:vslice[1]]
    return val, ts

def change_plotOption(curveName,color=None,width=None,symbolSize=None,scolor=None):
    dataset = MapOfDatasets.dtsDict[curveName]
    if color != None:
        prop = 'color'
        dataset.pen.setColor(color)
    if width != None:
        prop = 'width'
        dataset.width = width
        dataset.pen.setWidth(width)
    elif symbolSize!=None:
        dataset.symbolSize = symbolSize
    elif scolor!=None:
        dataset.symbolBrush = scolor
    else: return
    try:
        dataset.plotItem.setPen(
          dataset.pen)
    except: cprint('could not set '+prop+' for '+str(curveName))

def split_slice(parNameSlice):
    """Decode 'name[n1:n2]' to 'name',[n1:n2]"""
    devParSlice = parNameSlice.split('[',1)
    if len(devParSlice) < 2:
        return devParSlice[0], None
    sliceStr = devParSlice[1].replace(']','')
    vrange = sliceStr.split(':',1)
    r0 = int(vrange[0])
    if len(vrange) == 1:
        vslice = (r0, r0+1)
    else:
        vslice = (r0, int(vrange[1]))
    return devParSlice[0], vslice
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
def update_data():
    """ called on QtCore.qTimer() event to update plots."""
    tstart = timer()
    tt = round(time.time(),6)
    if tt > PVPlot.lastPlotTime + PVPlot.minPlottingPeriod:
        time2plot = True
        PVPlot.lastPlotTime = tt + PVPlot.minPlottingPeriod
    else:
        time2plot = False

    for dataset in MapOfDatasets.dtsDict.values():
        dataset.update_plot(time2plot)
        if dataset.dataChanged:
            printvv(f'updating {dataset.adoPars}')
            if PVPlot.statisticsWindow is None:
                continue

    if PVPlot.perfmon:
        v = timer()-tstart
        print('update time:'+str(timer()-tstart))

def get_statistics():
    statistics = {}
    for dataset in MapOfDatasets.dtsDict.values():
        s = dataset.get_statistics()
        if len(s) != 0:
            statistics.update(s)
    txt = 'Parm,\tRange,\tMean,\t\tSTD\n'
    for key,v in statistics.items():
        txt += f'{key},\t{v["xrange"]},\t{v["mean"]},\t{v["std"]}\n'
    return txt

def set_legend(dockNum:int, state:bool):
    if state: # legend enabled
        printv(f'add legends to dock{dockNum}')
        widget = PVPlot.mapOfPlotWidgets[dockNum]
        listOfItems = widget.getPlotItem().listDataItems()
        l = pg.LegendItem((100,60), offset=(70,30))  # args are (size, offset)
        l.setParentItem(widget.graphicsItem())
        PVPlot.legend[dockNum] = l
        for item in listOfItems:
            iname = item.name()
            printv(f'set_legend {iname} in dock{dockNum}')
            l.addItem(item, iname)
    else: # legend disabled
        printv(f'remove legend from dock{dockNum}')
        try:    
            PVPlot.legend[dockNum].scene().removeItem(PVPlot.legend[dockNum])
            del PVPlot.legend[dockNum]
        except Exception as e:
            printe('failed to remove legend '+dockNum+':'+str(e))
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
#```````````````````````````DateAxis class: time scale for bottom plot scale``
class DateAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        strns = []
        if len(values) == 0: 
            return ''
        rng = max(values)-min(values)
        #if rng < 120:
        #    return pg.AxisItem.tickStrings(self, values, scale, spacing)
        if rng < 3600*24:
            string = '%H:%M:%S'
        elif rng >= 3600*24 and rng < 3600*24*30:
            string = '%d'
        elif rng >= 3600*24*30 and rng < 3600*24*30*24:
            string = '%b'
        elif rng >=3600*24*30*24:
            string = '%Y'
        for x in values:
            try:
                strns.append(time.strftime(string, time.localtime(x)))
            except ValueError:  ## Windows can't handle dates before 1970
                strns.append('')
        return strns
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
#````````````````````````````Datasets`````````````````````````````````````````
class Dataset():
    """ dataset storage, keeps everything what is necessary to plot the curve.
    """
    def __init__(self, dockNum:int, name, paramAndCount):
        self.dockNum = dockNum
        self.name = name
        self.adoPars = paramAndCount # list of max 2 of (adoPar,count)
        self.plotItem = None # plotting object PlotDataItem
        self.pen = None # current pen
        self.width = 1 # pen width
        self.lastTimePlotted = 0.
        self.lastTimeUpdated = 0.
        self.plotWidget = None
        self.viewBox = None
        # members for stripchart plot
        self.viewXSize = 9E9# Wed Mar 14 2255 16:00:00
        self.viewXRange = [0., 9E9]
        self.scrolling = False
        
        # plotting options, described in 
        # http://www.pyqtgraph.org/documentation/graphicsItems/plotdataitem.html#pyqtgraph.PlotDataItem
        self.connect = None
        self.shadowPen = None
        self.fillLevel = None
        self.fillBrush = None
        self.stepMode = None
        self.symbol = None
        self.symbolPen = None
        self.symbolBrush = None
        self.symbolSize = None
        self.pxMode = None
        self.timeAxis = False
        self.statistics = {}
        self.enabled = True

        # ``````````````````` Add plotItem ``````````````````````````````````````
        #dockNum = name.split('.')[0]
        printv('plotItem for: '+str([s for s in self.adoPars])+', name:'+str(dockNum))
        initialWidth = 16
        self.data = [np.empty(initialWidth),np.empty(initialWidth)]# [X,U] data storage
        self.dataPtr = 0
        count = self.adoPars[0][1] #
        printv(f'adoPars,count: {self.adoPars,count}')
        isCorrelationPlot = len(self.adoPars) >= 2
        
        # assign the plotwidget
        if dockNum in PVPlot.mapOfPlotWidgets:
            # dock already exist, use the existing plotwidget
            self.plotWidget = PVPlot.mapOfPlotWidgets[dockNum]
            self.viewBox = self.plotWidget.getViewBox()
        else:
            # viewbox for new dock need to be created
            # create vewBox with plotwidget
            self.viewBox = CustomViewBox(dockNum, self)
            self.viewBox.setMouseMode(self.viewBox.RectMode)
            self.viewBox.sigRangeChangedManually.connect(self.xrangeChanged)
            printv(f'Creating new dock{dockNum}')
            title = None
            if count == 1 and not isCorrelationPlot:
                self.plotWidget = pg.PlotWidget(title=title, viewBox=self.viewBox,
                  axisItems={'bottom':DateAxis(orientation='bottom')})
                self.timeAxis = True
                if dockNum != 0:
                    self.plotWidget.setXLink(PVPlot.mapOfPlotWidgets[0])
            else: 
                self.plotWidget = pg.PlotWidget(title=title, viewBox=self.viewBox)
            #self.plotWidget.showGrid(True,True)
            PVPlot.mapOfPlotWidgets[dockNum] = self.plotWidget
            PVPlot.mapOfDocks[dockNum].addWidget(self.plotWidget)
            printv(f'docks: {PVPlot.mapOfDocks.keys()}, widgets: {PVPlot.mapOfPlotWidgets.keys()}')

            c = PVPlot.config
            if c is None:   xl,yl = 'LabelX','LabelY'
            else:           xl,yl = c.XLABEL,c.YLABEL
            #print(f'd:{self.dockNum}, X,Y: {xl,yl}')
            if self.dockNum == 0 and yl != 'LabelY':
                self.plotWidget.setLabel('left', yl)
            if self.dockNum == 0 and xl != 'LabelX':
                self.plotWidget.setLabel('bottom', xl)
            else:
                if isCorrelationPlot:
                    self.plotWidget.setLabel('bottom',self.adoPars[1][0])
                elif count == 1:
                    self.plotWidget.setLabel('bottom','time', units='date', unitPrefix='')
                else:
                    self.plotWidget.setLabel('bottom',PVPlot.scaleUnits[X][Units])

        # set X and Y ranges
        rangeMap = {X: (PVPlot.pargs.xrange, self.plotWidget.setXRange),
                    Y: (PVPlot.pargs.yrange, self.plotWidget.setYRange)}
        for axis,v in rangeMap.items():
            r,func = v
            if r is None:
                continue
            r = [float(i) for i in v[0].split(':')]
            func(*r)

        # create plotItem with proper pen
        lineNumber = len(PVPlot.mapOfPlotWidgets[self.dockNum].getPlotItem().listDataItems())
        self.pen = pg.mkPen(lineNumber)                
        if self.adoPars[0][0] == '':
            printv('no dataset - no plotItem')
        else:
            self.plotItem = pg.PlotDataItem(name=name, pen=self.pen)

        if self.plotItem:
            self.plotWidget.addItem(self.plotItem)
        self.lastTimePlotted = 0.

    def add_plot(self):
        self.plotWidget.addItem(self.plotItem)

    def remove_plot(self):
        self.plotWidget.removeItem(self.plotItem)

    def __str__(self):
        return f'Dataset {self.name}, x: {self.data[X].shape}'

    def xrangeChanged(self):
        viewRange = self.viewBox.viewRange()
        self.viewXRange = viewRange[X]
        viewlimit = self.viewXRange[1]
        self.viewXSize = viewlimit - self.viewXRange[0]
        self.viewBox.rangestack.append(viewRange)
        self.viewBox.unzooming = False
        #print(f'>rangestack {len(self.viewBox.rangestack)}')
        self.scrolling = (self.viewBox is not None)\
            and viewlimit > self.data[X][self.dataPtr-1]
        #print(f'scrolling: {self.scrolling}')

    def shift_viewXRange(self):
        if self.viewBox.state['autoRange'][X]:
                return
        dx = self.viewXSize*PVPlot.padding
        self.viewXRange[0] += dx
        self.viewXRange[1] += dx
        #print(f'>shift_viewXRange: {self.viewXRange[0], self.viewXRange[1]}')
        self.viewBox.setXRange(self.viewXRange[0], self.viewXRange[1])

    def plot(self, ts):
        # Plot the dataset. It may be several updates between these calls.
        if self.lastTimePlotted == ts:
            return
        printv(f'>plot: {self.name}')
        self.lastTimePlotted = ts
        #print(f'>plot: {self.name, {self.dataPtr}, round(ts,3)}')
        x = self.data[X][:self.dataPtr]
        y = self.data[Y][:self.dataPtr]
        pen = self.pen if self.width else None
        #printvv(f'x:{x}\ny:{y}')
        self.plotItem.setData(x=x, y=y,
            pen = pen,
            #TODO:connect = self.connect,
            #TODO:shadowPen = self.shadowPen,
            #TODO:fillLevel = self.fillLevel,
            #TODO:fillBrush = self.fillBrush,
            #TODO:stepMode = self.stepMode,
            symbol = self.symbol,
            #TODO:symbolPen = self.symbolPen,
            symbolPen = None,
            symbolBrush = self.symbolBrush,
            #TODO:symbolBrush = self.pen.color(),
            symbolSize = self.symbolSize,
            #TODO:pxMode = self.pxMode,
        )

    def update_plot(self, time2plot):
        curvePars = self.adoPars
        yd,ts = None,None
        try:
            #Limitation: only one (first) curve will be plotted 
            yd, ts = get_pv(curvePars[0][0])
        except Exception as e:
            #printv('got '+str((yd,ts))+', from:'+str(curvePars[0][0])+', except:'+str(e))
            printw(f'Exception getting {curvePars[0][0]}: {e}')
            return
        if ts:
            if ts == self.lastTimeUpdated:
                self.dataChanged = False
                printv(f'curve {self.name} did not change {round(ts,3)}')
                #if time2plot:
                #    self.plot(ts)
                return
        printv(f'update_plot: {self.name,curvePars}')
        self.dataChanged = True
        self.lastTimeUpdated = ts
        #printv(f'update_plot: {curvePars}, data:{yd}')
        #print(f'update {self.name, round(ts,3), round(self.lastTimePlotted,3)}')
        try:    
            l = len(yd)
            if l == 1: yd = yd[0]
        except: 
            l = 1

        # Evaluate X and Y arrays
        if l > 1:
            #printv('Array plot')
            self.data[Y] = np.array(yd)
            if len(curvePars) > 1:
                # use last item as horizontal axis
                self.data[X],*_ = get_pv(curvePars[-1][0])
            else:
                # scaled sample number
                self.data[X] = np.arange(len(yd))*PVPlot.scaleUnits[X][Scale]
            self.dataPtr = len(yd)
            self.plot(ts)
        else:
            # the plot is scrolling or correlation plot
            ptr = self.dataPtr
            if ptr >= PVPlot.pargs.limit:
                # do not extent the data buffer, roll it over instead
                self.data[X] = np.roll(self.data[X],-1)
                self.data[Y] = np.roll(self.data[Y],-1)
                ptr -= 1
            self.data[Y][ptr] = yd
            if len(curvePars) > 1:
                #print('Correlation Plot') 
                printv(f'correlation plot: {curvePars[1][0]}')
                try:
                    v,*_ = get_pv(curvePars[1][0])
                    try:    v = v[0]
                    except: pass 
                    self.data[X][ptr] = v
                except Exception as e:
                    printe('no data from '+str(curvePars[1][0]))
            else:
                # scrolling plot with time scale
                #print(f'ts: {round(ts,3), round(self.viewXRange[1],3)}')
                if self.scrolling and ts > self.viewXRange[1]:
                    self.shift_viewXRange()
                self.data[X][ptr] = ts
            ptr += 1
            self.dataPtr = ptr

            # re-alocate arrays,if necessary
            if (ptr >= self.data[Y].shape[0]):
                #print(f'realllocate: ptr: {ptr,self.data[Y].shape[0]}')
                tmp = self.data
                self.data = [np.empty(self.data[Y].shape[0] * 2),
                    np.empty(self.data[Y].shape[0] * 2)]
                self.data[Y][:tmp[Y].shape[0]] = tmp[Y]
                self.data[X][:tmp[X].shape[0]] = tmp[X]
                #printi(f'adjust {self.name} from {tmp[X].shape} to {self.data[X].shape}')

            if time2plot:
                self.plot(ts)

    def _visibleRange(self):
        npt = self.dataPtr
        #print(f'viewRange={self.viewBox.viewRange()}')
        xr = self.viewBox.viewRange()[X]
        for ileft in range(npt):
            if self.data[X][ileft] > xr[0]:
                break
        #print(f'last={self.data[X][npt-2], self.data[X][npt-1]}')
        for i in range(npt):
            if self.data[X][npt-i-1] < xr[1]:
                break
        iright = npt -i
        return ileft,iright

    def show_yProjection(self):
        ileft,iright = self._visibleRange()
        h = np.histogram(self.data[Y][ileft:iright],100)
        PVPlot.yProjectionPlotItem.setData(h[1],h[0],pen='b',stepMode=True)

    def get_statistics(self):
        ileft,iright = self._visibleRange()
        parname = self.adoPars[0][0].rsplit(':',1)[1]
        r = {parname:{}}
        rp = r[parname]
        rp['xrange'] = (ileft,iright)
        rp['mean'] = np.mean(self.data[Y][ileft:iright]).astype('f4')
        rp['std'] = np.std(self.data[Y][ileft:iright]).astype('f4')
        return r

    def get_visibleData(self):
        ileft,iright = self._visibleRange()
        r = (self.data[X][ileft:iright], self.data[Y][ileft:iright])
        return r
        
class MapOfDatasets():
    """Global dictionary of Datasets, provides safe methods to add and remove 
    the datasets"""
    dtsDict = {}    #{curveName:dataset,,,}
    
    def add(dockNum:int, mapOfCurves):
        """add new datasets, the adoPars is the space delimited string of 
        source ado:parameters."""
        printv(f'>MapOfDatasets.add({dockNum, mapOfCurves})')
        for i, kv in enumerate(mapOfCurves.items()):
            curveName,devList = kv
            printv(f'curveName: {curveName,devList}')
            if isinstance(devList,str):
                devList = [devList]
            else:
                devList = list(devList)
            devList.reverse()
            pnameAndCount = []
            for adoPar in devList:
                adoPar = adoPar.lstrip()#remove leading whitespaces
                printv(f'adoPar: {adoPar}')
                if adoPar.startswith('device('):
                    e = adoPar.index(')')
                    rest = adoPar[e+1:]# it could be arithmetics
                    adoPar = adoPar[7:e]
                try:
                    printv(f'check if {adoPar}, is alive')
                    valts = get_pv(adoPar) # check if parameter is alive
                    if valts is None:
                        printw('Could not add {adoPar}')
                        return 2
                except Exception as e:
                    printw(f'Exception in getting parameter {adoPar}: {e}')
                    return 1
                val,ts = valts
                try:    count = len(val)
                except: count = 1
                pnameAndCount.append((adoPar,count))
            printv('adding '+str(pnameAndCount)+' to datasets['+curveName+']')
            MapOfDatasets.dtsDict[curveName] = Dataset(dockNum, curveName, pnameAndCount)
            PVPlot.mapOfCurves[dockNum].append(curveName)
        printv(f'MapOfDatasets: {[(k,v.adoPars) for k ,v in  MapOfDatasets.dtsDict.items()]}')
        return 0
    
    def remove(name):
        printv('MapOfDatasets.remove '+name)
        dataset = MapOfDatasets.dtsDict[name]
        dataset.plotWidget.removeItem(dataset.plotItem)
        del MapOfDatasets.dtsDict[dataset.name]

class PopupWindow(QW.QWidget): 
    """ This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    Note: The created window will not be closed on app exit.
    To make it happen, the MainWindow should call close this widget in its closeEvent() 
    """
    def __init__(self):
        super().__init__()
        qr = PVPlot.qWin.geometry()
        self.setGeometry(QtCore.QRect(qr.x(), qr.y(), 0, 0))
        self.setWindowTitle('Statistics')
        layout = QW.QVBoxLayout()
        self.label = QW.QLabel()
        self.label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.label)
        self.setLayout(layout)
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
#`````````````````````````````````````````````````````````````````````````````
class CustomViewBox(pg.ViewBox):
    """ defines actions, activated on the right mouse click in the dock
    """
    def __init__(self, dockNum:int, dataset):
        #self.dockNum = kwds['name'] # cannot use name due to an issue in demo
        #del kwds['name'] # the name in ViewBox.init fails in demo
        self.dockNum = dockNum
        self.dataset = dataset# master dataset, it defines horizontal axis
        #print('CustomViewBox: '+str(self.dockNum))

        # call the init method of the parent class
        super(CustomViewBox, self).__init__()
        self.setDefaultPadding(0.)# standard is 0.02

        # IMPORTANT: menu creation is deferred because it is expensive 
        # and often the user will never see the menu anyway.
        self.menu = None
        self.cursors = set()
        self.unzooming = False
        self.rangestack = deque([],10) #stack of 10 of view ranges
           
    #v32#def mouseClickEvent(self, ev) removed, due to blank exports

    def raiseContextMenu(self, ev):
        # Let the scene add on to the end of our context menu
        menuIn = self.getContextMenus()        
        menu = self.scene().addParentContextMenus(self, menuIn, ev)
        menu.popup(ev.screenPos().toPoint())
        return True

    def getContextMenus(self, event=None):
        """ This method will be called when this item's children want to raise
        a context menu that includes their parents' menus.
        """
        if self.menu:
            printv('menu exist')
            return self.menu
        printv('getContextMenus for '+str(self.dockNum))
        self.menu = ViewBoxMenu(self)
        self.menu.setTitle(f'dock{self.dockNum} options..')

        # unzoom last
        unzoom = self.menu.addAction("&UnZoom")
        unzoom.triggered.connect(lambda: self.unzoom())

        # Datasets options dialog
        setDatasets = self.menu.addAction('Datasets &Options')
        setDatasets.triggered.connect(self.changed_datasetOptions)

        _statistics = self.menu.addAction('Show Statistics')
        _statistics.triggered.connect(self.show_statistics)

        _yProjection = self.menu.addAction('Show yProjection')
        _yProjection.triggered.connect(self.show_yProjection)

        cursorMenu = self.menu.addMenu('Add &Cursor')
        for cursor in ['Vertical','Horizontal']:
            action = cursorMenu.addAction(cursor)
            action.triggered.connect(partial(self.cursorAction,cursor))
        
        labelX = QW.QWidgetAction(self.menu)
        self.labelXGui = QW.QLineEdit('LabelX')
        self.labelXGui.returnPressed.connect(
            lambda: self.set_label('bottom',self.labelXGui))
        labelX.setDefaultWidget(self.labelXGui)
        self.menu.addAction(labelX)
        labelY = QW.QWidgetAction(self.menu)
        self.labelYGui = QW.QLineEdit('LabelY')
        self.labelYGui.returnPressed.connect(
            lambda: self.set_label('left',self.labelYGui))
        labelY.setDefaultWidget(self.labelYGui)
        self.menu.addAction(labelY)
                   
        backgroundAction = QW.QWidgetAction(self.menu)
        backgroundGui = QW.QCheckBox('&Black background')
        backgroundGui.stateChanged.connect(
          lambda x: self.setBackgroundColor(\
          'k' if x == QtCore.Qt.Checked else 'w'))
        backgroundAction.setDefaultWidget(backgroundGui)
        self.menu.addAction(backgroundAction)

        legenAction = QW.QWidgetAction(self.menu)
        legendGui = QW.QCheckBox('&Legend')
        legendGui.setChecked(True)
        legendGui.stateChanged.connect(lambda x: self.set_legend(x))
        legenAction.setDefaultWidget(legendGui)
        self.menu.addAction(legenAction)
        
        runAction = QW.QWidgetAction(self.menu)
        runWidget = QW.QCheckBox('&Stop')
        runWidget.setChecked(PVPlot.stopped)
        runWidget.stateChanged.connect(lambda x: self.set_stop(x))
        runAction.setDefaultWidget(runWidget)
        self.menu.addAction(runAction)

        sleepTimeMenu = self.menu.addMenu('Sleep&Time')
        sleepTimeAction = QW.QWidgetAction(sleepTimeMenu)
        sleepTimeWidget = QW.QDoubleSpinBox()
        sleepTimeWidget.setValue(PVPlot.pargs.sleepTime)
        sleepTimeWidget.setRange(0.001,100)
        sleepTimeWidget.setSuffix(' s')
        sleepTimeWidget.setSingleStep(.1)
        sleepTimeWidget.valueChanged.connect(lambda x: self.set_sleepTime(x))
        sleepTimeAction.setDefaultWidget(sleepTimeWidget)
        sleepTimeMenu.addAction(sleepTimeAction)
        return self.menu

    def cursor_text(self, pos, horizontal):
        #print(f'timeAxis = {self.dataset.timeAxis}')
        if (not horizontal) and self.dataset.timeAxis:
            txt = datetime.datetime.fromtimestamp(pos).strftime('%H:%M:%S')
        else:
            txt = f'{pos:.4g}'
        return txt
        
    def cursorAction(self, direction):
        angle = {'Vertical':90, 'Horizontal':0}[direction]
        pwidget = PVPlot.mapOfPlotWidgets[self.dockNum]
        vid = {'Vertical':0, 'Horizontal':1}[direction]
        vr = pwidget.getPlotItem().viewRange()
        #print(f'vid: {vid,vr[vid]}')
        pos = (vr[vid][1] + vr[vid][0])/2.
        pen = pg.mkPen(color='b', width=1, style=QtCore.Qt.DotLine)
        cursor = pg.InfiniteLine(pos=pos, pen=pen, movable=True, angle=angle
        , label=self.cursor_text(pos,vid), labelOpts={'color':(0,0,0)})#,'fill':(0,255,255)})
        cursor.sigPositionChangeFinished.connect(\
        (partial(self.cursorPositionChanged,cursor)))
        self.cursors.add(cursor)
        pwidget.addItem(cursor)
        self.cursorPositionChanged(cursor)

    def cursorPositionChanged(self, cursor):
        pos = cursor.value()
        horizontal = cursor.angle == 0.
        pwidget = PVPlot.mapOfPlotWidgets[self.dockNum]
        viewRange = pwidget.getPlotItem().viewRange()[horizontal]
        if pos > viewRange[1]:
            pwidget.removeItem(cursor)
            self.cursors.remove(cursor)
        else:
            cursor.label.setText(self.cursor_text(pos, horizontal))

    def changed_datasetOptions(self):
        """Dialog Plotting Options"""
        dlg = QW.QDialog()
        dlg.setWindowTitle(f"Dataset of dock{self.dockNum}")
        dlg.setWindowModality(QtCore.Qt.ApplicationModal)
        dlgSize = 500,200
        dlg.setMinimumSize(*dlgSize)
        rowCount,columnCount = 0,7
        tbl = QW.QTableWidget(rowCount, columnCount, dlg)
        tbl.setHorizontalHeaderLabels(
              ['Enb','Name','PV','Color','Width','Symbol','Size'])
        widths = (30,    50, 100,     30,     80,      40,    80)
        for column,width in enumerate(widths):
            tbl.setColumnWidth(column, width)
        tbl.setShowGrid(False)
        tbl.setSizeAdjustPolicy(
            QW.QAbstractScrollArea.AdjustToContents)
        #tbl.resize(*dlgSize)
        tbl.resize()

        for row,curveName in enumerate(PVPlot.mapOfCurves[self.dockNum]):
            tbl.insertRow(row)
            printv(f'curveName:{curveName}')
            dataset = MapOfDatasets.dtsDict[curveName]
            col = 0
            cbox = QW.QCheckBox()
            cbox.setChecked(dataset.enabled)
            #cbox.stateChanged.connect(lambda x: self.enable_dataset(x))
            cbox.stateChanged.connect(self.enable_dataset)
            cbox.setObjectName(curveName)
            tbl.setCellWidget(row, col, cbox)
            col+=1
            adoparName = dataset.adoPars[0][0]
            tbl.setItem(row, col, QW.QTableWidgetItem(curveName))
            col+=1
            printv(f'dataset:{adoparName}')
            tbl.setItem(row, col, QW.QTableWidgetItem(adoparName))
            col+=1
            # color button for line
            colorButton = pg.ColorButton(color=dataset.pen.color())
            colorButton.setObjectName(curveName)
            colorButton.sigColorChanging.connect(lambda x:
              change_plotOption(str(self.sender().objectName()),color=x.color()))
            tbl.setCellWidget(row, col, colorButton)
            col+=1
            # slider for changing the line width
            widthSlider = QW.QSlider()
            widthSlider.setObjectName(curveName)
            widthSlider.setOrientation(QtCore.Qt.Horizontal)
            widthSlider.setMaximum(10)
            widthSlider.setValue(1)
            widthSlider.valueChanged.connect(lambda x:
              change_plotOption(str(self.sender().objectName()),width=x))
            tbl.setCellWidget(row, col, widthSlider)
            col+=1
            # symbol, selected from a comboBox
            self.symbol = QW.QComboBox() # TODO: why self?
            for symbol in ' ostd+x': self.symbol.addItem(symbol)
            self.symbol.setObjectName(curveName)
            self.symbol.currentIndexChanged.connect(self.set_symbol)
            tbl.setCellWidget(row, col, self.symbol)
            col+=1
            # slider for changing the line width
            symbolSizeSlider = QW.QSlider()
            symbolSizeSlider.setObjectName(curveName)
            symbolSizeSlider.setOrientation(QtCore.Qt.Horizontal)
            symbolSizeSlider.setMaximum(10)
            symbolSizeSlider.setValue(1)
            symbolSizeSlider.valueChanged.connect(lambda x:
              change_plotOption(str(self.sender().objectName()),symbolSize=x))
            tbl.setCellWidget(row, col, symbolSizeSlider)
            col+=1
            # color button for symbol
            symbolColorButton = pg.ColorButton(color=dataset.pen.color())
            symbolColorButton.setObjectName(curveName)
            symbolColorButton.sigColorChanging.connect(lambda x:
              change_plotOption(str(self.sender().objectName()),scolor=x.color()))
            tbl.setCellWidget(row, col,symbolColorButton)
        dlg.exec_()

    def set_symbol(self, x):
        """ Change symbol of the scatter plot. The size and color are taken
        from the curve setting"""
        dtsetName = str(self.sender().objectName())
        symbol = str(self.sender().itemText(x))
        printv('set_symbol for '+dtsetName+' to '+symbol)
        dataset = MapOfDatasets.dtsDict[dtsetName]
        if symbol != ' ':
            dataset.symbol = symbol
            if not dataset.symbolSize:
                dataset.symbolSize = 4 # default size
            if not dataset.symbolBrush:
                dataset.symbolBrush = dataset.pen.color() # symbol color = line color
        else:
            # no symbols - remove the scatter plot
            dataset.symbol = None
            pass
            
    def set_label(self,side,labelGui):
        dock,label = self.dockNum,str(labelGui.text())
        printv('changed_label '+side+': '+str((dock,label)))
        PVPlot.mapOfPlotWidgets[dock].setLabel(side,label, units='')
        # it might be useful to return the prompt back:
        #labelGui.setText('LabelX' if side=='bottom' else 'LabelY')

    def set_legend(self, state):
        state = (state==QtCore.Qt.Checked)
        set_legend(self.dockNum, state)

    def set_stop(self, state):
        PVPlot.stop(state == QtCore.Qt.Checked)

    def set_sleepTime(self, itemData):
        #print('setting SleepTime to: '+str(itemData))
        PVPlot.pargs.sleepTime = itemData
        PVPlot.qTimer.stop()
        PVPlot.qTimer.start(int(PVPlot.pargs.sleepTime*1000))

    def unzoom(self):
        #print('>unzoom')
        try:
            if not self.unzooming:
                self.rangestack.pop()
            self.unzooming = True
            viewRange = self.rangestack.pop()
        except IndexError:
            #printw(f'nothing to unzoom')
            self.enableAutoRange()
            return
        #print(f'<rangestack {len(self.rangestack)}')
        self.setRange(xRange=viewRange[X], yRange=viewRange[Y], padding=None,
            update=True, disableAutoRange=True)

    def show_statistics(self):
        if PVPlot.statisticsWindow is None:
            PVPlot.statisticsWindow = PopupWindow()
        txt = get_statistics()
        PVPlot.statisticsWindow.label.setText(txt)
        PVPlot.statisticsWindow.show()
        PVPlot.statistics = {}

    def show_yProjection(self):
        if PVPlot.yProjectionWindow is None:
            PVPlot.yProjectionWindow = pg.PlotWidget()
            PVPlot.yProjectionPlotItem = pg.PlotDataItem()
            PVPlot.yProjectionWindow.addItem(PVPlot.yProjectionPlotItem)

        PVPlot.yProjectionWindow.show()
        PVPlot.yProjectionWindow.setWindowTitle(
            f'Vertical projection of {self.dataset.adoPars[0][0].rsplit(":",1)[1]}')
        self.dataset.show_yProjection()

    def enable_dataset(self, state):
        dtsetName = str(self.sender().objectName())
        print(f'enable_dataset {dtsetName, (state==QtCore.Qt.Checked)}')
        dataset = MapOfDatasets.dtsDict[dtsetName]
        enabled = (state==QtCore.Qt.Checked)
        dataset.enabled = enabled
        dataset.add_plot() if enabled else dataset.remove_plot()
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

def callback(args):
    #print(f'cb: {args}')
    for hostDevPar, pardict in args.items():
        try:
            axis,units = PVPlot.subscribedParMap[(hostDevPar)]
        except Exception as e:
            printw(f'callback exception for {hostDevPar}: {e}')
            #print(f'map: {PVPlot.subscribedParMap}')
            continue
        scale = pardict['value'][0]
        printv(f'axis={axis}, units={units}, scale={scale}')
        PVPlot.scaleUnits[axis][Scale] = scale

def add_curves(dockNum:int, curveMap:str):
    # if dock name is new then create new dock, otherwise extend the 
    # existing one with new curve
    
    #curves = [x for x in MapOfDatasets.dtsDict]
    #docks = [x.split('.')[0] for x in curves]
    curves = MapOfDatasets.dtsDict.keys()
    docks = PVPlot.mapOfDocks.keys()
    printv(f'>addcurves curves {curveMap} to {curves,docks}')
    if dockNum not in docks:
        printv(f'adding new dock{dockNum}')
        PVPlot.mapOfDocks[dockNum] = dockarea.Dock(str(dockNum),
          size=(500,200), hideTitle=True)
        if dockNum == 0:
            PVPlot.dockArea.addDock(PVPlot.mapOfDocks[dockNum], 'right',
            closable=True)
        else:
            PVPlot.dockArea.addDock(PVPlot.mapOfDocks[dockNum], 
              'top', PVPlot.mapOfDocks[0], closable=True) #TODO:closable does not work
        PVPlot.mapOfCurves[dockNum] = []
    if MapOfDatasets.add(dockNum, curveMap):
            printe(f'in add_curves: {dockNum, curveMap}')

def excepthook(exc_type, exc_value, exc_tb):
    """To uncover exceptions, missed in Qt"""
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error caught!:")
    print("error message:\n", tb)
    QApplication.quit()
    # or QApplication.exit(0)

class tmpClass():
    DOCKS = [{}]

def parse_input_parameters(pargs):
    fn = pargs.file
    if fn:
        sys.path.append(pargs.configDir)
        printv(f'importing {fn}')
        try:
            ConfigModule = import_module(fn)
            configFormat = ConfigModule.configFormat
        except ModuleNotFoundError as e:
            printe(f'Trying to import {pargs.configDir}/{fn}: {e}')
            sys.exit(0)
        return ConfigModule
    else:
        for parm in pargs.parms.split():
            parms = (pargs.prefix+parm).split(',')
            if len(parms) == 2:
                parms = (parms[0],pargs.prefix+parms[1])
            tmpClass.DOCKS[0][parm] =  parms
        return tmpClass

class PVPlot():
    config = None
    pargs = None
    mapOfPlotWidgets = {}# active plotItems
    mapOfDocks = {}# dockAreas
    mapOfCurves = {}
    padding = 0.1
    scaleUnits = [[1,'Sample'],[1,'Count']]
    subscribedParMap = {}
    perfmon = False # option for performance monitoring
    legend = {}# unfortunately we have to keep track of legends
    access = {'E:':(EPICSAccess,2), 'L:':(LITEAccess,2)}
    qWin = None
    qTimer = QtCore.QTimer()
    dockArea = None
    minPlottingPeriod = 1/10.# the data will not be plotted faster than that limit.
    lastPlotTime = 0.
    statisticsWindow = None
    yProjectionWindow = None
    yProjectionPlotItem = None
    stopped = False

    def start():
        pargs = PVPlot.pargs
        printv(f'pargs: {PVPlot.pargs}')

        try:    os.environ["QT_SCALE_FACTOR"] = str(pargs.zoomin)
        except: pass
        qApp = QApplication([])
        PVPlot.qWin = QMainWindow()
        PVPlot.dockArea = dockarea.DockArea()
        PVPlot.qWin.setCentralWidget(PVPlot.dockArea)
        PVPlot.qWin.resize(1000,500)
        ## Switch to using white background and black foreground
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        # Shortcuts
        shortcut = QW.QShortcut(QtGui.QKeySequence("Ctrl+H"), PVPlot.qWin)
        shortcut.activated.connect(PVPlot.actionHelp)
        shortcut = QW.QShortcut(QtGui.QKeySequence("Ctrl+S"), PVPlot.qWin)
        shortcut.activated.connect(partial(PVPlot.actionStop,True))
        shortcut = QW.QShortcut(QtGui.QKeySequence("Ctrl+Q"), PVPlot.qWin)
        shortcut.activated.connect(partial(PVPlot.actionStop,False))
        shortcut = QW.QShortcut(QtGui.QKeySequence("Ctrl+U"), PVPlot.qWin)
        shortcut.activated.connect(PVPlot.actionUnzoom)
        from . import helptxt
        PVPlot.helptxt = helptxt.txt

        #``````````process configuration file
        if pargs.file is not None:
            PVPlot.config = parse_input_parameters(pargs)

            try:    pargs.limit = PVPlot.config.POINTS
            except: pass

            try:    title = PVPlot.config.TITLE
            except: title = title = f'pvplot {pargs.parms}'
            PVPlot.qWin.setWindowTitle(title)
            dockList = PVPlot.config.DOCKS
            for dockNum,curveMap in enumerate(dockList):
                printv(f'add_curves to dock{dockNum}, {curveMap}')
                add_curves(dockNum, curveMap)
        #,,,,,,,,,,
        else:
            if pargs.dock:
                for par in pargs.dock:
                    dockNum = par[0][0]
                    adopar = par[0][1:].lstrip()
                    add_curves(dockNum, {adopar:adopar})
            else:
                # plots for the main dock
                if not ',' in pargs.parms:
                    for parName in pargs.parms.split():
                        add_curves(0, {parName:pargs.prefix+parName})
                else:
                    x,y = pargs.parms.split(',')
                    add_curves(0, {f'{y} vs {x}': (pargs.prefix+x, pargs.prefix+y)})

        if len(MapOfDatasets.dtsDict) == 0:
            printe(f'No datasets created')
            sys.exit(1)

        for dockNum in PVPlot.mapOfDocks:
            set_legend(dockNum, True)

        # Subscriptions. Only LITE system is supported.
        if pargs.xscale is not None:
            print(f'infra: {pargs.prefix}')
            infrastructure = pargs.prefix[:2]
            if infrastructure != 'L:':
                printe(f'The --xscale option is supported only for LITE infrastucture')
                sys.exit(1)
            hostDev = pargs.prefix[2:]
            if hostDev[-1] == ':':
                hostDev = hostDev[:-1]
            par = pargs.xscale
            printv(f'subscribing: {hostDev,par}')
            info = LITEAccess.info((hostDev,par))
            printv(f'info of {hostDev,par}: {info}')
            units = info[par].get('units','')
            PVPlot.scaleUnits[X][1] = units
            LITEAccess.subscribe(callback, (hostDev,par))
            PVPlot.subscribedParMap[(hostDev,par)] = [X, units]

        sys.excepthook = excepthook

        update_data()

        ## Start a timer to rapidly update the plot in pw
        PVPlot.qTimer.timeout.connect(update_data)
        PVPlot.qTimer.start(int(pargs.sleepTime*1000))

        PVPlot.qWin.show()
        PVPlot.qWin.resize(640,480)

        # start GUI
        ret = qApp.instance().exec_()
        print('Application exited')
        sys.exit(ret)

    def stop(state):
        PVPlot.stopped = state
        if state == True:
            PVPlot.qTimer.stop()
        else:
            PVPlot.qTimer.start(int(PVPlot.pargs.sleepTime*1000))

    #``````````Shorthcut handlers
    def actionHelp():
        PVPlot.helpWin = PopupWindow()
        PVPlot.helpWin.label.setText(PVPlot.helptxt)
        PVPlot.helpWin.show()

    def actionStop(state:bool):
        PVPlot.stop(state)

    def actionUnzoom():
        md = PVPlot.mapOfDocks
        docks = md.keys()
        for dockNum in docks:
            vb = PVPlot.mapOfPlotWidgets[dockNum].getPlotItem().getViewBox()
            vb.unzoom()

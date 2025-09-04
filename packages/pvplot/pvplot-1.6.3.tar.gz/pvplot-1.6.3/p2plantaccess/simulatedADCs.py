"""Example of communication with P2Plant simulatedADCs.
"""
__version__ = 'v1.0.3 2025-02-16'#input is working now, cleanup, time.sleep(.000001)#ISSUE, 
print(f'Version {__version__}')
import sys, time, os
import threading
import numpy as np
import pprint
from json import loads
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

from .p2plantaccess import Access as PA

UpArrow = b'\x1b[A' #Up arrow sequence
LastCmd = ''

def printTime(): return time.strftime("%m%d:%H%M%S")
def croppedText(txt, limit=200):
    if len(txt) > limit:
        txt = txt[:limit]+'...'
    return txt

def printi(msg, end=''): print(f'INF@{printTime()}: {msg}', end=end)

def printw(msg):
    msg = croppedText(msg)
    print(f'WRN@{printTime()}: {msg}')

def printe(msg):
    msg = croppedText(msg)
    print(f'ERR@{printTime()}: {msg}')

def _printv(msg, level=0):
    if pargs.verbose >= level: print(f'DBG{level}: {msg}')
def printv(msg):   _printv(msg, 1)
def printvv(msg):  _printv(msg, 2)

curves = []
lasttime = time.time()
fps = 0
def receive_subscription():
    global lasttime,fps
    ct = time.time()
    printInterval = 10#s
    if ct - lasttime >= printInterval:
        lasttime = ct
        txt = ''
        if pargs.keep_alive:
            # request something to inform server that I am alive
            r = PA.request('["get", ["perf"]]');
            txt += f'Perf: {str(r["perf"]["v"])}.'
        txt += f' Frame rate: {round(fps/printInterval,3)} Hz.'
        if not pargs.graph == '':
            TextItem.setText(txt)
        if not pargs.quiet: 
            printi(txt, end='\n>')
        fps = 0
    r = PA.recv('subscription','nonblocking')
    if len(r) == 0:
        #printv(f'no data, fps: {fps}')
        time.sleep(.000001)#ISSUE: if return without any system call, then the cycle rate is slow, same as with -g and CPU=100%. Is this QT issue? With this microsleep the CPU=26% and trig rate=frame. 
        return
    try:
        # data received
        fps += 1
        printv(f'data received, fps: {fps}')
        decoded = PA.decode()
        if pargs.verbose >= 2:
            printv(f'decoded: {decoded}')
        try:    data = decoded['adcs']['v']
        except KeyError:
            printe(f'PV not delivered: adcs')
            sys.exit(1)
        lx = len(data[0])
        #x = np.arange(lx)/adc_srate
        x= np.arange(lx)
        #printv(f'Data:[{len(data)}]:\n{data}')
        if pargs.graph == '':
            return
        if len(curves) == 0:
            for idx,row in enumerate(data):
                if pargs.graph is None or str(idx+1) in pargs.graph:
                    curve = pg.PlotCurveItem(pen=(idx,len(data)*1.3))
                    printv(f'adding curve ADC{idx+1}')
                    plot.addItem(curve)
                    curves.append(curve)
                    legend.addItem(curve, f'ADC{idx+1}')
            plot.resize(900,600)
        for idx,curvrow in enumerate(zip(curves,data)):
            #print(f'idx {idx} {pargs.graph is None or str(idx+1) in pargs.graph}')
            if pargs.graph is None or str(idx+1) in pargs.graph:
                curve,row = curvrow
                curve.setData(x, row*pargs.yscale)
        
    except KeyboardInterrupt:
        print(' Interrupted')
        sys.exit(1)

def input_thread():
    global LastCmd
    print(( 'Example commands:\n'
            '````````````````````````\n'
            '["info",["*"]]\n'
            '["set",[["run","stop"]]]\n'
            '["set",[["debug",2]]]\n'
            ',,,,,,,,,,,,,,,,,,,,,,,,'))
    while(1):
        msg = input()
        if msg.encode() == UpArrow:
            msg = LastCmd
        else:
            LastCmd = msg
        print(f'requested: {msg}')
        r = PA.request(msg)
        print(f'replied: {r}')
        print('>',end='')
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
#``````````````````Main function``````````````````````````````````````````````
def main():
    import argparse
    global pargs, plot, TextItem, legend
    parser = argparse.ArgumentParser(description=__doc__
    ,formatter_class=argparse.ArgumentDefaultsHelpFormatter
    ,epilog=f'{sys.argv[0]}: {__version__}')
    parser.add_argument('-b','--bitrate', type=int, default=7372800, help=
      'Optional, bitrate')
    parser.add_argument('-B','--black', action='store_true', help=
      'Black background, white foreground for all graphics')
    parser.add_argument('-g', '--graph', default='', nargs='?', help=\
      'Show waveforms on a graph, for example, -g: show all, -g123: only show waveforms 1,2 and 3')
    parser.add_argument('-k', '--keep_alive', action='store_true', help=\
      'Periodically send request to server to keep it alive')
    parser.add_argument('-q', '--quiet', action='store_true', help=\
      'Do not print frame statistics')
    parser.add_argument('-t','--transport', default='ipc', choices=['uart','ipc'], help=
      'Transport interface')
    parser.add_argument('-u', '--yunits', default='', help=\
      'Units for Y-axis')
    parser.add_argument('-v', '--verbose', action='count', default=0, help=\
      'Show more log messages (-vv: show even more)')
    parser.add_argument('-y', '--yscale', type=float, default=1., help=\
      'Y scale')
    parser.add_argument('-z', '--zoomin', help=\
      'Zoom the application window by a factor')
    pargs = parser.parse_args()
    #breakpoint()

    PA.init(pargs.transport, pargs.bitrate)
    PA.start()

    r = PA.request('["get", ["version"]]');
    print(f'P2Plant {r["version"]["v"]}')
    PA.request('["set", [["run", "start"]]]')

    #```````````````The P2Plant seems to be alive`````````````````````````````````
    threading.Thread(target=input_thread, daemon=True).start()
    if pargs.graph == '':
        # No plotting.
        while(1):
            receive_subscription()
    else:
        if not pargs.black:
            pg.setConfigOption('background', 'w')
            pg.setConfigOption('foreground', 'k')
        # the --zoom should be handled prior to QtWidgets.QApplication
        try:
            #print(f'argv: {sys.argv}')
            idx = sys.argv.index('-z')
            zoom = sys.argv[idx+1]
            print(f'Zoom is set to {zoom}')
            os.environ["QT_SCALE_FACTOR"] = zoom
        except Exception as e:
            #print(f'zoom option is not provided: {e}')
            pass
        app = pg.mkQApp()
        plot = pg.plot()
        plot.setWindowTitle('Simulated ADC')
        #print(f'ADC sampling rate: {adc_srate} Hz')
        adc_srate = 1.
        if adc_srate == .9999:
            printw(f'Fail to read ADC sampling rate. It can be recovered using `get adc_srate` command.')
            plot.setLabel('bottom', 'Sample')
        else:
            plot.setLabel('bottom', 'Time', units='S')
        plot.setLabel('left','', units=pargs.yunits)

        legend = pg.LegendItem((80,60), offset=(70,20))
        legend.setParentItem(plot.graphicsItem())

        #text = pg.TextItem(html='<div style="text-align: center"><span style="color: #FFF;">This is the</span><br><span style="color: #FF0; font-size: 16pt;">PEAK</span></div>', anchor=(-0.3,0.5), angle=45, border='w', fill=(0, 0, 255, 100))
        TextItem = pg.TextItem('Acquisition started', color='darkBlue', anchor=(0,1))#, ensureInBounds=True)
        TextItem.setParentItem(plot.graphicsItem())
        #plot.addItem(TextItem)
        #width = plot.size().width()
        #print(f'width: {width}')
        TextItem.setPos(40, 20)
        
        timer = QtCore.QTimer()
        timer.timeout.connect(receive_subscription)
        timer.start(1)
        app.exec_()

if __name__ == "__main__":
    main()


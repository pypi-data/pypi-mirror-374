""" Pvplot configuration for litePeakSimulator, serving port 9710 at localhost.
The command line to start litePeakSimulator:
   python3 -m liteserver.device.litePeakSimulator -ilo -p9710
"""
configFormat='pvplot'

TITLE="PeakSimulator"
XLABEL = "Time (us)"
YLABEL = "V"
POINTS = 1000# data arrays will be rolled over after accumulating this number of points

""" The following attributes are not handled yet:
YES = 1
POLLPERIOD = 0
MINPOLLPERIOD = 0
POLLBEFOREASYNC = 1
AVERAGETYPE = none
LOGFORMAT = logger
LOGPERIODSEC = 0
LOGMETHOD = 'continuous'
LOGDESCRIPTION = ""
LOGCORRELATION = 'NOTREQUIRED'
FILLDATA = YES
LOGTREEPATH = '/operations/app_store/RunData/currentFill/'
PREFERREDLOGDISPLAY = Snapshot
DATASTAMPTYPE = 'WCTPERIOD'
WCTCORRPERIOD_MSEC = 1000
WCTCORRWINDOW_MSEC = 1000
SYNCHRONIZED = 0
YMINAUTOSCALE = 2
YMAXAUTOSCALE = 2
YLOGAXIS = 0
Y2LABEL = ""
Y2MINAUTOSCALE = 2
Y2MAXAUTOSCALE = 2
Y2LOGAXIS = 0
ERRORBARS = 0
FONTTYPE = 'Medium'
KEEPPREVIOUS = 0
"""

dev='L:localhost;9710:dev1:'

DOCKS = [
  {'YMax':f'{dev}yMax',# without device()
   'YMin':f'device({dev}yMin)',
   'Y[10]':f'device({dev}y[500])',
  },
  {'YvsX':(f'device({dev}x)',f'device({dev}y)'),
  }
]

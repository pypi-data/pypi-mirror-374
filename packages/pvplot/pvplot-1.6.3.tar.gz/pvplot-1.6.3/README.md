# pvplot
Package for dynamic plotting of EPICS PVs (both CA and PVA) and [liteServer data objects](https://github.com/ASukhanov/liteServer).<br>
![litePeakSimulator](docs/pvplotx.jpg)

## Examples
- `python -m pvplot -cconfig -fpeakSimulator_pvp`: [Two docks](docs/peakSimulator_pvp.png) with array plot and a strip chart using native config file /operations/app_store/pvplot/peakSimulator_pvp.py. Note: The litePeakSimulator has to be running and serving localhost port 9710, it can be started like this: `python -m liteserver.device.litePeakSimulator -ilo -p9710`.
- Sliced array plot of EPICS Channel Access [testAsynPortDriverApp](https://epics.anl.gov/modules/soft/asyn/R4-38/asynDriver.html#testAsynPortDriverApp):<br>
`python -m pvplot -s0.01 -a'E:testAPD:scope1:' 'Waveform_RBV[1:500]'`
- Waveform of EPICS PVAccess [simScope](https://github.com/ASukhanov/p4pex):<br>
`python -m pvplot P:simScope1:Waveform_RBV`
- Fast correlation plot of a litePeakSimulator<br>
`python -m pvplot -s.01 -a'L:localhost;9710:dev1:' 'x,y'`
- Strip chart of analog inputs of a LabJack U3-HV instrument, served by liteLabjack:<br>
`python -m pvplot -a'L:localhost:dev1' 'tempU3 ADC_HV[0] ADC_HV[1] ADC_HV[2] ADC_HV[3] ADC_LV'`
- To change properties of curves: right click on a plot and select 'DataSets Options'

import pylab
import nest
import numpy as np

RS = nest.Create("izhikevich",15)
nest.GetStatus(RS, "I_e")
nest.SetStatus(RS, {"I_e":5.7 ,"a":0.02, "b":.2, "c":-65. , "d":8. ,"V_th":30.})

CH = nest.Create("izhikevich",15)
nest.GetStatus(CH, "I_e")
nest.SetStatus(CH, {"I_e":5.7 ,"a":0.02, "b":.2, "c":-50. , "d":2. ,"V_th":30.})

FS = nest.Create("izhikevich",15)
nest.GetStatus(FS, "I_e")
nest.SetStatus(FS, {"I_e":5.7 ,"a":0.1, "b":.2, "c":-65. , "d":2. ,"V_th":30.})

thinker = nest.Create("izhikevich",100)
nest.GetStatus(thinker, "I_e")
nest.SetStatus(thinker, {"a":0.02, "b":.2, "c":-65. , "d":8. ,"V_th":30.})


multimeter = nest.Create("multimeter")
nest.SetStatus(multimeter, {"withtime":True, "record_from":["V_m"]})

spikedetector = nest.Create("spike_detector",
                params={"withgid": True, "withtime": True})

nest.Connect(multimeter, RS)
nest.Connect(multimeter, CH)
nest.Connect(multimeter, FS)
nest.Connect(RS, thinker)
nest.Connect(CH, thinker)
nest.Connect(FS, thinker)

nest.Connect(RS, spikedetector)
nest.Connect(CH, spikedetector)
nest.Connect(FS, spikedetector)
nest.Connect(thinker, spikedetector)

nest.Simulate(1000.0)

dmm = nest.GetStatus(multimeter)[0]
Vms = dmm["events"]["V_m"]
ts = dmm["events"]["times"]
pylab.figure(1)
pylab.plot(ts, Vms)

dSD = nest.GetStatus(spikedetector,keys="events")[0]
evs = dSD["senders"]
ts = dSD["times"]
pylab.figure(2)
pylab.plot(ts, evs, ".")
pylab.show()

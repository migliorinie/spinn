import pylab
import nest
import numpy as np

RS = nest.Create("izhikevich",15)
nest.SetStatus(RS, {"I_e":5.7 ,"a":0.02, "b":.2, "c":-65. , "d":8. ,"V_th":30.})

CH = nest.Create("izhikevich",15)
nest.SetStatus(CH, {"I_e":5.7 ,"a":0.02, "b":.2, "c":-50. , "d":2. ,"V_th":30.})

FS = nest.Create("izhikevich",15)
nest.SetStatus(FS, {"I_e":5.7 ,"a":0.1, "b":.2, "c":-65. , "d":2. ,"V_th":30.})

FBex = nest.create("izhikevich",15)
nest.SetStatus(FBex, {"I_e":5.7 ,"a":0.02, "b":.2, "c":-65. , "d":8. ,"V_th":30.})

FBin = nest.create("izhikevich",15)
nest.SetStatus(FBin, {"I_e":5.7 ,"a":0.02, "b":.2, "c":-65. , "d":8. ,"V_th":30.})

multimeter = nest.Create("multimeter")
nest.SetStatus(multimeter, {"withtime":True, "record_from":["V_m"]})

spikedetector = nest.Create("spike_detector",
                params={"withgid": True, "withtime": True})

# nest.Connect(multimeter, RS)
# nest.Connect(multimeter, CH)
# nest.Connect(multimeter, FS)

#pensare se mettere gli weights uguali a una distribuzione.
nest.Connect(RS, FS, "all_to_all", {"model": "stdp_synapse", "alpha":1, "delay":1.0})
nest.Connect(CH, RS, "all_to_all", {"model": "stdp_synapse", "alpha":1, "delay":1.0})
nest.Connect(FS, CH, "all_to_all", {"model": "stdp_synapse", "alpha":1, "delay":1.0})
nest.Connect(FS, RS, "all_to_all", {"model": "stdp_synapse", "alpha":1, "delay":1.0})
nest.Connect(RS, CH, "all_to_all", {"model": "stdp_synapse", "alpha":1, "delay":1.0})
nest.Connect(CH, FS, "all_to_all", {"model": "stdp_synapse", "alpha":1, "delay":1.0})
nest.Connect(FBex, RS, {"weight":20.0})
nest.Connect(FBex, CH, {"weight":20.0})
nest.Connect(FBex, FS, {"weight":20.0})
nest.Connect(FBin, RS, {"weight":-20.0})
nest.Connect(FBin, CH, {"weight":-20.0})
nest.Connect(FBin, FS, {"weight":-20.0})
# nest.Connect(RS, spikedetector)
# nest.Connect(CH, spikedetector)
# nest.Connect(FS, spikedetector)
# nest.Connect(thinker, spikedetector)

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

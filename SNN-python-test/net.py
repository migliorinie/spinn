#!/usr/bin/env python
#coding: utf-8
from future import division
import nest
import nest.voltage_trace
import nest.raster_plot
import pylab as pl
import numpy as np
import os
from matplotlib.pylab import *
##Print the names of the models we need
for s in nest.Models():
  if( (s.find("parrot") == 0) or (s.find("izhikevich") == 0)  ):
    #print s
#print "-----------------------------------------------------------------"
#Get path of the working directory
my_path = os.getcwd()
 
g = 7.1
eta = 45.0
delay = 1.5
V_th_Granular = -41.0
V_th_Golgi = -55.0     # [mV]
N_Granular = 20000     # [Sahasranamam et al, NatSciRep, 2016]; all RS
N_Golgi = 45
N_Glomeruli= 1500
N_Mossy = 75  
N_neurons = N_Golgi+N_Granular+N_Glomeruli
#---------------rapporti di convergenza----------------
C_mossy_Glo = 20
C_Glo_Gra = 4
C_Glo_Gol = 70
C_Gol_Gol = 400
C_Gol_Gra = 4
C_Gra_Parallel = 1000
#------------------------------------------------------
#---------------conduttanze----------------------------
J_E = 0.1    # Peak of alpha function for synapses
J_I = -g*J_E
#nu_ex = eta*V_th/(J_E*C_E)
#p_rate = 1000.0*nu_ex*C_E      # From spk/ms to spk/s
# —---------------------------------- INPUT FIRING RATE —---------------------------------
p_rate = 2.0/N_Mossy #perchè la frequenza di stimolazione è 6Hz
#------------------------------------------------------------------------------------------
#--------------------------------- SIMULATION TIMING —----------------------------------
time_sim = 500.0 #ms
#------------------------------------------------------------------------------------—
regular_spiking_set_golgi = {'a':0.2,'b':0.2,'c':-65.0,'d':2.0,'V_th': V_th_Golgi, 'I_e':5.7}
fast_spiking_set_golgi = {'a':0.1,'b':0.2,'c':-65.0,'d':2.0,'V_th': V_th_Golgi, 'I_e':5.7}
burst_spiking_set_golgi = {'a':0.02,'b':0.2,'c':-50.0,'d':2.0,'V_th': V_th_Golgi, 'I_e':5.7}
regular_spiking_set_granular = {'a':0.2,'b':0.2,'c':-65.0,'d':2.0,'V_th': V_th_Granular, 'I_e':14.85}
fast_spiking_set_granular = {'a':0.1,'b':0.2,'c':-65.0,'d':2.0,'V_th': V_th_Granular, 'I_e':14.85}
burst_spiking_set_granular = {'a':0.02,'b':0.2,'c':-50.0,'d':2.0,'V_th': V_th_Granular, 'I_e':14.85}
  
nest.SetKernelStatus({'#print_time': True})
nest.SetKernelStatus({"overwrite_files": True,              # Parameters for writing on files
                      "data_path": my_path,
                      "data_prefix": "reteGranular_prova_"})
 
# Neuroni rete
neu = nest.Create('izhikevich', (N_neurons-N_Glomeruli))
neu_Granular = neu[:N_Granular]
neu_Golgi = neu[N_Granular😏
# Random
#nest.SetStatus(neu_Granular, {'a': 0.1,'b': 0.2,'c': -65.0, 'd': 2.0,'V_th': V_th_Granular})
#nest.SetStatus(neu_Golgi, {'a': 0.1,'b': 0.2,'c': -65.0, 'd': 2.0,'V_th': V_th_Golgi})
# Values from paper
nest.SetStatus(neu_Golgi, regular_spiking_set_golgi)
nest.SetStatus(neu_Granular, regular_spiking_set_granular)
# La b è il reciproco della tau di membrana, 0.17 Granular, 0.023 Golgi per similarità con LEAK INTEGRATE AND FIRE
#nest.SetStatus(neu_Golgi, {'a': 0.02,'b': 0.17,'c': -75.0, 'd': 2.0,'V_th': V_th_Golgi,'I_e':5.7})
#nest.SetStatus(neu_Granular, {'a': 0.2,'b': 0.023,'c': -70.0, 'd': 2.0,'V_th': V_th_Granular,'I_e':14.85})
#da mettere a variare i diversi input, mentre rimane invariato il fatto di avere bursting o spike o altro.
#per i valori che possiamo recuperare da fisiologia li mettiamo fissi (con il valore pari al valore della grandezza con le stess eunità di misura)
 
 
neu_Glomeruli=nest.Create('parrot_neuron',N_Glomeruli)
neu_TOT = neu_Glomeruli+neu
 
# Neuroni esterni
mossy = nest.Create('poisson_generator',N_Mossy,{'rate': p_rate}) #il p-rate va bene che sia 6, da controllare (da variare nel range)
#le mossy fibers le modellizziamo come un generatore di poisson (quindi le mossy sono poisson)
 
#Spike detector
spk_Granular = nest.Create('spike_detector', 1, params = {"to_file": True,
  "withgid": True,
            "label": "Spikes_Granular"})
spk_Golgi = nest.Create('spike_detector', 1, params = {"to_file": True,
            "withgid": True,
            "label": "Spikes_Golgi"})
spk_Glomeruli = nest.Create('spike_detector', 1, params = {"to_file": True,
            "withgid": True,
            "label": "Spikes_Glomeruli"})
#Multimeters
m_Golgi = nest.Create("multimeter",
                params = {"interval": 1.0,
                         "record_from": ['V_m'],
                          "withgid": True,
                          "to_file": True,
                          "label": "multimeter_Golgi"})
m_Granular = nest.Create("multimeter",
                params = {"interval": 1.0,
                         "record_from": ['V_m'],
                          "withgid": True,
                          "to_file": True,
                          "label": "multimeter_Granular"})
# Connections
nest.CopyModel('static_synapse_hom_w',
        'excitatory', {'weight': J_E, 'delay': delay})
nest.CopyModel('static_synapse_hom_w',
        'inhibitory', {'weight': J_I*3, 'delay': delay})
nest.Connect(mossy,neu_Glomeruli)
nest.Connect(neu_Glomeruli,neu_Granular,{'rule':'fixed_indegree','indegree': C_Glo_Gra},'excitatory')
nest.Connect(neu_Golgi,neu_Granular,{'rule':'fixed_indegree','indegree': C_Gol_Gra},'inhibitory')
nest.Connect(neu_Golgi,neu_Golgi,{'rule':'fixed_indegree','indegree': C_Gol_Gol},'inhibitory')
nest.Connect(neu_Glomeruli,neu_Golgi,{'rule':'fixed_indegree','indegree': C_Glo_Gol},'excitatory')
nest.Connect(neu_Glomeruli,spk_Glomeruli)
nest.Connect(neu_Golgi,spk_Golgi)
nest.Connect(neu_Granular,spk_Granular)
nest.Connect(m_Golgi,neu_Golgi)
nest.Connect(m_Granular,neu_Granular)
nest.Simulate(time_sim)
try: nest.raster_plot.from_device(spk_Glomeruli, hist=True)
except nest.NESTError as err:
  #print err
  try: nest.raster_plot.from_device(spk_Golgi, hist=True)
except nest.NESTError as err:
  #print err
  try: nest.raster_plot.from_device(spk_Granular, hist=True)
except nest.NESTError as err:
  #print err
  pl.figure()
events = nest.GetStatus(m_Granular)[0]['events']
t = events['times'];
pl.plot(t, events['V_m'])
pl.axis([0, 100, -80, -30])
pl.ylabel('Membrane potential [mV]')
pl.show()
#rasterplot alla fine di ogni simulazione, come input poisson sia segnale che rumore. usiamo un poisson per tutti i neuroni a diverse frequenze.
#siamo felici quando dando un input a una frequenza tra 8-10 Hz le granular hanno andamento oscialltorio a 6 Hz di risonanza.
"""
- Fissare parametro corrente in modo tale che le granular con input minimo producano degli spike (2Hz di popolazione).
- Dare diversi valori agli altri parametri in modo da differenziare in bursting/fast spiking oppure regular/bursting golgi e granular
    - Prima mettere il bursting solo alle golgi, poi le altri fast o regular. 
- Fare simulazione con le tre frequenze, magari cambiare anche i pesi. 
"""
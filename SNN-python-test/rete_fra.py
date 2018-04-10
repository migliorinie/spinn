#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import nest
import nest.voltage_trace
import nest.raster_plot
import pylab as pl
import numpy as np
import os
import sys
from scipy.interpolate import interp1d
from scipy import signal
# import peakf
from matplotlib.pylab import *


p_rate = 6.00
print "------------------------------------------"
if (len(sys.argv) > 1):
	p_rate = float(sys.argv[1])
	print "Stimulous frequency is %f"%(p_rate) 
else:
	print "Default is %f"%p_rate
print "------------------------------------------"

#Print the names of the models we need
print " ---------------- Models' names----------------------------------"
for s in nest.Models():
	if( (s.find("parrot") == 0) or (s.find("izhikevich") == 0)  ):
		print s
print "-----------------------------------------------------------------"

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
C_mossy_Glo = 1
C_Glo_Gra = 4
C_Glo_Gol = 70
C_Gol_Gol = 400
C_Gol_Gra = 4
C_Gra_Parallel = 1000
C_Gra_Gol = 1400
#------------------------------------------------------

#---------------conduttanze----------------------------
J_E = 0.1       # Peak of alpha function for synapses
J_I = -g*J_E*0.2
#nu_ex = eta*V_th/(J_E*C_E)
#p_rate = 1000.0*nu_ex*C_E      # From spk/ms to spk/s
#p_rate = 6.0 #perchè la frequenza di stimolazione è 6Hz
#------------------------------------------------------
 
 
nest.SetKernelStatus({'print_time': True})
nest.SetKernelStatus({"overwrite_files": True,              # Parameters for writing on files
                      "data_path": my_path,
                      "data_prefix": "reteGranular_prova_"+str(p_rate)+"_Hz"})
 
# Neuroni rete
neu = nest.Create('izhikevich', (N_neurons-N_Glomeruli))
neu_Granular = neu[:N_Granular]
neu_Golgi = neu[N_Granular:]


# Random
#nest.SetStatus(neu_Granular, {'a': 0.1,'b': 0.2,'c': -65.0, 'd': 2.0,'V_th': V_th_Granular})
#nest.SetStatus(neu_Golgi, {'a': 0.1,'b': 0.2,'c': -65.0, 'd': 2.0,'V_th': V_th_Golgi})

# Bursting
#nest.SetStatus(neu_Golgi, {'a': 0.02,'b': 0.2,'c': -75.0, 'd': 2.0,'V_th': V_th_Golgi})
#nest.SetStatus(neu_Granular, {'a': 0.02,'b': 0.2,'c': -70.0, 'd': 2.0,'V_th': V_th_Granular,})

# La b è il reciproco della tau di membrana, 0.17 Granular, 0.023 Golgi per similarità con LEAK INTEGRATE AND FIRE


if ( p_rate < 7.0 and p_rate > 5 ): 
	#bursting
	print " Golgi bursting "
	nest.SetStatus(neu_Golgi, {'a': 0.02,'b': 0.17,'c': -52.5, 'd': 3.0,'V_th': V_th_Golgi,'I_e':5.7})
else:
	#regular spiking
	print " Golgi regular " 
	nest.SetStatus(neu_Golgi, {'a': 0.02,'b': 0.20,'c': -65.0, 'd': 8.0,'V_th': V_th_Golgi,'I_e':5.7})

#nest.SetStatus(neu_Golgi, {'a': 0.02,'b': 0.20,'c': -65.0, 'd': 8.0,'V_th': V_th_Golgi,'I_e':5.7})





nest.SetStatus(neu_Granular, {'a': 0.2,'b': 0.03,'c': -70.0, 'd': 2.0,'V_th': V_th_Granular,'I_e':14.85})


#da mettere a variare i diversi input, mentre rimane invariato il fatto di avere bursting o spike o altro.
#per i valori che possiamo recuperare da fisiologia li mettiamo fissi (con il valore pari al valore della grandezza con le stess eunità di misura)
 
 
neu_Glomeruli=nest.Create('parrot_neuron',N_Glomeruli)

neu_TOT = neu_Glomeruli+neu
 
# Neuroni esterni
mossy = nest.Create('poisson_generator',1,{'rate': p_rate}) #il p-rate va bene che sia 6, da controllare (da variare nel range)
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
        'excitatory_Glo_Gra', {'weight': 0.65, 'delay': delay})
nest.CopyModel('static_synapse_hom_w',
        'inhibitory_Gol_Gra', {'weight': -1.0, 'delay': delay})
nest.CopyModel('static_synapse_hom_w',
        'excitatory_Gra_Gol', {'weight': 0.01, 'delay': delay})
nest.CopyModel('static_synapse_hom_w',
        'inhibitory_Gol_Gol', {'weight': -0.01, 'delay': delay})
nest.CopyModel('static_synapse_hom_w',
        'excitatory_Glo_Gol', {'weight': 0.07, 'delay': delay})

nest.Connect(mossy,neu_Glomeruli)
nest.Connect(neu_Glomeruli,neu_Granular,{'rule':'fixed_indegree','indegree': C_Glo_Gra},'excitatory_Glo_Gra')
nest.Connect(neu_Golgi,neu_Granular,{'rule':'fixed_indegree','indegree': C_Gol_Gra},'inhibitory_Gol_Gra')
nest.Connect(neu_Golgi,neu_Golgi,{'rule':'fixed_indegree','indegree': C_Gol_Gol},'inhibitory_Gol_Gol')
nest.Connect(neu_Glomeruli,neu_Golgi,{'rule':'fixed_indegree','indegree': C_Glo_Gol},'excitatory_Glo_Gol')
nest.Connect(neu_Granular,neu_Golgi,{'rule':'fixed_indegree','indegree': C_Gra_Gol},'excitatory_Gra_Gol')
nest.Connect(neu_Glomeruli,spk_Glomeruli)
nest.Connect(neu_Golgi,spk_Golgi)
nest.Connect(neu_Granular,spk_Granular)
nest.Connect(m_Golgi,neu_Golgi)
nest.Connect(m_Granular,neu_Granular)


nest.Simulate(float(sys.argv[2]))

"""
try: nest.raster_plot.from_device(spk_Glomeruli, hist=True)
except nest.NESTError as err:
	print err

try: nest.raster_plot.from_device(spk_Golgi, hist=True)
except nest.NESTError as err:
	print err

try: nest.raster_plot.from_device(spk_Granular, hist=True)
except nest.NESTError as err:
	print err


pl.figure()
"""

events = nest.GetStatus(m_Granular)[0]['events']
t = events['times'];
pl.plot(t, events['V_m'])
pl.axis([0, 100, -80, -30])
pl.ylabel('Membrane potential [mV]')


#rasterplot alla fine di ogni simulazione, come input poisson sia segnale che rumore. usiamo un poisson per tutti i neuroni a diverse frequenze.
#siamo felici quando dando un input a una frequenza tra 8-10 Hz le granular hanno andamento oscialltorio a 6 Hz di risonanza.

events_spk = nest.GetStatus(spk_Granular)[0]['events']
t_spk = events_spk['times']


#population_activity è un array con il tempo di spiking di ogni neurone

window = 5 #ms
N_pop = t_spk.size  #first dimension is the number
Max_time = t_spk[-1] #ms, last is the last spike

t_start = 0; 
t_end = t_start + window

size_pop = int(Max_time/window)+1
pop = np.zeros(size_pop)


i = 0
w = 0
while( i < N_pop ): 
	if(t_spk[i] <= t_end and t_spk[i] >= t_start):
		#print t_spk[i]
		#current time falls within the window
		i = i+1
		pop[w] = pop[w]+1
	else:
		#print " -------------- "
		w = w+1;
		t_start = t_end;
		t_end = t_start + window

#pop = pop - np.mean(pop)

x = np.arange(size_pop)

#print x
#print pop

pl.figure()

"""
pl.plot(x, pop)
pl.axis([0, np.max(x), 0, np.max(pop)])
pl.ylabel('Population Spiking')
"""


#calculate envelop 

#q_u = zeros(pop.shape)

u_x = [ ]
u_y = [ ]

#peakfind method 1
"""
peakind = signal.find_peaks_cwt(pop, np.arange(1,6))

for index in peakind:
	u_x.append(index)
	u_y.append(pop[index])
"""

	# #peakfind method 2
	# maxtab, mintab = peakf.peakdet(pop,.3)
	# print maxtab[:,0]
		
	# peakind = np.array(maxtab[:,0],dtype='int')

	# for index in peakind:
	# 	u_x.append(index)
	# 	u_y.append(pop[index])

	# #u_x.append(len(pop)-1)
	# #u_y.append(pop[-1])

	# #l_x.append(len(pop)-1)
	# #l_y.append(pop[-1])

	# #Fit suitable models to the data. Here I am using cubic splines, similarly to the MATLAB example given in the question.

	# u_p = interp1d(u_x,u_y, kind = 'cubic',bounds_error = False, fill_value=0.0)

	# q_u = np.zeros(peakind[-1]-peakind[0])

	# q_u_for_plot = np.zeros(pop.shape[-1])

	# #Evaluate each model over the domain of (s)
	# for k in xrange(peakind[0],peakind[-1]):
	#     q_u[k-peakind[0]] = u_p(k)
	#     #q_l[k] = l_p(k)

	# for kp in xrange(0,len(pop)):
	#     q_u_for_plot[kp] = u_p(kp)


	# plot(pop)
	# pl.hold(True)
	# plot(x[peakind],pop[peakind],'ro')
	# pl.hold(True)
	# plot(q_u_for_plot)

	# pl.figure()
	# q_u = q_u - np.mean(q_u)
	# plot(q_u)


	# #sampling freq
	# sp = np.fft.fft(q_u)
	# #freq = np.fft.fftfreq(len(sp))
	# N = len(q_u)
	# dt = 1/size_pop
	# T = dt*N #seconds
	# df = 1/T #fundamental frequency
	# sw = 2*np.pi*df #fundamental freq in radiants

	# xf = np.fft.fftfreq(N)*N*df

	# xf_trunc = xf[:N//2]
	# sp_trunc = 2.0/N * np.abs(sp[:N//2])


	# np.save("xf"+str(p_rate),xf_trunc)
	# np.save("sp"+str(p_rate),sp_trunc)

	# pl.figure()
	# plot(xf_trunc,sp_trunc)


	# pl.show()




"""
- Fissare parametro corrente in modo tale che le granular con input minimo producano degli spike (2Hz di popolazione).
- Dare diversi valori agli altri parametri in modo da differenziare in bursting/fast spiking oppure regular/bursting golgi e granular
    - Prima mettere il bursting solo alle golgi, poi le altri fast o regular. 
- Fare simulazione con le tre frequenze, magari cambiare anche i pesi. 
"""

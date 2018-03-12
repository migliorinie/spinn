# Created by Eugene M. Izhikevich, February 25, 2003
# Translated to Python by Enrico Migliorini

import numpy as np
import matplotlib.pyplot as plt
import progressbar
from scipy.misc import imsave

Ne = 800
Ni = 200
sampleNeuron = 76
re = np.random.rand(Ne)
ri = np.random.rand(Ni)

a = np.append(np.ones((Ne))*0.02, 0.02+0.08*ri)
b = np.append(np.ones((Ne))*0.2, 0.25-0.05*ri)
c = np.append(-65+15*np.power(re, 2), -65*np.ones(Ni)) #-65mV for RS neurons
d = np.append(8-6*np.power(re, 2), 2*np.ones(Ni)) #As above
S = np.hstack((0.5*np.random.rand(Ne+Ni, Ne), -1*np.random.rand(Ne+Ni, Ni)))

#np.set_printoptions(threshold=np.nan)
#print(S)

v = -65*np.ones(Ne+Ni)
u = np.multiply(b, v)
firings = []
sampleVTracer = []
sampleUTracer = []

#print("Stats[996]: ", a[996], b[996], c[996], d[996], v[996], u[996])
#print("Stats[16]: ", a[16], b[16], c[16], d[16], v[16], u[16])

timelimit = 1000
with progressbar.ProgressBar(max_value=timelimit) as progress:
  for t in range(timelimit):
    I = np.append(5*np.random.normal(size=Ne), 2*np.random.normal(size=Ni))
    #I = np.append(re*5, ri*2)
    fired = np.asarray([n>=30 for n in v])
    sampleVTracer.append(v[sampleNeuron])
    sampleUTracer.append(u[sampleNeuron])
    firings.append([1 if n else 0 for n in fired])
    v[fired] = c[fired]
    u[fired] = u[fired]+d[fired]
    I = I+np.sum(S[:,fired], axis=1)
    v=v+0.5*(0.04*np.power(v,2)+5*v+140-u+I)
    v=v+0.5*(0.04*np.power(v,2)+5*v+140-u+I)
    u=u+np.multiply(a,(np.multiply(b,v)-u))
    progress.update(t)

firings = np.asarray(firings)
firings = np.flipud(firings)

imsave('pyprimo.bmp', np.ones(firings.shape) - firings)
#plt.matshow(firings, cmap='Greys')
#plt.show()
#plt.plot(range(timelimit), sampleVTracer, 'b', range(timelimit), sampleUTracer, 'r', range(timelimit), [30 for tl in range(timelimit)], "g")
#plt.show()

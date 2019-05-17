
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import adaptfilt as adf
from scipy import signal as sgn

# Import data
data = pd.read_csv('datasetB.csv', header=None)
data = data.values[:, 1:5]

# Compute indices S to separate the different signals
Q = (np.diff(data[:, 3]) > 0.001)+0  # señal algo raro pasa
S = [0]
k = 0
while k < len(Q):
    if Q[k] == 1:                  # si algo ha pasado, guarda indice de donde y salta ventana de 1000
        S.append(k)
        k += 1000
    else:
        k += 1                       # de lo contrario sigue recorriendo vector de errores

for i in range(1, len(S)-1):         # los indices menos el primero y el ultimo son modificados a valores medios
    S[i] = int((S[i]+S[i+1])/2)
S[-1] = len(Q)


# Correlation between optical sgn and linear combination of  accelerometer sgn
def my_fun(x):
    num = np.cov(x[0]*qx+x[1]*qy+x[2]*qz, qV)[0, 1]
    den = np.std(x[0]*qx+x[1]*qy+x[2]*qz)*np.std(qV)
    return -num/den


M = 150     # FIR filter taps
step = 0.001   # FIR filter step
newV = []
# Run adaptive filter on each signal
for r in range(0, len(S)-1):

    qx = data[S[r]+2:S[r+1]-2, 0]  # x-axis
    qy = data[S[r]+2:S[r+1]-2, 1]  # y-axis
    qz = data[S[r]+2:S[r+1]-2, 2]  # z-axis
    qV = data[S[r]+2:S[r+1]-2, 3]  # optical signal

    # Find coefficients of linear combination s.t. correlation between optical
    # signal and linear combination of accelerometer signals is maximal
    res = minimize(my_fun, np.array([1, 1, 1]), method='Nelder-Mead', tol=1e-6)
    xF = res.x
    qF = qx*xF[0]+qy*xF[1]+qz*xF[2]

    u = qF.copy()
    d = qV.copy()

    # Apply adaptive filter
    y, e, w = adf.lms(u, d, M, step)
    plt.subplot(int((len(S)-1)/2), 2, r+1)
    plt.plot(d[M-1:len(y)+M-1], 'b', e, 'r')

    for i in y:
        newV.append(i)

    # Compute residual interference
    f1, pw1 = sgn.welch(d[M-1:len(y)+M-1])      # PSD optical sgn
    f2, pw2 = sgn.welch(e)                      # PSD optical sgn minus interference
    avgP1 = sum(pw1)/len(pw1)                   # power optical sgn
    avgP2 = sum(pw2)/len(pw2)                   # power optical sgn minus interference
    SNR = round((1/(avgP1/avgP2))*100, 1)       # inverse SNR
    print('Residual interference: {0}%'.format(SNR))

plt.show()

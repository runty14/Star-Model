import numpy as np

# Начальное распределение температуры
def T0_pow4(Teff, tau, qtau):
    return np.pow((3. / 4) * np.pow(Teff, 4) * (tau + qtau), 0.25)

# Constant of Boltzmann
k = 1.38e-23
def formulaSaha(u_rplus1, u_r, Temp, I_r):
    mult1 = 0.333
    mult2 = 2 * u_rplus1 / u_r
    mult3 = np.pow(Temp, 2.5)
    mult4 = np.exp(-I_r / k * Temp)
    return mult1 * mult2 * mult3 * mult4

def sumIonizedElements(N0, N1, N2):
    return N0 + N1 + N2

def x_iz(N0, N1, N2, i):
    if i == 1:
        return N1 / (N0 + N1 + N2)
    else:
        return N2 / (N0 + N1 + N2)

def avgElectronsToNuclear(eps, x_1z, x_2z):
    sum1 = np.sum(np.multiply(eps, x_1z))
    sum2 = 2 * np.sum(np.multiply(eps, x_2z))
    devided = np.sum(eps)
    return (sum1 + sum2) / devided

# Formula 1.24
def search_Pe0(Pg0, E):
    return Pg0 * (E + 1) / E

# Formula 1.29
def search_a0z(I_0z, Temp, C):
    return np.pow(C, -1) * np.exp(I_0z / (k * Temp))

def search_a1z(I_1z, Temp, C):
    return C * np.exp(-I_1z / (k * Temp))

# Formula 1.29
def search_dEdPe(I_0z, I_1z, Temp, C, eps, Pe_prev):
    mult1 = 1 / sum(eps)
    a0z = search_a0z(I_0z, Temp, C)
    a1z = search_a1z(I_1z, Temp, C)
    sum1 = 0
    sum2 = 0
    for i in range(len(eps)):
        mult21 = eps[i] * (-a0z[i] + a1z[i] * np.pow(Pe_prev, -2))
        mult22 = np.pow((a0z[i] * Pe_prev + a1z[i] * np.pow(Pe_prev, -2) + 1), 2)
        sum1 += mult21 / mult22
        mult31 = 2 * eps[i] * (2 * a0z[i] * Pe_prev + 1) * np.pow(a1z[i], 2) *\
                 np.exp(I_1z[i] / (k * Temp))
        mult32 = np.pow((np.pow(Pe_prev, 2) * a0z[i] + Pe_prev + a1z[i]), 2)
        sum2 += mult31 / mult32
    return mult1 * (sum1 - sum2)

# Formula 1.27
def search_dPe(Pg0, Pe_prev, dEdPe, E):
    ratio1 = E / (E + 1)
    devisible = Pg0 * ratio1 - Pe_prev
    devider = 1 - (Pg0 / (E + 1)) * (1 - ratio1) * dEdPe
    return devisible / devider

def search_Pe(Pe_prev, dPe):
    return Pe_prev + dPe

# Начальные параметры
Teff = 5770
g = np.exp(4.44)
Pg0 = 2.940
qtau = []
tau = []

# Массив температур по глубинам (начальные условия)
T = T0_pow4(Teff, tau, qtau)

countPlasts = 20
# Cycle for each plast
for i in countPlasts:
    Temp = T[i]
    # C, N, O, Na, Mg, Si, K, Ca, Cr, Fe, Ni
    N_Z = []

    N0z = []
    N1z = []
    N2z = []

    # eps [i] = N_Z[i] / N_H
    eps = [
        4e-4, 1e-4, 7.2e-4, 2e-6,
        3.8e-5, 3.6e-5, 3.3e-7, 2.3e-6,
        4e-7, 3.2e-5, 1.8e-6
    ]
    # Potencial ionezed with 0 state
    I_0z = [
        11.264, 14.454, 13.614, 5.138,
        7.644, 8.149, 4.339, 6.111,
        6.754, 7.896, 7.633
    ]
    # Potencial ionezed with 1 state
    I_1z = [
        24.376, 29.605, 35.146, 47.290,
        15.030, 16.340, 31.810, 11.870,
        16.490, 16.180, 18.150
    ]

    countElements = 11
    for i in range(countElements):
        N_Z.append(sumIonizedElements(N0z[i], N1z[i], N2z[i]))

    X1z = []
    X2z = []
    for i in range(countElements):
        X1z[i] = x_iz(N0z[i], N1z[i], N2z[i], 1)
        X2z[i] = x_iz(N0z[i], N1z[i], N2z[i], 2)

    E = avgElectronsToNuclear(eps, X1z, X2z)
    Pe0 = search_Pe0(Pg0, E)
    Pe = Pe0
    Pe_prev = Pe0 + 1
    C = 0.333 * np.pow(Temp, 2.5)

    countIter = 0
    err = 1e-7
    while(abs(Pe_prev - Pe) < err):
        dEdPe = search_dEdPe(I_0z, I_1z, Temp, C, eps, Pe)
        dPe = search_dPe(Pg0, Pe, dEdPe, E)
        Pe_prev = Pe
        Pe = search_Pe(Pe)
        countIter += 1


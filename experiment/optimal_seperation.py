# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 18:03:48 2018

@author: gqs0108
"""

from scipy.optimize import linprog
import numpy as np
import matplotlib.pyplot as plt

n = 100

x = np.arange(n)
y = np.zeros(n)
y[40:60] = np.linspace(0,1,20)
y[60:] = 1
y += np.random.randn(n)*.1

row1 = np.concatenate([-1*y, y, [-1]], axis=0)
row2 = np.concatenate([y, -1*y, [-1]], axis=0)
bub = np.zeros(2)
Aub = np.stack([row1, row2], axis=0)
augI = np.concatenate([np.eye(2*n), np.zeros((2*n,1))], axis=1)
Aub = np.concatenate([Aub, augI, -1*augI], axis=0)
bub = np.concatenate([bub, np.ones(2*n), np.zeros(2*n)])
for i in range(n-1):
    row1 = np.zeros(2*n + 1)
    row1[i] = 1
    row1[i+1] = -1
    row2 = np.zeros(2*n + 1)
    row2[i+n] = -1
    row2[i+n+1] = 1
    rows = np.stack([row1, row2], axis=0)
    Aub = np.concatenate([Aub, rows], axis=0)
    bub = np.concatenate([bub, np.zeros(2)], axis=0)
   
Aeq = np.concatenate([np.eye(n), np.eye(n), np.zeros((n,1))], axis=1)
beq = np.ones(Aeq.shape[0])
c = np.zeros(2*n+1)
c[-1] = 1

result = linprog(c, Aub, bub, Aeq, beq)

plt.plot(y)
plt.plot(result.x[:n])
plt.plot(result.x[n:-1])
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 18:03:48 2018

@author: gqs0108
"""

from scipy.optimize import linprog
import numpy as np
import matplotlib.pyplot as plt
import cv2

def downsample_avg(img, ds):
    img_rs = img[:(img.shape[0]//ds)*ds,:(img.shape[1]//ds)*ds]
    img_ds = img_rs.reshape((img_rs.shape[0]//ds, ds, img_rs.shape[1]//ds, -1)).mean(3).mean(1)
    return img_ds

def section_1d(f, nu):
    l = f.shape[0]
    Aub = np.empty((0,2*l))
    for i in range(l):
        x = np.zeros(l-1)
        x[:i] = 1
        row1 = np.concatenate([[-1, -1], -1*x, x], axis=0)
        row2 = np.concatenate([[1, -1], x, -1*x], axis=0)
        Aub = np.concatenate([Aub, row1[None,:], row2[None,:]], axis=0)
    
    bub = np.stack([np.ones(l)*-1*f, np.ones(l)*f], axis=1).ravel()
        
    Aeq = np.empty((1,2*l))
    Aeq[0,0] = l
    Aeq[0,1] = 0
    Aeq[0,2:l+1] = np.arange(l-1,0,-1)
    Aeq[0,l+1:] = -1*np.arange(l-1,0,-1)
    
    beq = np.sum(f)
    
    c = np.ones(2*l) / l
    c[0] = 0
    c[1] = nu
    
    result = linprog(c, Aub, bub, Aeq, beq)
    
    return result

def section_2d(img, nu):
    l = min(img.shape[0], img.shape[1])
    img = img[:l, :l]
    eps = 0
    x = np.arange(l*(l-1)).reshape((l,l-1))
    xp = x + 1
    xm = x + 1 + l*(l-1)
    y = np.arange(l*(l-1)).reshape((l-1,l))
    yp = y + 1 + 2*l*(l-1)
    ym = y + 1 + 3*l*(l-1)
    p = np.arange(l*l).reshape((l,l)) + 1 + 4*l*(l-1)
    L = p.ravel()[-1] + 1
    Aeq = []
    beq = [0]*(2*l*(l-1))
    
    for i in range(1,l):
        row = np.zeros(L)
        row[p[0,i]] = 1
        row[p[0,i-1]] = -1
        row[xp[0,i-1]] = -1
        row[xm[0,i-1]] = 1
        Aeq.append(row)
        row = np.zeros(L)
        row[p[i,0]] = 1
        row[p[i-1,0]] = -1
        row[yp[i-1,0]] = -1
        row[ym[i-1,0]] = 1
        Aeq.append(row)
        for j in range(1,l):
            row = np.zeros(L)
            row[p[i,j]] = 1
            row[p[i-1,j]] = -1
            row[yp[i-1,j]] = -1
            row[ym[i-1,j]] = 1
            Aeq.append(row)
            row = np.zeros(L)
            row[p[i,j]] = 1
            row[p[i,j-1]] = -1
            row[xp[i,j-1]] = -1
            row[xm[i,j-1]] = 1
            Aeq.append(row)
    row = np.zeros(L)
    row[p.ravel()] = 1
    Aeq.append(row)
    Aeq = np.array(Aeq)
    beq.append(np.sum(img))
    beq = np.array(beq)
    
    Aub = np.concatenate([np.eye(l**2), -1*np.eye(l**2)], axis=0)
    Aub = np.concatenate([np.zeros((2*l**2, 4*l*(l-1))), Aub], axis=1)
    Aub = np.concatenate([np.ones((2*l**2,1))*-1, Aub], axis=1)
    bub = np.concatenate([img.ravel(), -1*img.ravel()], axis=0)
    
    c_ind = np.concatenate([xp.ravel(), xm.ravel(), yp.ravel(), ym.ravel()], axis=0)
    c =  np.zeros(L)
    c[c_ind] = 1/(2*l**2)
    c[eps] = nu
    
    print("solving...")
    
    result = linprog(c, Aub, bub, Aeq, beq, method='interior-point')
    
    print(result.message)
    
    if result.success:
        p = result.x[p.ravel()]
        p = p.reshape((l,l))
        
        return p, result
    
    return c, Aub, bub, Aeq, beq

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--downsample','-d',type=int,default=20)
    parser.add_argument('--nu', '-n', type=float, default=.15)
    args = parser.parse_args()
    
    ds = args.downsample
    nu = args.nu
    im = cv2.imread("../images/180905_Test_cells.tif")
    blue, _1, _2 = cv2.split(im)
    blue_ds = downsample_avg(blue, ds)
    p, result = section_2d(blue_ds, nu)
    print("Cost function: {}".format(result.fun))
    print("epsilon: {}".format(result.x[0]))
    plt.imshow(p)
    plt.show()
    
    
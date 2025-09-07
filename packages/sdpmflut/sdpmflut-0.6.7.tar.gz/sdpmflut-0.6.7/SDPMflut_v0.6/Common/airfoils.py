#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package airfoils contains functions to define and interpolate airfoil sections.

This code is part of the SDPMflut Python distribution.
Copyright (C) 2024 Grigorios Dimitriadis

This program is free software: you can redistribute it and/or modify it 
under the terms of the GNU General Public License as published by the 
Free Software Foundation, either version 3 of the License, or (at your 
option) any later version.
 
This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
Public License for more details.

You should have received a copy of the GNU General Public License along 
with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import math
import numpy as np
import sys
from scipy.interpolate import CubicSpline

def nacafourdigit(xp,m,mpt,teclosed):
    # Function that calculates the thickness distribution and camber line of  
    # any NACA four digit airfoil.
    # xp: x-coordinates starting from 1, going to 0 and back up to 1. 
    #     Length of xp must be 2*m+1
    # mpt: 4-digit serial number of airfoil, e.g. 2412 or 0008.
    # teclosed: if teclosed=0, the normal NACA four digit thickness equation is
    #   used. If teclosed=1, a modified equation is used to close the trailing
    #   edge
    # zp: z-coordinates of the complete airfoil shape. They are arranged from
    # the lower trailing edge towards the leading edge and then towards the
    # upper trailing edge.
    # zcamb: z-coordinates of the camber line only. They are arranged from the
    # leading edge to the trailing edge.

    # Check if the length of the xp vector is correct
    if len(xp) != 2*m+1:
        sys.exit('Length of xp must be 2*m+1')
    # End if    
    # Calculate airfoil parameters from serial number
    maxcamb=math.floor(mpt/1000)/100.0    # Maximum camber
    mpt=mpt-maxcamb*1.0e5
    maxpos=math.floor(mpt/100.0)/10.0       # Position of maximum camber
    mpt=mpt-maxpos*1.0e3
    t=mpt/100.0                      # Thickness ratio
    
    # x-coordinates from leading to trailing edge (0 to 1).
    xpup=xp[m:2*m+1]
    if teclosed == 0:
        # Calculate thickness distribution from equation in Abbott and Von Doenhoff
        zpthick=t/0.2*(0.2969*np.sqrt(xpup)-0.126*xpup-0.35160*xpup**2+0.2843*xpup**3-0.1015*xpup**4)
    elif teclosed == 1:
        # Adapt highest order coefficient to close the trailing edge
        zpthick=t/0.2*(0.2969*np.sqrt(xpup)-0.126*xpup-0.3516*xpup**2+0.2843*xpup**3-0.1036*xpup**4)
    else:
        print('teclosed must be equal to 0 or 1')

    # Initialize the camber line and its derivative
    zpcamb=np.zeros(m+1)
    dzpcambdx=np.zeros(m+1)
    if maxpos != 0:
        # Find x-coordinates that lie upwstream of the maximum camber position
        iko=np.argwhere(xpup <= maxpos)
        # Use camber equation in Abbott and Von Doenhoff
        zpcamb[iko]=maxcamb/maxpos**2.0*(2.0*maxpos*xpup[iko]-xpup[iko]**2.0)
        dzpcambdx[iko]=maxcamb/maxpos**2.0*(2.0*maxpos-2*xpup[iko])
       # Find x-coordinates that lie downsream of the maximum camber position
        iko=np.argwhere(xpup > maxpos)
        # Use camber equation in Abbott and Von Doenhoff
        zpcamb[iko]=maxcamb/((1-maxpos)**2.0)*((1-2.0*maxpos)+2.0*maxpos*xpup[iko]-xpup[iko]**2.0)
        dzpcambdx[iko]=maxcamb/((1-maxpos)**2.0)*(2.0*maxpos-2.0*xpup[iko])
    
    # Assemble complete z-coordinates from lower trailing edge to upper
    # trailing edge.
    # According to http://airfoiltools.com/airfoil/naca4digit#calculation   
    theta=np.arctan(dzpcambdx)
    xup=xpup-zpthick*np.sin(theta)
    xlo=xpup+zpthick*np.sin(theta)
    zup=zpcamb+zpthick*np.cos(theta)
    zlo=zpcamb-zpthick*np.cos(theta)

    # Interpolate the upper surface using linear interpolation
    zpup=np.interp(xpup,np.abs(xup),zup) # Use np.abs(xup) to avoid having negative x values near the leading edge
    # Interpolate the lower surface using lienar interpolation
    zplo=np.interp(xpup,xlo,zlo)
    # Assemble the complete z coordinate vector
    zp=np.concatenate([np.flip(zplo),zpup[1:m+1]]) 
    
    return zp, zpcamb

def nacafivedigit(xp,m,mpt,teclosed):
    # Function that calculates the thickness distribution and camber line of  
    # any NACA five digit airfoil.
    # xp: x-coordinates starting from 1, going to 0 and back up to 1. 
    #     Length of xp must be 2*m+1
    # mpt: 4-digit serial number of airfoil, e.g. 23015.
    # teclosed: if teclosed=0, the normal NACA four digit thickness equation is
    #   used. If teclosed=1, a modified equation is used to close the trailing
    #   edge
    # zp: z-coordinates of the complete airfoil shape. They are arranged from
    # the lower trailing edge towards the leading edge and then towards the
    # upper trailing edge.
    # zcamb: z-coordinates of the camber line only. They are arranged from the
    # leading edge to the trailing edge.

    # Check if the length of the xp vector is correct
    if len(xp) != 2*m+1:
        sys.exit('Length of xp must be 2*m+1')
    # End if    
    # Calculate airfoil parameters from serial number
    meanline=math.floor(mpt/100)    # Mean line 
    t=(mpt-meanline*100.0)/100.0    # Thickness ratio
    
    if meanline == 210:
        maxpos=0.05
        r=0.0580
        k1=361.4
        k2dk1=0.    # Only for reflex airfoils
    elif meanline == 220:
        maxpos=0.1
        r=0.1260
        k1=51.64
        k2dk1=0.    # Only for reflex airfoils
    elif meanline == 230:
        maxpos=0.15
        r=0.2025
        k1=15.957
        k2dk1=0.    # Only for reflex airfoils
    elif meanline == 240:
        maxpos=0.2
        r=0.29
        k1=6.643
        k2dk1=0.    # Only for reflex airfoils
    elif meanline == 250:
        maxpos=0.25
        r=0.391
        k1=3.23
        k2dk1=0.    # Only for reflex airfoils
    elif meanline == 221:
        maxpos=0.1
        r=0.13
        k1=51.99
        k2dk1=0.000764    # Only for reflex airfoils
    elif meanline == 231:
        maxpos=0.15
        r=0.2170
        k1=15.793
        k2dk1=0.00677    # Only for reflex airfoils
    elif meanline == 241:
        maxpos=0.2
        r=0.3180
        k1=6.520
        k2dk1=0.0303    # Only for reflex airfoils
    elif meanline == 251:
        maxpos=0.25
        r=0.4410
        k1=3.191
        k2dk1=0.1355    # Only for reflex airfoils
    # End if     
    
    # x-coordinates from leading to trailing edge (0 to 1).
    xpup=xp[m:2*m+1]
    if teclosed == 0:
        # Calculate thickness distribution from equation in Abbott and Von Doenhoff
        zpthick=t/0.2*(0.2969*np.sqrt(xpup)-0.126*xpup-0.35160*xpup**2+0.2843*xpup**3-0.1015*xpup**4)
    elif teclosed == 1:
        # Adapt highest order coefficient to close the trailing edge
        zpthick=t/0.2*(0.2969*np.sqrt(xpup)-0.126*xpup-0.3516*xpup**2+0.2843*xpup**3-0.1036*xpup**4)
    else:
        print('teclosed must be equal to 0 or 1')

    # Initialize the camber line and its derivative
    zpcamb=np.zeros(m+1)
    dzpcambdx=np.zeros(m+1)
    if k2dk1 == 0.:
        # Standard airfoils
        iko=np.argwhere(xpup <= r)
        zpcamb[iko]=1/6.0*k1*(xpup[iko]**3.0-3.0*r*xpup[iko]**2.0+r**2.0*(3.0-r)*xpup[iko])
        dzpcambdx[iko]=1/6.0*k1*(3.0*xpup[iko]**2.0-6.0*r*xpup[iko]+r**2.0*(3.0-r))
        iko=np.argwhere(xpup > r)
        zpcamb[iko]=1/6.0*k1*r**3.0*(1-xpup[iko])
        dzpcambdx[iko]=-1/6*k1*r**3.0
    else:
        # Reflex airfoils
        iko=np.argwhere(xpup <= r)
        zpcamb[iko]=1/6.0*k1*((xpup[iko]-r)**3.0-k2dk1*(1-r)**3.0*xpup[iko]-r**3.0*xpup[iko]+r**3.0)
        dzpcambdx[iko]=1/6.0*k1*(3.0*(xpup[iko]-r)**2.0-k2dk1*(1-r)**3.0-r**3.0)
        iko=np.argwhere(xpup > r)
        zpcamb[iko]=1/6.0*k1*(k2dk1*(xpup[iko]-r)**3.0-k2dk1*(1-r)**3.0*xpup[iko]-r**3.0*xpup[iko]+r**3.0)
        dzpcambdx[iko]=1/6.0*k1*(3.0*k2dk1*(xpup[iko]-r)**2.0-k2dk1*(1-r)**3.0-r**3.0)
    # End if    
    
    # Assemble complete z-coordinates from lower trailing edge to upper
    # trailing edge.
    # According to http://airfoiltools.com/airfoil/naca4digit#calculation   
    theta=np.arctan(dzpcambdx)
    xup=xpup-zpthick*np.sin(theta)
    xlo=xpup+zpthick*np.sin(theta)
    zup=zpcamb+zpthick*np.cos(theta)
    zlo=zpcamb-zpthick*np.cos(theta)

    # Interpolate the upper surface using linear interpolation
    zpup=np.interp(xpup,np.abs(xup),zup) # Use np.abs(xup) to avoid having negative x values near the leading edge
    # Interpolate the lower surface using lienar interpolation
    zplo=np.interp(xpup,xlo,zlo)
    # Assemble the complete z coordinate vector
    zp=np.concatenate([np.flip(zplo),zpup[1:m+1]]) 
    
    return zp, zpcamb


def biconvex(xp,m,thick):
    # Function that calculates the coordinates of a biconvex airfoil.
    # m: Number of panels on the upper surface. There will be another m panels
    #    on the lower surface and the total number of vertices will be m+1.
    # xp: x-coordinates starting from 1, going to 0 and back up to 1. 
    #     Length of xp must be 2*m+1
    # t: airfoil thickness-to-chord ratio
    # zp: z-coordinates of the complete airfoil shape. They are arranged from

    # x-coordinates from leading to trailing edge (0 to 1).
    xpup=xp[m:2*m+1]
    zpup=2.0*(xpup-xpup**2)*thick
    # Ensure that the trailing edge thickness is exactly zero
    zpup[m]=0.0
    # Assemble the complete z coordinate vector
    zp=np.concatenate([-np.flip(zpup),zpup[1:m+1]]) 
    zpcamb=np.zeros(m+1)

    return zp, zpcamb

def flatplate(xp,m):
    # Create a flat plate airfoil section with unit thickness.
    # m: Number of panels on the upper surface. There will be another m panels
    #    on the lower surface and the total number of vertices will be m+1.
    # xp: x-coordinates starting from 1, going to 0 and back up to 1. 
    #     Length of xp must be 2*m+1
    # zp: z-coordinates of the complete airfoil shape. They are arranged from
    # the lower trailing edge towards the leading edge and then towards the
    # upper trailing edge.
    # zcamb: z-coordinates of the camber line only. They are arranged from the
    # leading edge to the trailing edge.
    
    # Check if the length of the xp vector is correct
    if len(xp) != 2*m+1:
        sys.exit('Length of xp must be 2*m+1')
    # End if    
    # Set upper surface to 1
    zpup=np.ones(m+1)
    zpup[0]=0.0
    zpup[m]=0.0
    # Assemble the complete z coordinate vector
    zp=np.concatenate([-zpup,zpup[1:m+1]]) 
    # Set camber line to zero
    zpcamb=np.zeros(m+1)    
    
    return zp, zpcamb

def NACA65A004(xp,m,dataset):
    # Outputs the coordinates of the NACA 65A004 airfoil, starting at the lower
    # trailing edge and ending at the upper leading edge
    # xp: (2*m+1)*1 vector of x coordinates of panel endpoints on both surfaces
    # m: Number of panels on each surface
    # dataset: 1 - coordinates from NACA TN 3047
    #         2 - coordinates from AGARD Report No. 765
    # zp: (2*m+1)*1 vector of z coordinates of panel endpoints on both surfaces
    # zpcamb: (m+1)*1 vector of z coordinates of camber point on one surface
    
    # Check if the length of the xp vector is correct
    if len(xp) != 2*m+1:
        sys.exit('Length of xp must be 2*m+1')
    # End if   
    # NACA65A004 coordinates
    if dataset == 1:
        # From NACA TN 3047
        xy=np.array([(0, 0),
            (0.00025, 0.0007),
            (0.00050, 0.00098),
            (0.00100, 0.00140),
            (0.0025, 0.00226),
            (0.0050, 0.00314),
            (0.0075, 0.00381),
            (0.0100, 0.00437),
            (0.0125, 0.00485),
            (0.0175, 0.00566),
            (0.0250, 0.00659),
            (0.0375, 0.00777),
            (0.0500, 0.00879),
            (0.0750, 0.01061),
            (0.1000, 0.01215),
            (0.1500, 0.01464),
            (0.2000, 0.01655),
            (0.2500, 0.01798),
            (0.3000, 0.01900),
            (0.3500, 0.01967),
            (0.4000, 0.02000),
            (0.4500, 0.01998),
            (0.5000, 0.01957),
            (0.5500, 0.01875),
            (0.6000, 0.01754),
            (0.6500, 0.01597),
            (0.7000, 0.01410),
            (0.7500, 0.01200),
            (0.8000, 0.00972),
            (0.8500, 0.00735),
            (0.9000, 0.00494),
            (0.9500, 0.00250),
            (0.9600, 0.00200),
            (0.9700, 0.00150),
            (0.9800, 0.00100),
            (0.9900, 0.00050),
            (1.0000, 0.00000)])
    elif dataset == 2:
        # From AGARD Report No. 765 (AD-A199 433)
        xy=np.array([(0.0, 0.00),
            (0.005, 0.00304),
            (0.0075, 0.00368),
            (0.0125, 0.00469),
            (0.025,  0.00647),
            (0.050,  0.00875),
            (0.075,  0.01059),
            (0.10,   0.01213),
            (0.15,   0.01459),
            (0.20,   0.01645),
            (0.25,   0.01788),
            (0.30,   0.01892),
            (0.35,   0.01962),
            (0.40,   0.01997),
            (0.45,   0.01996),
            (0.50,   0.01954),
            (0.55,   0.01868),
            (0.60,   0.01743),
            (0.65,   0.01586),
            (0.70,   0.01402),
            (0.75,   0.01195),
            (0.80,   0.00967),
            (0.85,   0.00729),
            (0.90,   0.00490),
            (0.95,   0.00250),
            (1.00,   0.00009)])
    # End if
    # Interpolate coordinates onto xp
    cs = CubicSpline(xy[:,0], xy[:,1])
    # Calculate airfoil shape at xp
    zp=cs(xp)
    # Mirror lower side
    zp[0:m]=-zp[0:m]
    # Camber is zero, it is a symmetric airfoil
    zpcamb=np.zeros(m+1)
    
    return zp, zpcamb
    
def NASASC20414(xp,m,teclosed):
    
    # Check if the length of the xp vector is correct
    if len(xp) != 2*m+1:
        sys.exit('Length of xp must be 2*m+1')
    # End if    
    xzup=np.array([(0.000000,  0.000000),
             (0.002000,  0.010800),
             (0.005000,  0.016600),
             (0.010000,  0.022500),
             (0.020000,  0.029900),
             (0.030000,  0.035000),
             (0.040000,  0.038900),
             (0.050000,  0.042100),
             (0.060000,  0.044800),
             (0.070000,  0.047100),
             (0.080000,  0.049100),
             (0.090000,  0.051000),
             (0.100000,  0.052700),
             (0.110000,  0.054200),
             (0.120000,  0.055600),
             (0.130000,  0.056900),
             (0.140000,  0.058100),
             (0.150000,  0.059200),
             (0.160000,  0.060200),
             (0.170000,  0.061200),
             (0.180000,  0.062100),
             (0.190000,  0.062900),
             (0.200000,  0.063700),
             (0.210000,  0.064400),
             (0.220000,  0.065100),
             (0.230000,  0.065700),
             (0.240000,  0.066300),
             (0.250000,  0.066800),
             (0.260000,  0.067300),
             (0.270000,  0.067700),
             (0.280000,  0.068100),
             (0.290000,  0.068500),
             (0.300000,  0.068800),
             (0.310000,  0.069100),
             (0.320000,  0.069300),
             (0.330000,  0.069500),
             (0.340000,  0.069700),
             (0.350000,  0.069900),
             (0.360000,  0.070000),
             (0.370000,  0.070100),
             (0.380000,  0.070200),
             (0.390000,  0.070200),
             (0.400000,  0.070200),
             (0.410000,  0.070200),
             (0.420000,  0.070100),
             (0.430000,  0.070000),
             (0.440000,  0.069900),
             (0.450000,  0.069700),
             (0.460000,  0.069500),
             (0.470000,  0.069300),
             (0.480000,  0.069000),
             (0.490000,  0.068700),
             (0.500000,  0.068400),
             (0.510000,  0.068000),
             (0.520000,  0.067600),
             (0.530000,  0.067200),
             (0.540000,  0.066700),
             (0.550000,  0.066200),
             (0.560000,  0.065600),
             (0.570000,  0.065000),
             (0.580000,  0.064300),
             (0.590000,  0.063600),
             (0.600000,  0.062800),
             (0.610000,  0.062000),
             (0.620000,  0.061100),
             (0.630000,  0.060200),
             (0.640000,  0.059300),
             (0.650000,  0.058300),
             (0.660000,  0.057300),
             (0.670000,  0.056200),
             (0.680000,  0.055100),
             (0.690000,  0.054000),
             (0.700000,  0.052800),
             (0.710000,  0.051600),
             (0.720000,  0.050300),
             (0.730000,  0.049000),
             (0.740000,  0.047700),
             (0.750000,  0.046400),
             (0.760000,  0.045000),
             (0.770000,  0.043600),
             (0.780000,  0.042200),
             (0.790000,  0.040700),
             (0.800000,  0.039200),
             (0.810000,  0.037700),
             (0.820000,  0.036200),
             (0.830000,  0.034600),
             (0.840000,  0.033000),
             (0.850000,  0.031400),
             (0.860000,  0.029800),
             (0.870000,  0.028100),
             (0.880000,  0.026400),
             (0.890000,  0.024700),
             (0.900000,  0.022900),
             (0.910000,  0.021100),
             (0.920000,  0.019300),
             (0.930000,  0.017500),
             (0.940000,  0.015600),
             (0.950000,  0.013700),
             (0.960000,  0.011700),
             (0.970000,  0.009700),
             (0.980000,  0.007600),
             (0.990000,  0.005500),
             (1.000000,  0.003300)])
   
    xzlo=np.array([(0.000000,  0.000000),
            (0.002000, -0.010800),
            (0.005000, -0.016600),
            (0.010000, -0.022500),
            (0.020000, -0.029900),
            (0.030000, -0.035000),
            (0.040000, -0.038900),
            (0.050000, -0.042100),
            (0.060000, -0.044800),
            (0.070000, -0.047200),
            (0.080000, -0.049300),
            (0.090000, -0.051200),
            (0.100000, -0.052900),
            (0.110000, -0.054500),
            (0.120000, -0.056000),
            (0.130000, -0.057300),
            (0.140000, -0.058500),
            (0.150000, -0.059700),
            (0.160000, -0.060800),
            (0.170000, -0.061800),
            (0.180000, -0.062700),
            (0.190000, -0.063600),
            (0.200000, -0.064400),
            (0.210000, -0.065100),
            (0.220000, -0.065800),
            (0.230000, -0.066400),
            (0.240000, -0.067000),
            (0.250000, -0.067500),
            (0.260000, -0.068000),
            (0.270000, -0.068400),
            (0.280000, -0.068800),
            (0.290000, -0.069100),
            (0.300000, -0.069400),
            (0.310000, -0.069600),
            (0.320000, -0.069800),
            (0.330000, -0.069900),
            (0.340000, -0.070000),
            (0.350000, -0.070000),
            (0.360000, -0.070000),
            (0.370000, -0.069900),
            (0.380000, -0.069800),
            (0.390000, -0.069700),
            (0.400000, -0.069500),
            (0.410000, -0.069300),
            (0.420000, -0.069000),
            (0.430000, -0.068600),
            (0.440000, -0.068200),
            (0.450000, -0.067700),
            (0.460000, -0.067200),
            (0.470000, -0.066600),
            (0.480000, -0.065900),
            (0.490000, -0.065100),
            (0.500000, -0.064200),
            (0.510000, -0.063300),
            (0.520000, -0.062300),
            (0.530000, -0.061200),
            (0.540000, -0.060000),
            (0.550000, -0.058700),
            (0.560000, -0.057300),
            (0.570000, -0.055800),
            (0.580000, -0.054300),
            (0.590000, -0.052700),
            (0.600000, -0.051000),
            (0.610000, -0.049200),
            (0.620000, -0.047400),
            (0.630000, -0.045500),
            (0.640000, -0.043500),
            (0.650000, -0.041500),
            (0.660000, -0.039400),
            (0.670000, -0.037300),
            (0.680000, -0.035200),
            (0.690000, -0.033000),
            (0.700000, -0.030800),
            (0.710000, -0.028600),
            (0.720000, -0.026400),
            (0.730000, -0.024200),
            (0.740000, -0.022000),
            (0.750000, -0.019800),
            (0.760000, -0.017700),
            (0.770000, -0.015600),
            (0.780000, -0.013600),
            (0.790000, -0.011600),
            (0.800000, -0.009700),
            (0.810000, -0.007800),
            (0.820000, -0.006000),
            (0.830000, -0.004300),
            (0.840000, -0.002700),
            (0.850000, -0.001200),
            (0.860000,  0.000100),
            (0.870000,  0.001300),
            (0.880000,  0.002300),
            (0.890000,  0.003200),
            (0.900000,  0.003900),
            (0.910000,  0.004400),
            (0.920000,  0.004600),
            (0.930000,  0.004600),
            (0.940000,  0.004300),
            (0.950000,  0.003800),
            (0.960000,  0.003100),
            (0.970000,  0.002100),
            (0.980000,  0.000800),
            (0.990000, -0.000800),
            (1.000000, -0.002700)])
    if round(teclosed) == 1:
           xzup[-1,1]=0.0
           xzlo[-1,1]=0.0
    # End if
    # Interpolate the upper surface using piecewise cubic interpolation
    cs = CubicSpline(xzup[:,0], xzup[:,1])
    zpup=cs(xp[m:2*m+1])
    # Interpolate the lower surface using piecewise cubic interpolation
    cs = CubicSpline(xzlo[:,0], xzlo[:,1])
    zplo=cs(xp[0:m+1])
    # Assemble the complete z coordinate vector
    zp=np.concatenate([zplo,zpup[1:m+1]]) 
    # Calculate the camber line
    zpcamb=(zpup+np.flip(zplo))/2.0

    return zp, zpcamb

def NACA64A010(xp,m,teclosed):
    
    # Check if the length of the xp vector is correct
    if len(xp) != 2*m+1:
        sys.exit('Length of xp must be 2*m+1')
    # End if    
    xz=np.array([(0,         0),
        (0.0010,    0.0036),
        (0.0020,    0.0051),
        (0.0050,    0.0080),
        (0.0100,    0.0112),
        (0.0200,    0.0154),
        (0.0300,    0.0185),
        (0.0400,    0.0211),
        (0.0500,    0.0235),
        (0.0600,    0.0255),
        (0.0700,    0.0273),
        (0.0800,    0.0290),
        (0.0900,    0.0306),
        (0.1000,    0.0320),
        (0.1100,    0.0334),
        (0.1200,    0.0347),
        (0.1300,    0.0359),
        (0.1400,    0.0371),
        (0.1500,    0.0382),
        (0.1600,    0.0392),
        (0.1700,    0.0402),
        (0.1800,    0.0411),
        (0.1900,    0.0419),
        (0.2000,    0.0427),
        (0.2100,    0.0435),
        (0.2200,    0.0442),
        (0.2300,    0.0449),
        (0.2400,    0.0455),
        (0.2500,    0.0461),
        (0.2600,    0.0466),
        (0.2700,    0.0471),
        (0.2800,    0.0476),
        (0.2900,    0.0480),
        (0.3000,    0.0484),
        (0.3100,    0.0487),
        (0.3200,    0.0490),
        (0.3300,    0.0493),
        (0.3400,    0.0495),
        (0.3500,    0.0497),
        (0.3600,    0.0498),
        (0.3700,    0.0499),
        (0.3800,    0.0500),
        (0.3900,    0.0500),
        (0.4000,    0.0499),
        (0.4100,    0.0498),
        (0.4200,    0.0496),
        (0.4300,    0.0495),
        (0.4400,    0.0492),
        (0.4500,    0.0489),
        (0.4600,    0.0486),
        (0.4700,    0.0482),
        (0.4800,    0.0478),
        (0.4900,    0.0473),
        (0.5000,    0.0469),
        (0.5100,    0.0463),
        (0.5200,    0.0458),
        (0.5300,    0.0452),
        (0.5400,    0.0445),
        (0.5500,    0.0439),
        (0.5600,    0.0432),
        (0.5700,    0.0425),
        (0.5800,    0.0418),
        (0.5900,    0.0410),
        (0.6000,    0.0402),
        (0.6100,    0.0394),
        (0.6200,    0.0386),
        (0.6300,    0.0377),
        (0.6400,    0.0369),
        (0.6500,    0.0360),
        (0.6600,    0.0350),
        (0.6700,    0.0341),
        (0.6800,    0.0332),
        (0.6900,    0.0322),
        (0.7000,    0.0313),
        (0.7100,    0.0303),
        (0.7200,    0.0293),
        (0.7300,    0.0283),
        (0.7400,    0.0273),
        (0.7500,    0.0263),
        (0.7600,    0.0253),
        (0.7700,    0.0243),
        (0.7800,    0.0233),
        (0.7900,    0.0223),
        (0.8000,    0.0213),
        (0.8100,    0.0203),
        (0.8200,    0.0193),
        (0.8300,    0.0183),
        (0.8400,    0.0173),
        (0.8500,    0.0163),
        (0.8600,    0.0153),
        (0.8700,    0.0143),
        (0.8800,    0.0133),
        (0.8900,    0.0123),
        (0.9000,    0.0113),
        (0.9100,    0.0103),
        (0.9200,    0.0093),
        (0.9300,    0.0083),
        (0.9400,    0.0073),
        (0.9500,    0.0063),
        (0.9600,    0.0053),
        (0.9700,    0.0043),
        (0.9800,    0.0033),
        (0.9900,    0.0023),
        (1.0000,    0.0013)])
    if round(teclosed) == 1:
           xz[-1,1]=0.0
    # End if
    # Interpolate coordinates onto xp
    cs = CubicSpline(xz[:,0], xz[:,1])
    # Calculate airfoil shape at xp
    zp=cs(xp)
    # Mirror lower side
    zp[0:m]=-zp[0:m]
    # Camber is zero, it is a symmetric airfoil
    zpcamb=np.zeros(m+1)

    return zp, zpcamb    
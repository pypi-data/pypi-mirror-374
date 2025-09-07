#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program flutter_SDPM_NACA0012 calculates the flutter boundary of the NASA
Benchmark Supercritical wing with pitch and plunge degrees of freedom.

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

# Input installation directory
install_dir='/Users/Username/Documents/Python/SDPMflut_v0.6/Common/'
# install_dir=r"C:\Users\Username\Documents\Python\SDPMflut\Common"  # Windows example
# Import libraries and packages
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append(install_dir)
from SDPMgeometry import SDPMgeometry_trap_fun
import flutsol
import SDPMcalcs
# Create SDPM data types
tp_trap, tp_body, _=SDPMcalcs.SDPMdtypes()
                    
# Run data from wind tunnel flutter tests. Source:
# Experimental unsteady pressures at flutter on the supercritical wing
# benchmark model. Bryan E. Dansbeny et al, AIAA-93-1592-CP, pp. 2504-2514.
# Test Cases for Flutter of the Benchmark Models Rectangular Wings on the Pitch
# and Plunge Apparatus. Robert M. Bennett. Defense Technical Information Center
# Compilation Part Notice ADPO10713.
# Chordwise reference length in m
cref=16*0.0254 
# Free stream Mach number
Machdata=np.array([0.319, 0.509, 0.730, 0.769, 0.326, 0.513, 0.725, 0.766, 0.335, 0.503, 0.619, 0.679, 0.738, 0.762])
# Mean pitch angle
alpha0data=np.array([-0.1, 0.0, -0.2, 0.0, 1.0, 1.0, 1.2, 1.2, 0.0, -0.2, -0.4, -0.1, -0.1, -0.1])*np.pi/180.0
# Speed of sound data
asounddata=np.array([1142.2, 1129.6, 1120.2, 1115.6, 1140.2, 1130.4, 1121.1, 1117.8, 1139, 1132, 1125, 1123, 1118, 1116])*0.3048
# Free stream air density (kg/m^3)
rhodata=515.37882*np.array([2.113, 0.922, 0.516, 0.459, 2.097, 0.930, 0.516, 0.461, 2.132, 0.987, 0.693, 0.588, 0.522, 0.480])*1e-3
# Mass ratio Mh./(pi*rhodata*b*c0^2/4)
mubardata=np.array([776, 1779, 3178, 3569, 782, 1763, 3180, 3556, 769, 1660, 2366, 2789, 3142, 3413])*1.0
# Flutter speed (m/s)
Uflutdata=np.array([364.4, 574.7, 817.6, 857.6, 372.0, 580.0, 812.4, 856.8, 381.9, 569.5, 696.9, 763.0, 825.0, 850.8])*0.3048
# Flutter frequency (rad/s)
freqflutdata=np.array([4.60, 4.47, 4.23, 4.14, 4.55, 4.43, 4.19, 4.09, 4.55, 4.47, 4.39, 4.36, 4.27, 4.23])*2.0*np.pi
# Frequency of first torsion mode from experiment
omega_alpha=5.25*2.0*np.pi 
# Nondimensional flutter speed Uflutdata./(c0/2*34.2*sqrt(mubardata)). 
# Different values in different sources and they both do not agree with the definition of Ustar
# Ustardata=[0.595 0.620 0.622 0.692 0.605 0.628 0.655 0.653 0.626 0.636 0.652 0.657 0.669 0.662]; According to Rivera
# Ustardata=[0.68 0.73 0.83 0.82 0.70 0.74 0.82 0.84 0.72 0.75 0.78 0.79 0.82 0.82]; According to AIAA-93-1592-CP
# Recalculate experimental Ustar values
Ustardata=np.divide(Uflutdata,cref/2.0*omega_alpha*np.sqrt(mubardata))
# Flutter frequency ratio freqflutdata/wn(2)
freqratdata=np.array([0.876, 0.851, 0.806, 0.789, 0.867, 0.844, 0.798, 0.779,  0.867, 0.851, 0.836, 0.830, 0.813, 0.806])
# Flutter dynamic pressure data (N/m^2)
dynpressdata=np.array([140.3, 152.2, 172.4, 168.9, 145.1, 156.4, 170.2, 169.3, 155.5, 160.1, 168.2, 171.1, 177.6, 173.8])*4.44822/0.3048**2
# Static pressure calculated from speed of sound and density
pressdata=asounddata**2.*rhodata/1.4
# Reduced frequency
kflutdata=np.array([0.0529, 0.0326, 0.0217, 0.0202, 0.0513, 0.0320, 0.0216, 0.0200, 0.0499, 0.0329, 0.0264, 0.0239, 0.0217, 0.0208])
# Total number of runs
nruns=len(Machdata);
# Structural dynamic properties measured from experiment
mass=6.1*14.5939 # Mass of wing in kg
Ialpha=2.7*14.5939*0.3048**2 # Moment of inertia around pitch axis in kg*m^2
fn=np.array([3.32, 5.25])   # Natural frequencies in plunge and pitch in Hz
wn=2*np.pi*fn             #  Natural frequencies in plunge and pitch in rad/s
zeta0=np.array([0.00, 0.00]) # Damping ratios in plunge and pitch
Kh=2637*4.44822/0.3048; # Plunge stiffness in N/m
Kalpha=2964*0.3048*4.44822; # Pitch stiffness in Nm/rad
# Number of structural modes
nmodes=2

# Select reduced frequency values
kvec=np.array([0.001, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.1])

# Select airspeed range in m/s
Uv=np.linspace(50,320,num=101)

# Choose order of pressure coefficient equation
cp_order=2 # 1 for linear and 2 for second order

# Set values of mean (or steady) angle of sideslip
beta0=0.0*np.pi/180.0  # Angle of sideslip in rad

# Number of bodies
nbody=1
# Initialize body struct array
body=np.zeros(nbody,dtype=tp_body)

# Input first body
ibody=0         # Index of body
name='wing'     # Name of body
# Choose numbers of panels for this wing and its wake
nhalf=10    # Number of spanwise panels per half-wing.
m=20        # Number of chordwise panels
nchords=10  # Set length of wake in chord lengths
# Calculate number of chordwise wake rings
mw=m*nchords 
# Number of trapezoidal sections
ntrap=1;
# Initialize trapezoidal section struct array
trap=np.zeros(ntrap,dtype=tp_trap)

# Input wing geometry
bhalf=32*0.0254                 # Span in m of half-wing
c0=16*0.0254                    # Root chord in m
lamda=1.0                       # Taper ratio
LamdaLE=0.0*np.pi/180.0;        # Sweep at leading edge
roottwist=0.0*np.pi/180.0       # Twist angle at the root in rad
tiptwist=0.0*np.pi/180.0        # Twist angle at the root in rad
dihedral=0.0*np.pi/180.0        # Dihedral angle in rad
twistcent=0.0                   # Chordwise axis around which twist is defined
# Chordwise distance of root leading edge from previous
# trapezoidal section's tip leading edge
xledist=0.0  
# Coordinates of points through which pitch axis passes
xf0=c0/2.0
yf0=0.0
zf0=0.0
# Set airfoil name (must be the filename of a function in the Common directory)
airfoil='NASASC20414'
# Set airfoil parameters
teclosed=1                  # 1 for closed trailing edge, 0 otherwise
# Assemble airfoil parameter values
airfoil_params=np.array([teclosed, 0])

# Calculate panel aspect ratio
panelAR=(c0/m)/(bhalf/nhalf)
if panelAR < 0.1:
    sys.exit('Panel aspect ratio too low. Increase n or decrease m.')

# Arrange all data into trapezoidal sections
trap[0]=np.array([(c0,xledist,bhalf,lamda,LamdaLE,roottwist,tiptwist,twistcent,dihedral,airfoil,airfoil_params,airfoil,airfoil_params)],dtype=tp_trap)

# Minimum number of spanwise panels per trapezoidal section
nmin=3
# Chordwise panel distribution: 1 constant, 2 denser at the leading edge
linchord=0
# Spanwise panel distribution: 1 constant, 2 denser at the wing tip(s)
linspan=0
# Define root leading edge
lexyz=np.array([0, 0, 0])
# Define roll, pitch and yaw angles
rollpitchyaw=np.array([0, 0, 0])*np.pi/180
# Define roll, pitch and yaw centre (x,y,z position of rotation centre)
rollpitchyaw_cent=np.array([0, 0, 0])
mirroredwing=2 # If mirroredwing=-1: a left half-wing will be created
                # If mirroredwing=1: a right half-wing will be created
                # If mirroredwing=2: two mirrored half-wings will be created.
# dir_tau is the direction in which the unit tangent vector  for this wing
# (tauxx, tauxy, tauxz) has a zero component
dir_tau=2
# Calculate vertices of wing panels
body=SDPMgeometry_trap_fun(body,ibody,m,mw,nhalf,mirroredwing,linchord,linspan,trap,name,dir_tau,rollpitchyaw,rollpitchyaw_cent,lexyz,nmin)

# The pitch-plunge wing has two degrees of freedom and therefore two modes of 
# vibration
nmodes=2
# Parameter to determine if the structural model concerns a half wing or a
# full wing.
halfwing=1 # halfwing=1: half-wing. halfwing=0: full wing

# Plot all bodies
fig, axx = plt.subplots(subplot_kw={"projection": "3d"})
for i in range (0,len(body)):
    axx.plot_surface(body['Xp0'][i], body['Yp0'][i], body['Zp0'][i])
# End for
axx.set_proj_type('ortho')  # FOV = 0 deg
axx.axis('equal')
axx.set_xlabel("$x$", labelpad=10)
axx.set_ylabel("$y$", labelpad=10)
axx.set_zlabel("$z$", labelpad=10)
axx.zaxis.labelpad=-2
axx.view_init(26, -120)
plt.show()

# Assemble the indices of the body panels, spanwise body panels, wake
# panels etc. for all bodies.
allbodies=SDPMcalcs.allbodyindex(body)

# Calculate structural matrices
A=np.matrix([[mass, 0.0],[0.0, Ialpha]]) # Structural mass matrix
E=np.matrix([[Kh, 0.0],[0.0, Kalpha]])   # Structural stiffness matrix
C=np.matrix([[2*mass*wn[0]*zeta0[0], 0.0],[0.0, 2*Ialpha*wn[1]*zeta0[1]]])   # Structural damping matrix

# Initialize results arrays for all runs
Ustarvec=np.zeros((nruns))    # Flutter speed index
Uflutvec=np.zeros((nruns))    # Flutter speed in m/s
dynpressvec=np.zeros((nruns)) # Flutter dynamic pressure in Pa
freqflutvec=np.zeros((nruns)) # Flutter frequency in rad/s
kflutvec=np.zeros((nruns))    # Reduced flutter frequency

print('Calculating flutter solutions for all experimental test cases')
for irun in range (0,nruns):
    print('')
    print('Simulating run '+str(irun+1))

    # Set Mach number of current run
    Mach=Machdata[irun]
    # Set mass ratio of current run
    mubar=mubardata[irun]
    # Set density of current run
    rho=rhodata[irun]
    # Calculate subsonic compressibility factor
    beta=np.sqrt(1-Mach**2); 
    # Set mean angle of attack
    alpha0=alpha0data[irun]
    
    # Calculate steady aerodynamic pressures and loads
    body,allbodies,Aphi,Bphi,Cphi,barUinf,barVinf,barWinf=SDPMcalcs.steadysolve(body,allbodies,cp_order,Mach,beta,alpha0,beta0,xf0,yf0,zf0,install_dir)
        
    # Calculate flutter solution for pitch-plunge motion
    Uflut,freqflut,kflut,dynpressflut,omega,zeta=flutsol.flutsolve_pitchplunge(body,allbodies,kvec,Uv,nmodes,Aphi,Bphi,Cphi,barUinf,barVinf,barWinf,c0,Mach,beta,cp_order,A,C,E,rho,wn,halfwing,xf0,yf0,zf0,install_dir)
    
    # Print out flutter solution
    if Uflut != 0: # If there is a flutter point
        # Store flutter data for this run
        Uflutvec[irun]=Uflut
        Ustarvec[irun]=Uflut/(c0/2.0*omega_alpha*np.sqrt(mubar))
        dynpressvec[irun]=dynpressflut
        freqflutvec[irun]=freqflut
        kflutvec[irun]=kflut
        # Compare to experimental data        
        print('Flutter speed (m/s)')
        print('SDPM      Exp.')
        print(np.array([Uflut,Uflutdata[irun]]))
        print('Flutter frequency (rad/s)')
        print('SDPM      Exp.')
        print(np.array([freqflut,freqflutdata[irun]]))
    else:
        print('Could not find a flutter point for run '+str(irun))
    # End if 
# End loop for irun

# Plot flutter airspeed
fig, axx = plt.subplots()
axx.plot(Machdata[0:4], Uflutvec[0:4], label = "SDPM $\\alpha_0=0^{\\circ}$")
axx.plot(Machdata[4:8], Uflutvec[4:8], label = "SDPM $\\alpha_0=1^{\\circ}$")
axx.plot(Machdata[8:nruns], Uflutvec[8:nruns], label = "SDPM grit")
axx.plot(Machdata[0:4], Uflutdata[0:4], "o", label = "Exp. $\\alpha_0=0^{\\circ}$")
axx.plot(Machdata[4:8], Uflutdata[4:8], "o", label = "Exp. $\\alpha_0=1^{\\circ}$")
axx.plot(Machdata[8:nruns], Uflutdata[8:nruns], "o", label = "Exp. grit")
axx.set_xlabel("$M_{\\infty}$")
axx.set_ylabel("$U_F$ (m/s)")
axx.grid()
axx.legend(loc="upper left")

# Plot flutter frequency
fig, axx = plt.subplots()
axx.plot(Machdata[0:4], freqflutvec[0:4], label = "SDPM $\\alpha_0=0^{\\circ}$")
axx.plot(Machdata[4:8], freqflutvec[4:8], label = "SDPM $\\alpha_0=1^{\\circ}$")
axx.plot(Machdata[8:nruns], freqflutvec[8:nruns], label = "SDPM grit")
axx.plot(Machdata[0:4], freqflutdata[0:4], "o", label = "Exp. $\\alpha_0=0^{\\circ}$")
axx.plot(Machdata[4:8], freqflutdata[4:8], "o", label = "Exp. $\\alpha_0=1^{\\circ}$")
axx.plot(Machdata[8:nruns], freqflutdata[8:nruns], "o", label = "Exp. grit")
axx.set_xlabel("$M_{\\infty}$")
axx.set_ylabel("$\\omega_F$ (rad/s)")
axx.grid()
axx.legend(loc="lower left")

# Plot flutter speed index
fig, axx = plt.subplots()
axx.plot(Machdata[0:4], Ustarvec[0:4], label = "SDPM $\\alpha_0=0^{\\circ}$")
axx.plot(Machdata[4:8], Ustarvec[4:8], label = "SDPM $\\alpha_0=1^{\\circ}$")
axx.plot(Machdata[8:nruns], Ustarvec[8:nruns], label = "SDPM grit")
axx.plot(Machdata[0:4], Ustardata[0:4], "o", label = "Exp. $\\alpha_0=0^{\\circ}$")
axx.plot(Machdata[4:8], Ustardata[4:8], "o", label = "Exp. $\\alpha_0=1^{\\circ}$")
axx.plot(Machdata[8:nruns], Ustardata[8:nruns], "o", label = "Exp. grit")
axx.set_xlabel("$M_{\\infty}$")
axx.set_ylabel("$Q^*_F$")
axx.grid()
axx.legend(loc="upper left")

# Plot flutter frequency ratio
fig, axx = plt.subplots()
axx.plot(Machdata[0:4], freqflutvec[0:4]/omega_alpha, label = "SDPM $\\alpha_0=0^{\\circ}$")
axx.plot(Machdata[4:8], freqflutvec[4:8]/omega_alpha, label = "SDPM $\\alpha_0=1^{\\circ}$")
axx.plot(Machdata[8:nruns], freqflutvec[8:nruns]/omega_alpha, label = "SDPM grit")
axx.plot(Machdata[0:4], freqratdata[0:4], "o", label = "Exp. $\\alpha_0=0^{\\circ}$")
axx.plot(Machdata[4:8], freqratdata[4:8], "o", label = "Exp. $\\alpha_0=1^{\\circ}$")
axx.plot(Machdata[8:nruns], freqratdata[8:nruns], "o", label = "Exp. grit")
axx.set_xlabel("$M_{\\infty}$")
axx.set_ylabel("$\\omega_F/\\omega_alpha$")
axx.grid()
axx.legend(loc="lower left")

# Plot flutter dynamic pressure
fig, axx = plt.subplots()
axx.plot(Machdata[0:4], dynpressvec[0:4], label = "SDPM $\\alpha_0=0^{\\circ}$")
axx.plot(Machdata[4:8], dynpressvec[4:8], label = "SDPM $\\alpha_0=1^{\\circ}$")
axx.plot(Machdata[8:nruns], dynpressvec[8:nruns], label = "SDPM grit")
axx.plot(Machdata[0:4], dynpressdata[0:4], "o", label = "Exp. $\\alpha_0=0^{\\circ}$")
axx.plot(Machdata[4:8], dynpressdata[4:8], "o", label = "Exp. $\\alpha_0=1^{\\circ}$")
axx.plot(Machdata[8:nruns], dynpressdata[8:nruns], "o", label = "Exp. grit")
axx.set_xlabel("$M_{\\infty}$")
axx.set_ylabel("$1/2\\rho Q_F^2$ (Pa)")
axx.grid()
axx.legend(loc="upper left")

# Plot flutter reduced frequency
fig, axx = plt.subplots()
axx.plot(Machdata[0:4], kflutvec[0:4], label = "SDPM $\\alpha_0=0^{\\circ}$")
axx.plot(Machdata[4:8], kflutvec[4:8], label = "SDPM $\\alpha_0=1^{\\circ}$")
axx.plot(Machdata[8:nruns], kflutvec[8:nruns], label = "SDPM grit")
axx.plot(Machdata[0:4], kflutdata[0:4], "o", label = "Exp. $\\alpha_0=0^{\\circ}$")
axx.plot(Machdata[4:8], kflutdata[4:8], "o", label = "Exp. $\\alpha_0=1^{\\circ}$")
axx.plot(Machdata[8:nruns], kflutdata[8:nruns], "o", label = "Exp. grit")
axx.set_xlabel("$M_{\\infty}$")
axx.set_ylabel("$k$")
axx.grid()
axx.legend(loc="upper right")


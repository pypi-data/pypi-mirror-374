#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program flutter_SDPM_AGARD calculates the flutter boundary of the
AGARD 445.6 weakened wing.

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

# Input path to Common directory
install_dir=r'/Username/mbgssgd3/Documents/Python/SDPMflut_v0.6/Common/'
# install_dir=r"C:\Users\Username\Documents\Python\SDPMflut\Common"  # Windows example
# Import libraries and packages
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append(install_dir)
from SDPMgeometry import SDPMgeometry_trap_fun
import flutsol
import FEmodes
import SDPMcalcs
import VanZylTtail 
# Create SDPM data types
tp_trap, tp_body, _=SDPMcalcs.SDPMdtypes()

# Run data from wind tunnel flutter tests. Source:
# T-tail flutter:Potential-flow modelling,experimental validation
# and flight tests, J. Murua et al, Progress in Aerospace Sciences,
# Vol 71, 2014, pp. 54–84.
# Horizontal tailplane pitch angle (rad)
alphaHdata=np.array([-4.0, 0.0, 4.0, 8.0])*np.pi/180.0
# Flutter speed (m/s) (two repetitions at each tailplane pitch angle)
Uflutdata=np.array([[55.04, 45.92, 38.93, 34.89], [53.96, 44.94, 37.95, 33.88]])
# Steady lift coefficient of horizontal tailplane from CSIR simulations
CL0Hdata=np.array([-0.1996, -0.0003, 0.2012, 0.3902, 0.5905])  # Lift coefficient values
CL0HUdata=np.array([53.40, 47.58, 43.26, 39.63, 36.43]) # Corresponding airspeed values
# Total number of runs
nruns=alphaHdata.size;
# Set wind tunnel Mach number
Mach=0.167
# Calculate subsonic compressibility factor
beta=np.sqrt(1-Mach**2); 
# Set air density at an altitude of 1340 m
rho=1.0750      # kg/m^3
# Set speed of sound in air at an altitude of 1340 m
asound=335.1116 # m/s

# Select reduced frequency values
kvec=np.array([0.001, 0.01, 0.05, 0.08, 0.1, 0.15, 0.2, 0.5, 1.0, 1.8])

# Select airspeed range in m/s
Uv=np.linspace(10,70,num=101)

# Choose order of pressure coefficient equation
cp_order=2 # 1 for linear and 2 for second order

# Set values of mean (or steady) angles of attack and sideslip
alpha0=0.0*np.pi/180.0  # Angle of attack in rad
beta0=0.0*np.pi/180.0  # Angle of sideslip in rad

# The T-tail consists of a fin, two fin fairing halves (upper and lower) and 
# two horizontal tailplane halves (left and right) that are attached to the fin 
# fairing halves.
# Number of bodies
nbody=5
# Initialize body struct array
body=np.zeros(nbody,dtype=tp_body)

# Set numbers of spanwise and chordwise panels. These are not global: the
# two halves of the horizontal tailplane have nhalf spanwise and 2*m
# chordwise panels. The fin has 2*nhalf spanwise and 2*m chordwise panels.
# The fairing has 2 spanwise and 4*m chordwise panels.
nhalf=10    # Number of spanwise panels per half-wing.
m=20        # Number of chordwise panels. MUST BE EVEN!
nchords=10  # Set length of wake in chord lengths
# Chordwise and spanwise panel distributions for all bodies
# Chordwise panel distribution: 1 constant, 2 denser at the leading edge
linchord=0
# Spanwise panel distribution: 1 constant, 2 denser at the wing tip(s)
linspan=0
# Calculate number of chordwise wake rings
mw=m*nchords

###### Input fin description
# Index of fin
ibody=0
# Name of body
name='Fin'
# Number of trapezoidal sections
ntrap=2;
# Initialize trapezoidal section struct array
trap=np.zeros(ntrap,dtype=tp_trap)

# Input geometry of first trapezoidal section
bhalf=0.217                     # Span in m 
c0=0.425                        # Root chord in m
lamda=1                         # Taper ratio
LamdaLE=0.*np.pi/180.0;         # Sweep at leading edge in rad
roottwist=0.0*np.pi/180.0       # Twist angle at the root in rad
tiptwist=0.0*np.pi/180.0        # Twist angle at the root in rad
twistcent=0.0                   # Chordwise axis around which twist is defined
dihedral=0.0*np.pi/180.0        # Dihedral angle in rad
# Chordwise distance of root leading edge from previous
# trapezoidal section's tip leading edge
xledist=0.0
# Set airfoil name (must be the filename of a function in the Common directory)
airfoil='nacafourdigit'
# Set airfoil parameters
mpt=12
teclosed=1
# dir_tau is the direction in which the unit tangent vector  for this wing
# (tauxx, tauxy, tauxz) has a zero component
dir_tau=3
# Calculate panel aspect ratio
panelAR=(c0/m)/(bhalf/nhalf)
if panelAR < 0.1:
    sys.exit('Panel aspect ratio too low. Increase n or decrease m.')
# Assemble airfoil parameter values
airfoil_params=np.array([mpt, teclosed])
# Arrange all data into trapezoidal sections
trap[0]=np.array([(c0,xledist,bhalf,lamda,LamdaLE,roottwist,tiptwist,twistcent,dihedral,airfoil,airfoil_params,airfoil,airfoil_params)],dtype=tp_trap)

# Input geometry of second trapezoidal section
bhalf=0.714-0.217               # Span in m 
c0=0.425                        # Root chord in m
lamda=1                         # Taper ratio
LamdaLE=33.1*np.pi/180.0;       # Sweep at leading edge in rad
roottwist=0.0*np.pi/180.0       # Twist angle at the root in rad
tiptwist=0.0*np.pi/180.0        # Twist angle at the root in rad
twistcent=0.0                   # Chordwise axis around which twist is defined
dihedral=0.0*np.pi/180.0        # Dihedral angle in rad
# Set airfoil name (must be the filename of a function in the Common directory)
# Chordwise distance of root leading edge from previous
# trapezoidal section's tip leading edge
xledist=0.0
airfoil='nacafourdigit'
# Set airfoil parameters
mpt=12
teclosed=1
# Calculate panel aspect ratio
panelAR=(c0/m)/(bhalf/nhalf)
if panelAR < 0.1:
    sys.exit('Panel aspect ratio too low. Increase n or decrease m.')
# Assemble airfoil parameter values
airfoil_params=np.array([mpt, teclosed])
# Arrange all data into trapezoidal sections
trap[1]=np.array([(c0,xledist,bhalf,lamda,LamdaLE,roottwist,tiptwist,twistcent,dihedral,airfoil,airfoil_params,airfoil,airfoil_params)],dtype=tp_trap)

# Create SDPM grid for fin
# Minimum number of spanwise panels per trapezoidal section
nmin=3
# Define root leading edge
lexyz=np.array([0, 0, 0])
# Define roll, pitch and yaw angles
rollpitchyaw=np.array([90, 0, 0])*np.pi/180;
# Define roll, pitch and yaw centre (x,y,z position of rotation centre)
rollpitchyaw_cent=np.array([0, 0, 0]);
mirroredwing=1 # If mirroredwing=1: a right half-wing will be created
# dir_tau is the direction in which the unit tangent vector  for this wing
# (tauxx, tauxy, tauxz) has a zero component
dir_tau=3
# Create fin SDPM grid                
body=SDPMgeometry_trap_fun(body,ibody,m,mw,2*nhalf,mirroredwing,linchord,linspan,trap,name,dir_tau,rollpitchyaw,rollpitchyaw_cent,lexyz,nmin)

###### Input horizontal tailplane description

# Number of trapezoidal sections
ntrap=1;
# Initialize trapezoidal section struct array
trapHT=np.zeros(ntrap,dtype=tp_trap)

# Input geometry of first trapezoidal section
bhalf=0.625                     # Span in m 
c0=0.363                # Root chord in m
lamda=0.1/0.363               # Taper ratio
LamdaLE=36.5*np.pi/180.0;     # Sweep at leading edge in rad
roottwist=0.0*np.pi/180.0       # Twist angle at the root in rad
tiptwist=0.0*np.pi/180.0        # Twist angle at the root in rad
twistcent=0.0                   # Chordwise axis around which twist is defined
dihedral=0.0*np.pi/180.0      # Dihedral angle in rad
# Chordwise distance of root leading edge from previous
# trapezoidal section's tip leading edge
xledist=0.0
# Set airfoil name (must be the filename of a function in the Common directory)
airfoil='nacafivedigit'
# Set airfoil parameters
mpt=23015
teclosed=1
# Calculate panel aspect ratio
panelAR=(c0/m)/(bhalf/nhalf)
if panelAR < 0.1:
    sys.exit('Panel aspect ratio too low. Increase n or decrease m.')
# Assemble airfoil parameter values
airfoil_params=np.array([mpt, teclosed])
# Arrange all data into trapezoidal sections
trapHT[0]=np.array([(c0,xledist,bhalf,lamda,LamdaLE,roottwist,tiptwist,twistcent,dihedral,airfoil,airfoil_params,airfoil,airfoil_params)],dtype=tp_trap)
# Tailplane pitch axis location
xf=0.375+c0*0.741
yf=0;
zf=0.763;

# We will create the horizontal tailplanes in the run loop because they
# will be rotated to the correct pitch angle.

###### Input fin fairing description

# Fairing root position
x0Root=0.324
# Fairing chord
c0Fair=0.528
# Vertical location of fairing root
zroot=0.714
# Vertical location of fairing tip
ztip=0.812
# Assemble root and tip of fairing
z_root_tip=np.array([zroot, ztip])
airfoil_fairing='nacafourdigit'
# Set airfoil parameters
mpt=12
teclosed=1
airfoil_params_fairing=np.array([mpt, teclosed])

# We will create the fin fairing when we have rotated the tailplanes to the
# right angle.

# File name of Matlab mat file that contains the structural model
fname='modes_Ttail.mat' 
# Choose number of modes to include in the flutter calculation
nmodes=3    # Cannot exceed number of modes in FE model
zeta0=np.zeros(nmodes) # Structural damping ratios
zeta0[0:3]=np.array([0.62, 2.11, 3.45])/100.0
# Parameter to determine if the structural model concerns a half wing or a
# full wing.
halfwing=0 # halfwing=1: half-wing. halfwing=0: full wing

# Assemble the indices of the body panels, spanwise body panels, wake
# panels etc. for all bodies.
allbodies=SDPMcalcs.allbodyindex(body)
    
# Acquire structural matrices and mode shapes
A, C, E, wn, xxplot, yyplot, zzplot, modeshapesx, modeshapesy, modeshapesz, \
    modeshapesRx, modeshapesRy, modeshapesRz=FEmodes.FE_matrices(fname,zeta0,nmodes)

# Initialize results arrays for all runs
Uflutvec=np.zeros((nruns))    # Flutter speed in m/s
dynpressvec=np.zeros((nruns)) # Flutter dynamic pressure in Pa
freqflutvec=np.zeros((nruns)) # Flutter frequency in rad/s
kflutvec=np.zeros((nruns))    # Reduced flutter frequency
CL0Hvec=np.zeros((nruns))    # Steady tailplane lift coefficient

print('Calculating flutter solutions for all experimental test cases')
for irun in range (0,nruns):
    print('')
    print('Simulating run '+str(irun+1))
        
    # Set incidence of horizontal tailplane of current run
    alpha_H=alphaHdata[irun]
    
    # Create SDPM grid for the two halves of the tailplane
    # Index of right horizontal taiplane
    ibody=1
    # Name of body
    name='HTright'
    # Minimum number of spanwise panels per trapezoidal section
    nmin=3
    # Define root leading edge
    lexyz=np.array([0.375, 0.0244, 0.763])
    # Define roll, pitch and yaw angles
    rollpitchyaw=np.array([0, alpha_H, 0])
    # Define roll, pitch and yaw centre (x,y,z position of rotation centre)
    rollpitchyaw_cent=np.array([xf, yf, zf]);
    mirroredwing=1 # If mirroredwing=1: a right half-wing will be created
    # dir_tau is the direction in which the unit tangent vector  for this wing
    # (tauxx, tauxy, tauxz) has a zero component
    dir_tau=2
    # Create right horizontal taiplane SDPM grid                
    body=SDPMgeometry_trap_fun(body,ibody,m,mw,nhalf,mirroredwing,linchord,linspan,trapHT,name,dir_tau,rollpitchyaw,rollpitchyaw_cent,lexyz,nmin)
   
    # Index of left horizontal taiplane
    ibody=2
    # Name of body
    name='HTleft'
    # Minimum number of spanwise panels per trapezoidal section
    nmin=3
    # Define root leading edge
    lexyz=np.array([0.375, -0.0244, 0.763])
    # Define roll, pitch and yaw angles
    rollpitchyaw=np.array([0, alpha_H, 0])
    # Define roll, pitch and yaw centre (x,y,z position of rotation centre)
    rollpitchyaw_cent=np.array([xf, yf, zf]);
    mirroredwing=-1 # If mirroredwing=-1: a left half-wing will be created
    # dir_tau is the direction in which the unit tangent vector  for this wing
    # (tauxx, tauxy, tauxz) has a zero component
    dir_tau=2
    # Create left horizontal taiplane SDPM grid                
    body=SDPMgeometry_trap_fun(body,ibody,m,mw,nhalf,mirroredwing,linchord,linspan,trapHT,name,dir_tau,rollpitchyaw,rollpitchyaw_cent,lexyz,nmin)
    
    # Create SDPM grid for the fin fairing. 
    # There are two bodies, one for the lower and one for the upper
    # fairing, separated by the taiplane.
    body=VanZylTtail.finfairing(body,airfoil_fairing,airfoil_params_fairing,z_root_tip,x0Root,c0Fair)
    
    if irun == 1:
        # Plot all bodies for zero tailplane incidence
        fig, axx = plt.subplots(subplot_kw={"projection": "3d"})
        for i in range(0,nbody):
            axx.plot_surface(body['Xp0'][i], body['Yp0'][i], body['Zp0'][i])
        # End for
        axx.set_proj_type('ortho')  # FOV = 0 deg
        axx.axis('equal')
        axx.set_xlabel("$x$", labelpad=10)
        axx.set_ylabel("$y$", labelpad=10)
        axx.set_zlabel("$z$", labelpad=-2)
        axx.view_init(26, -120)
        plt.show() 
    # End if
 
    # Select which root chord will be used as the characteristic length scale
    c0=body['c0'][1]
    
    # Assemble the indices of the body panels, spanwise body panels, wake
    # panels etc. for all bodies.
    allbodies=SDPMcalcs.allbodyindex(body)
    
    # Interpolate mode shapes
    body=VanZylTtail.ttailmodesinterp(body,z_root_tip,nmodes,xxplot,yyplot,zzplot,modeshapesx,modeshapesy,modeshapesz,modeshapesRx,modeshapesRy,modeshapesRz)
    
    # Assemble mode shapes for all bodies into global matrices
    allbodies=SDPMcalcs.modeshape_assemble(body,allbodies,nmodes)
    
    # Calculate steady aerodynamic pressures and loads
    body,allbodies,Aphi,Bphi,Cphi,barUinf,barVinf,barWinf=SDPMcalcs.steadysolve(body,allbodies,cp_order,Mach,beta,alpha0,beta0,0.0,0.0,0.0,install_dir)
    # Steady horizontal tailplane lift coefficient, calculated for the 
    # right tailplane only. The total lift coefficient is the same.  
    CL0Hvec[irun]=np.sum(allbodies['Fz0'][0][allbodies['inds'][0][1]:allbodies['inds'][0][2]])/body['S'][2]
   
    # Calculate flutter solution for flexible modes  
    Uflut,freqflut,kflut,dynpressflut,omega,zeta=flutsol.flutsolve_flex(body,allbodies,kvec,Uv,nmodes,Aphi,Bphi,Cphi,barUinf,barVinf,barWinf,c0,Mach,beta,cp_order,A,C,E,rho,wn,halfwing,install_dir)

    # Print out flutter solution
    if Uflut != 0: # If there is a flutter point
        # Store flutter data for this run
        UflutEAS=np.sqrt(2.0*dynpressflut/1.225) # Equivalent airspeed based on the flutter dynamic pressure
        Uflutvec[irun]=UflutEAS
        dynpressvec[irun]=dynpressflut
        freqflutvec[irun]=freqflut
        kflutvec[irun]=kflut        
        # Compare to experimental data
        print('Flutter speed (m/s)')
        print('SDPM      Exp.')
        print(np.array([Uflutvec[irun],Uflutdata[1,irun]]))
    else:
        print('Could not find a flutter point for run '+str(irun))
    # End if
# End loop for irun

# Plot flutter airspeed
fig, axx = plt.subplots()
axx.plot(alphaHdata*180.0/np.pi, Uflutvec, label = "SDPM")
axx.plot(alphaHdata*180.0/np.pi, Uflutdata[0,:], "o",label = "Exp.",)
axx.plot(alphaHdata*180.0/np.pi, Uflutdata[1,:], "o",label = "Exp.",)
axx.set_xlabel("$\\alpha_H$ (rad)")
axx.set_ylabel("$Q_F$ (m/s)")
axx.grid()
axx.legend(loc="lower left")

# Plot steady tailplane lift coefficient against flutter airspeed
fig, axx = plt.subplots()
axx.plot(CL0Hvec, Uflutvec, label = "SDPM")
axx.plot(CL0Hdata, CL0HUdata, "o",label = "Exp.",)
axx.set_xlabel("$C_{L_{0,HTP}}$")
axx.set_ylabel("$Q_F$ (m/s)")
axx.grid()
axx.legend(loc="upper right")


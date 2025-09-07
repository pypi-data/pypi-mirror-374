#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program flutter_SDPM_NACA0012 calculates the flutter boundary of a
NACA 0012 rectangular wing with pitch and plunge degrees of freedom.

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
install_dir = r"D:\KHADER\KHADER_OTHER_PROJECTS\SDPMflut\Dev\KhaderX\sdpmflut\SDPMflut_v0.6\Common"
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
tp_trap, tp_body, _ = SDPMcalcs.SDPMdtypes()

# Run data from wind tunnel flutter tests. Sources:
# Test Cases for Flutter of the Benchmark Models Rectangular Wings on the Pitch
# and Plunge Apparatus. Robert M. Bennett. Defense Technical Information Center
# Compilation Part Notice ADPO10713.
# PRESSURE MEASUREMENTS ON A RECTANGULAR WING WITH A NACA0012 AIRFOIL DURING
# CONVENTIONAL FLUTTER. J. A. Rivera, Jr., et al. NASA Technical Memorandum
# 104211. July 1992.
# Chordwise reference length in m
cref = 16 * 0.0254
# Free stream Mach number
Machdata = np.array([0.3, 0.39, 0.45, 0.51, 0.61, 0.67, 0.71, 0.77, 0.80, 0.82])
# Mean pitch angle
alpha0data = (
    np.array([0.07, 0.07, 0.06, 0.06, 0.05, 0.05, 0.04, 0.07, 0.06, 0.07])
    * np.pi
    / 180.0
)
# Speed of sound data
asounddata = (
    np.array(
        [1127.2, 1132.3, 1129.5, 1121.6, 1108.8, 1096.0, 1106.6, 1097.1, 1109.1, 1111.6]
    )
    * 0.3048
)
# Free stream air density (kg/m^3)
rhodata = (
    515.37882
    * np.array([2.303, 1.407, 1.066, 0.867, 0.632, 0.543, 0.476, 0.404, 0.374, 0.385])
    * 1e-3
)
# Mass ratio Mh./(pi*rhodata*b*c0^2/4)
mubardata = np.array(
    [696.0, 1139.0, 1503.0, 1848.0, 2535.0, 2951.0, 3366.0, 3966.0, 4284.0, 4162.0]
)
# Flutter speed (m/s)
Uflutdata = (
    np.array([338.2, 441.6, 508.3, 572.0, 676.4, 734.3, 785.7, 844.8, 887.3, 911.5])
    * 0.3048
)
# Flutter frequency (rad/s)
freqflutdata = (
    np.array([4.56, 4.51, 4.47, 4.43, 4.34, 4.28, 4.25, 4.13, 4.09, 4.07]) * 2.0 * np.pi
)
# Frequency of first torsion mode from experiment
omega_alpha = 5.20 * 2.0 * np.pi
# Nondimensional flutter speed Uflutdata./(c0/2*34.2*sqrt(mubardata)).
# Different values in different sources and they both do not agree with the definition of Ustar
# Ustardata=[0.538 0.549 0.550 0.558 0.564 0.567 0.568 0.563 0.567 0.593]; According to Rivera
# Ustardata=[0.563 0.574 0.575 0.584 0.590 0.593 0.594 0.589 0.595 0.620]; According to Bennett
# Recalculate experimental Ustar values
Ustardata = np.divide(Uflutdata, cref / 2.0 * omega_alpha * np.sqrt(mubardata))
# Flutter frequency ratio freqflutdata/wn(2)
freqratdata = np.array(
    [0.877, 0.867, 0.860, 0.852, 0.835, 0.823, 0.817, 0.794, 0.787, 0.783]
)
# Flutter dynamic pressure data (N/m^2)
dynpressdata = (
    np.array([131.7, 137.2, 137.7, 141.9, 144.6, 146.5, 146.9, 144.2, 147.2, 159.9])
    * 4.44822
    / 0.3048**2
)
# Static pressure calculated from speed of sound and density
pressdata = asounddata**2.0 * rhodata / 1.4
# Reduced frequency
kflutdata = np.array(
    [0.0565, 0.0428, 0.0368, 0.0324, 0.0269, 0.0244, 0.0227, 0.0205, 0.0193, 0.0187]
)
# Total number of runs
nruns = len(Machdata)
# Structural dynamic properties measured from experiment
mass = 6.01 * 14.5939  # Mass of wing in kg
Ialpha = 2.78 * 14.5939 * 0.3048**2  # Moment of inertia around pitch axis in kg*m^2
fn = np.array([3.36, 5.20])  # Natural frequencies in plunge and pitch in Hz
wn = 2 * np.pi * fn  #  Natural frequencies in plunge and pitch in rad/s
zeta0 = np.array([0.00, 0.00])  # Damping ratios in plunge and pitch
Kh = 2659 * 4.44822 / 0.3048
# Plunge stiffness in N/m
Kalpha = 2897 * 0.3048 * 4.44822
# Pitch stiffness in Nm/rad

# Select reduced frequency values
kvec = np.array([0.001, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.1])

# Select airspeed range in m/s
Uv = np.linspace(50, 320, num=101)

# Choose order of pressure coefficient equation
cp_order = 2  # 1 for linear and 2 for second order

# Set values of mean (or steady) angle of sideslip
beta0 = 0.0 * np.pi / 180.0  # Angle of sideslip in rad

# Number of bodies
nbody = 1
# Initialize body struct array
body = np.zeros(nbody, dtype=tp_body)

# Input first body
ibody = 0  # Index of body
name = "wing"  # Name of body
# Choose numbers of panels for this wing and its wake
nhalf = 10  # Number of spanwise panels per half-wing.
m = 20  # Number of chordwise panels
nchords = 10  # Set length of wake in chord lengths
# Calculate number of chordwise wake rings
mw = m * nchords
# Number of trapezoidal sections
ntrap = 1
# Initialize trapezoidal section struct array
trap = np.zeros(ntrap, dtype=tp_trap)

# Input wing geometry
bhalf = 32 * 0.0254  # Span in m of half-wing
c0 = 16 * 0.0254  # Root chord in m
lamda = 1.0  # Taper ratio
LamdaLE = 0.0 * np.pi / 180.0
# Sweep at leading edge
roottwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
tiptwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
dihedral = 0.0 * np.pi / 180.0  # Dihedral angle in rad
twistcent = 0.0  # Chordwise axis around which twist is defined
# Chordwise distance of root leading edge from previous
# trapezoidal section's tip leading edge
xledist = 0.0
# Coordinates of points through which pitch axis passes
xf0 = c0 / 2.0
yf0 = 0.0
zf0 = 0.0
# Set airfoil name (must be the filename of a function in the Common directory)
airfoil = "nacafourdigit"
# Set airfoil parameters
mpt = 12  # NACA 0012, ignore the leading zeros
teclosed = 0  # 1 for closed trailing edge, 0 otherwise
# Assemble airfoil parameter values
airfoil_params = np.array([mpt, teclosed])

# Calculate panel aspect ratio
panelAR = (c0 / m) / (bhalf / nhalf)
if panelAR < 0.1:
    sys.exit("Panel aspect ratio too low. Increase n or decrease m.")

# Arrange all data into trapezoidal sections
trap[0] = np.array(
    [
        (
            c0,
            xledist,
            bhalf,
            lamda,
            LamdaLE,
            roottwist,
            tiptwist,
            twistcent,
            dihedral,
            airfoil,
            airfoil_params,
            airfoil,
            airfoil_params,
        )
    ],
    dtype=tp_trap,
)

# Minimum number of spanwise panels per trapezoidal section
nmin = 3
# Chordwise panel distribution: 1 constant, 2 denser at the leading edge
linchord = 0
# Spanwise panel distribution: 1 constant, 2 denser at the wing tip(s)
linspan = 0
# Define root leading edge
lexyz = np.array([0, 0, 0])
# Define roll, pitch and yaw angles
rollpitchyaw = np.array([0, 0, 0]) * np.pi / 180
# Define roll, pitch and yaw centre (x,y,z position of rotation centre)
rollpitchyaw_cent = np.array([0, 0, 0])
mirroredwing = 2  # If mirroredwing=-1: a left half-wing will be created
# If mirroredwing=1: a right half-wing will be created
# If mirroredwing=2: two mirrored half-wings will be created.
# dir_tau is the direction in which the unit tangent vector  for this wing
# (tauxx, tauxy, tauxz) has a zero component
dir_tau = 2
# Calculate vertices of wing panels
body = SDPMgeometry_trap_fun(
    body,
    ibody,
    m,
    mw,
    nhalf,
    mirroredwing,
    linchord,
    linspan,
    trap,
    name,
    dir_tau,
    rollpitchyaw,
    rollpitchyaw_cent,
    lexyz,
    nmin,
)

# The pitch-plunge wing has two degrees of freedom and therefore two modes of
# vibration
nmodes = 2
# Parameter to determine if the structural model concerns a half wing or a
# full wing.
halfwing = 1  # halfwing=1: half-wing. halfwing=0: full wing

# Plot all bodies
fig, axx = plt.subplots(subplot_kw={"projection": "3d"})
for i in range(0, len(body)):
    axx.plot_surface(body["Xp0"][i], body["Yp0"][i], body["Zp0"][i])
# End for
axx.set_proj_type("ortho")  # FOV = 0 deg
axx.axis("equal")
axx.set_xlabel("$x$", labelpad=10)
axx.set_ylabel("$y$", labelpad=10)
axx.set_zlabel("$z$", labelpad=-2)
axx.view_init(26, -120)
plt.show()

# Assemble the indices of the body panels, spanwise body panels, wake
# panels etc. for all bodies.
allbodies = SDPMcalcs.allbodyindex(body)

# Calculate structural matrices
A = np.matrix([[mass, 0.0], [0.0, Ialpha]])  # Structural mass matrix
E = np.matrix([[Kh, 0.0], [0.0, Kalpha]])  # Structural stiffness matrix
C = np.matrix(
    [[2 * mass * wn[0] * zeta0[0], 0.0], [0.0, 2 * Ialpha * wn[1] * zeta0[1]]]
)  # Structural damping matrix

# Initialize results arrays for all runs
Ustarvec = np.zeros((nruns))  # Flutter speed index
Uflutvec = np.zeros((nruns))  # Flutter speed in m/s
dynpressvec = np.zeros((nruns))  # Flutter dynamic pressure in Pa
freqflutvec = np.zeros((nruns))  # Flutter frequency in rad/s
kflutvec = np.zeros((nruns))  # Reduced flutter frequency

print("Calculating flutter solutions for all experimental test cases")
for irun in range(0, nruns):
    print("")
    print("Simulating run " + str(irun + 1))

    # Set Mach number of current run
    Mach = Machdata[irun]
    # Set mass ratio of current run
    mubar = mubardata[irun]
    # Set density of current run
    rho = rhodata[irun]
    # Calculate subsonic compressibility factor
    beta = np.sqrt(1 - Mach**2)
    # Set mean angle of attack
    alpha0 = alpha0data[irun]

    # Calculate steady aerodynamic pressures and loads
    body, allbodies, Aphi, Bphi, Cphi, barUinf, barVinf, barWinf = (
        SDPMcalcs.steadysolve(
            body,
            allbodies,
            cp_order,
            Mach,
            beta,
            alpha0,
            beta0,
            xf0,
            yf0,
            zf0,
            install_dir,
        )
    )

    # Calculate flutter solution for pitch-plunge motion
    Uflut, freqflut, kflut, dynpressflut, omega, zeta = flutsol.flutsolve_pitchplunge(
        body,
        allbodies,
        kvec,
        Uv,
        nmodes,
        Aphi,
        Bphi,
        Cphi,
        barUinf,
        barVinf,
        barWinf,
        c0,
        Mach,
        beta,
        cp_order,
        A,
        C,
        E,
        rho,
        wn,
        halfwing,
        xf0,
        yf0,
        zf0,
        install_dir,
    )

    # Print out flutter solution
    if Uflut != 0:  # If there is a flutter point
        # Store flutter data for this run
        Uflutvec[irun] = Uflut
        # Calculate flutter speed index
        Ustarvec[irun] = Uflut / (c0 / 2.0 * omega_alpha * np.sqrt(mubar))
        dynpressvec[irun] = dynpressflut
        freqflutvec[irun] = freqflut
        kflutvec[irun] = kflut
        # Compare to experimental data
        print("Flutter speed (m/s)")
        print("SDPM      Exp.")
        print(np.array([Uflut, Uflutdata[irun]]))
        print("Flutter frequency (rad/s)")
        print("SDPM      Exp.")
        print(np.array([freqflut, freqflutdata[irun]]))
    else:
        print("Could not find a flutter point for run " + str(irun))
    # End if
# End loop for irun

# Plot flutter airspeed
fig, axx = plt.subplots()
axx.plot(Machdata, Uflutvec, label="SDPM")
axx.plot(
    Machdata,
    Uflutdata,
    "o",
    label="Exp.",
)
axx.set_xlabel("$M_{\\infty}$")
axx.set_ylabel("$U_F$ (m/s)")
axx.grid()
axx.legend(loc="upper left")

# Plot flutter frequency
fig, axx = plt.subplots()
axx.plot(Machdata, freqflutvec, label="SDPM")
axx.plot(
    Machdata,
    freqflutdata,
    "o",
    label="Exp.",
)
axx.set_xlabel("$M_{\\infty}$")
axx.set_ylabel("$\\omega_F$ (rad/s)")
axx.grid()
axx.legend(loc="upper right")

# Plot flutter speed index
fig, axx = plt.subplots()
axx.plot(Machdata, Ustarvec, label="SDPM")
axx.plot(
    Machdata,
    Ustardata,
    "o",
    label="Exp.",
)
axx.set_xlabel("$M_{\\infty}$")
axx.set_ylabel("$U^*_F$")
axx.grid()
axx.legend(loc="upper left")

# Plot flutter frequency ratio
fig, axx = plt.subplots()
axx.plot(Machdata, freqflutvec / wn[1], label="SDPM")
axx.plot(
    Machdata,
    freqratdata,
    "o",
    label="Exp.",
)
axx.set_xlabel("$M_{\\infty}$")
axx.set_ylabel("$\\omega_F/\\omega_{a}$")
axx.grid()
axx.legend(loc="upper right")

# Plot flutter dynamic pressure
fig, axx = plt.subplots()
axx.plot(Machdata, dynpressvec, label="SDPM")
axx.plot(
    Machdata,
    dynpressdata,
    "o",
    label="Exp.",
)
axx.set_xlabel("$M_{\\infty}$")
axx.set_ylabel("Dynamic pressure (Pa)")
axx.grid()
axx.legend(loc="upper left")

# Plot flutter reduced frequency
fig, axx = plt.subplots()
axx.plot(Machdata, kflutvec, label="SDPM")
axx.plot(
    Machdata,
    kflutdata,
    "o",
    label="Exp.",
)
axx.set_xlabel("$M_{\\infty}$")
axx.set_ylabel("$k$")
axx.grid()
axx.legend(loc="upper right")

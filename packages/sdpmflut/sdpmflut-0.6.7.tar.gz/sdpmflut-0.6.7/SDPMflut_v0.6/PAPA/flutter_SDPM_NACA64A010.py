#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program flutter_SDPM_NACA0012 calculates the flutter boundary of a
NACA64A010 rectangular wing with pitch and plunge degrees of freedom.

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

# Run data from wind tunnel flutter tests in R-12 gas. Source:
# Test Cases for Flutter of the Benchmark Models Rectangular Wings on the Pitch
# and Plunge Apparatus. Robert M. Bennett. Defense Technical Information Center
# Compilation Part Notice ADPO10713.
# Chordwise reference length in m
cref = 16 * 0.0254
# Free stream Mach number
Machdata = np.array(
    [
        0.543,
        0.588,
        0.630,
        0.674,
        0.691,
        0.728,
        0.731,
        0.742,
        0.750,
        0.781,
        0.781,
        0.799,
        0.801,
        0.816,
        0.856,
        0.861,
        0.937,
        0.947,
    ]
)
# Mean pitch angle
alpha0data = (
    np.array(
        [
            0.48,
            0.48,
            0.48,
            0.48,
            0.48,
            0.43,
            0.48,
            0.48,
            0.48,
            0.47,
            0.43,
            0.40,
            0.42,
            0.46,
            0.45,
            0.42,
            0,
            -0.1,
        ]
    )
    * np.pi
    / 180.0
)
# Speed of sound data
asounddata = (
    np.array(
        [
            500.9,
            500.9,
            500.6,
            500.6,
            499.7,
            503.4,
            502.1,
            501.6,
            500.5,
            500.8,
            503.3,
            501.3,
            503.7,
            500.5,
            504.3,
            502.8,
            502.5,
            502.7,
        ]
    )
    * 0.3048
)
# Free stream air density (kg/m^3)
rhodata = (
    515.37882
    * np.array(
        [
            4.020,
            3.446,
            3.033,
            2.685,
            2.554,
            2.352,
            2.359,
            2.255,
            2.182,
            2.082,
            2.069,
            1.993,
            1.956,
            1.914,
            1.873,
            1.887,
            1.613,
            1.523,
        ]
    )
    * 1e-3
)
# Mass ratio Mh./(pi*rhodata*b*c0^2/4)
mubardata = (
    np.array(
        [
            405,
            472,
            537,
            606,
            637,
            692,
            690,
            722,
            746,
            782,
            787,
            817,
            832,
            851,
            869,
            863,
            1009,
            1069,
        ]
    )
    * 1.0
)
# Flutter speed (m/s)
Uflutdata = (
    np.array(
        [
            272,
            294.5,
            315.4,
            337.4,
            345.3,
            366.5,
            367.0,
            372.2,
            375.4,
            391.1,
            393.1,
            400.5,
            403.5,
            408.4,
            431.7,
            432.9,
            470.8,
            476.1,
        ]
    )
    * 0.3048
)
# Flutter frequency (rad/s)
freqflutdata = (
    np.array(
        [
            4.462,
            4.440,
            4.407,
            4.370,
            4.365,
            4.300,
            4.286,
            4.290,
            4.296,
            4.218,
            4.228,
            4.192,
            4.200,
            4.162,
            4.070,
            4.090,
            3.592,
            3.600,
        ]
    )
    * 2.0
    * np.pi
)
# Frequency of first torsion mode from experiment
omega_alpha = 5.20 * 2.0 * np.pi
# Nondimensional flutter speed Uflutdata./(c0/2*34.2*sqrt(mubardata)). I
Ustardata = np.array(
    [
        0.619,
        0.621,
        0.624,
        0.628,
        0.627,
        0.638,
        0.640,
        0.635,
        0.641,
        0.642,
        0.642,
        0.642,
        0.641,
        0.642,
        0.671,
        0.675,
        0.679,
        0.667,
    ]
)
# Flutter frequency ratio freqflutdata/omega_alpha
freqratdata = np.array(
    [
        0.856,
        0.852,
        0.846,
        0.839,
        0.838,
        0.825,
        0.823,
        0.823,
        0.825,
        0.810,
        0.812,
        0.805,
        0.806,
        0.799,
        0.781,
        0.785,
        0.689,
        0.691,
    ]
)
# Flutter dynamic pressure data (N/m^2)
dynpressdata = (
    np.array(
        [
            148.7,
            149.4,
            150.8,
            152.8,
            152.3,
            158.0,
            158.8,
            156.1,
            153.7,
            159.2,
            159.8,
            159.8,
            159.2,
            159.6,
            174.5,
            176.8,
            178.7,
            172.5,
        ]
    )
    * 4.44822
    / 0.3048**2
)
# Static pressure calculated from speed of sound and density
pressdata = asounddata**2.0 * rhodata / 1.4
# Reduced frequency
kflutdata = np.array(
    [
        0.069,
        0.063,
        0.059,
        0.054,
        0.053,
        0.049,
        0.049,
        0.048,
        0.048,
        0.045,
        0.045,
        0.044,
        0.044,
        0.043,
        0.040,
        0.040,
        0.032,
        0.032,
    ]
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
# Number of structural modes
nmodes = 2

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
airfoil = "NACA64A010"
# Set airfoil parameters
teclosed = 0  # 1 for closed trailing edge, 0 otherwise
# Assemble airfoil parameter values
airfoil_params = np.array([teclosed, 0.0])

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
# Input body description
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

fig, axx = plt.subplots(subplot_kw={"projection": "3d"})
axx.plot_surface(body["Xp0"][0], body["Yp0"][0], body["Zp0"][0])
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

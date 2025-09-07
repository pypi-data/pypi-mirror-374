#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program flutter_SDPM_AGARD calculates the flutter boundary of the
AGARD 445.6 weakened wing using the new SDPMflut package structure.

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

# Import libraries and packages
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add the source directory to Python path to import the new package
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.join(project_root, "src")
sys.path.insert(0, src_path)

# Import from new package structure
from sdpmflut.core.SDPMgeometry import SDPMgeometry_trap_fun
from sdpmflut.core import flutsol
from sdpmflut.core import FEmodes
from sdpmflut.core import SDPMcalcs

# Acquire SDPMflut trap and body data types
tp_trap, tp_body, _ = SDPMcalcs.SDPMdtypes()

# Run data from wind tunnel flutter tests of wing 3 (weakened). Source:
# AGARD Standard Aeroelastic Configurations for Dynamic Response I -Wing 445.6.
# E.Carson Yates, Jr, AGARD REPORT No.765, 1985
# Free stream Mach number
Machdata = np.array([0.499, 0.678, 0.901, 0.954, 0.957, 0.960])
# Free stream air density (kg/m^3)
rhodata = 515.37882 * np.array([0.830, 0.404, 0.193, 0.123, 0.123, 0.123]) * 1e-3
# Mass ratio Mh./(pi*rhodata*b*c0^2/4)
mubardata = np.array([33.465, 68.753, 143.920, 225.820, 225.820, 225.820])
# Flutter speed (m/s)
Uflutdata = np.array([565.8, 759.1, 973.4, 1008.4, 1013.8, 1020.2]) * 0.3048
# Nondimensional flutter speed
Ustardata = np.array([0.4459, 0.4174, 0.3700, 0.3059, 0.3076, 0.3095])
# Flutter frequency (rad/s)
freqflutdata = np.array([128.1, 113.0, 101.1, 91.1, 87.3, 87.9])
# Frequency of first torsion mode from experiment
omega_alpha = 239.3
# Calculate flutter ratio
freqflutratio = freqflutdata / omega_alpha
# Total number of runs
nruns = Machdata.size

# Select reduced frequency values
kvec = np.array([0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 2.2])

# Select airspeed range in m/s
Uv = np.linspace(100, 400, num=101)

# Choose order of pressure coefficient equation
cp_order = 2  # 1 for linear and 2 for second order

# Set values of mean (or steady) angles of attack and sideslip
alpha0 = 0.0 * np.pi / 180.0  # Angle of attack in rad
beta0 = 0.0 * np.pi / 180.0  # Angle of sideslip in rad

# Set number of bodies
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
# Set number of trapezoidal sections for this wing
ntrap = 1
# Initialize trapezoidal section struct array
trap = np.zeros(ntrap, dtype=tp_trap)

# Input wing geometry
bhalf = 2.5 * 0.3048  # Span in m of half-wing
c0 = 1.833 * 0.3048  # Root chord in m
lamda = 1.208 / 1.833  # Taper ratio
Lamdac4 = 45.0 * np.pi / 180.0
# Sweep at quarter chord in rad
# Calculate the sweep angle at the leading edge
LamdaLE = np.arctan((1 - lamda) * c0 / 4.0 / bhalf + np.tan(Lamdac4))
roottwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
tiptwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
twistcent = 0.0  # Chordwise axis around which twist is defined
dihedral = 0.0 * np.pi / 180.0  # Dihedral angle in rad
# Chordwise distance of root leading edge from previous
# trapezoidal section's tip leading edge
xledist = 0.0
# Set airfoil name (must be the filename of a function in the src/sdpmflut/core directory)
airfoil = "NACA65A004"
# Set airfoil parameters
dataset = 2  # There are two data sets in function NACA65A004, select 1 for
# points in NACA TN 3047, 2 for points in AGARD Report No. 765
# Assemble airfoil parameter values
airfoil_params = np.array([dataset, 0.0])
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

# Calculate panel aspect ratio
panelAR = (c0 / m) / (bhalf / nhalf)
if panelAR < 0.1:
    sys.exit("Panel aspect ratio too low. Increase n or decrease m.")

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

# File name of Matlab mat file that contains the structural model
fname = "modes_AGARD_Q4EPM.mat"
# Choose number of modes to include in the flutter calculation
nmodes = 5  # Cannot exceed number of modes in FE model
zeta0 = 0.02 * np.ones(nmodes)  # Structural damping ratios
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

# Acquire structural matrices and mode shapes
(
    A,
    C,
    E,
    wn,
    xxplot,
    yyplot,
    zzplot,
    modeshapesx,
    modeshapesy,
    modeshapesz,
    modeshapesRx,
    modeshapesRy,
    modeshapesRz,
) = FEmodes.FE_matrices(fname, zeta0, nmodes)

# Interpolate mode shapes onto panel control points
body = FEmodes.SDPMmodeinterp(
    xxplot,
    yyplot,
    modeshapesx,
    modeshapesy,
    modeshapesz,
    modeshapesRx,
    modeshapesRy,
    modeshapesRz,
    body,
)

# Assemble mode shapes for all bodies into global matrices
allbodies = SDPMcalcs.modeshape_assemble(body, allbodies, nmodes)

# Get path to the kernels directory for the new package structure
kernels_dir = os.path.join(src_path, "sdpmflut", "kernels")

# Initialize results arrays for all runs
Ustarvec = np.zeros((nruns))  # Flutter speed index
Uflutvec = np.zeros((nruns))  # Flutter speed in m/s
dynpressvec = np.zeros((nruns))  # Flutter dynamic pressure in Pa
freqflutvec = np.zeros((nruns))  # Flutter frequency in rad/s
kflutvec = np.zeros((nruns))  # Reduced flutter frequency

print(
    "Calculating flutter solutions for all experimental test cases using new package structure"
)
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
            0.0,
            0.0,
            0.0,
        )
    )

    Uflut, freqflut, kflut, dynpressflut, omega, zeta = flutsol.flutsolve_flex(
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
        print("NEW SDPM  Exp.")
        print(np.array([Uflut, Uflutdata[irun]]))
        print("Flutter frequency (rad/s)")
        print("NEW SDPM  Exp.")
        print(np.array([freqflut, freqflutdata[irun]]))
    else:
        print("Could not find a flutter point for run " + str(irun))
    # End if
# End loop for irun

# Plot flutter airspeed
fig, axx = plt.subplots()
axx.plot(Machdata, Uflutvec, label="NEW SDPM")
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
axx.plot(Machdata, freqflutvec, label="NEW SDPM")
axx.plot(
    Machdata,
    freqflutdata,
    "o",
    label="Exp.",
)
axx.set_xlabel("$M_{\\infty}$")
axx.set_ylabel(r"$\omega_F$ (rad/s)")
axx.grid()
axx.legend(loc="upper right")

# Plot flutter speed index
fig, axx = plt.subplots()
axx.plot(Machdata, Ustarvec, label="NEW SDPM")
axx.plot(
    Machdata,
    Ustardata,
    "o",
    label="Exp.",
)
axx.set_xlabel("$M_{\\infty}$")
axx.set_ylabel("$U^*_F$")
axx.grid()
axx.legend(loc="upper right")

# Plot flutter frequency ratio
fig, axx = plt.subplots()
axx.plot(Machdata, freqflutvec / omega_alpha, label="NEW SDPM")
axx.plot(
    Machdata,
    freqflutratio,
    "o",
    label="Exp.",
)
axx.set_xlabel("$M_{\\infty}$")
axx.set_ylabel(r"$\omega_F/\omega_{a}$")
axx.grid()
axx.legend(loc="upper right")

# Save results for comparison
print("\n" + "=" * 60)
print("RESULTS SUMMARY - NEW PACKAGE")
print("=" * 60)
print("Run | Mach | SDPM U_F (m/s) | Exp U_F (m/s) | SDPM ω_F | Exp ω_F")
print("-" * 60)
for i in range(nruns):
    if Uflutvec[i] != 0:
        print(
            f"{i+1:3d} | {Machdata[i]:.3f} | {Uflutvec[i]:12.2f} | {Uflutdata[i]:11.2f} | {freqflutvec[i]:8.1f} | {freqflutdata[i]:7.1f}"
        )
    else:
        print(
            f"{i+1:3d} | {Machdata[i]:.3f} | {'No solution':>12} | {Uflutdata[i]:11.2f} | {'N/A':>8} | {freqflutdata[i]:7.1f}"
        )

plt.show()

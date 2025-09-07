#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program steady_SDPM_NASATM84367 calculates the steady pressure
distributions around the steady swept wing tested by Lockman and Lee
Seegmiller in NASA TM 84367.

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
import scipy.io
import sys

sys.path.append(install_dir)
from SDPMgeometry import SDPMgeometry_trap_fun
import SDPMcalcs

# Create SDPM data types
tp_trap, tp_body, _ = SDPMcalcs.SDPMdtypes()

# Run data from wind tunnel tests of wing. Source:
# An experimental investigation of the subcritical and supercritical flow
# about a swept semispan wing, W. K. Lockman and H. Lee Seegmiller, NASA TM
# 84367, 1983.
# Free stream Mach number
Machdata = np.array(
    [0.501, 0.499, 0.601, 0.601, 0.695, 0.695, 0.794, 0.793]
)  # The last two test cases are highly transonic
# Mean angle of attack in degrees
alpha0data = np.array([0.0, 2.0, -2.0, 2.0, -2.0, 2.0, 2.0, -2.0]) * np.pi / 180.0
# Total number of runs
nruns = Machdata.size
# Load experimental pressure data from .mat file
mat = scipy.io.loadmat("dataNASATM84367.mat")

# Choose order of pressure coefficient equation
cp_order = 2  # 1 for linear and 2 for second order

# Set value of mean (or steady) angle of sideslip
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
# Set number of trapezoidal sections for this wing
ntrap = 1
# Initialize trapezoidal section struct array
trap = np.zeros(ntrap, dtype=tp_trap)

# Input wing geometry
bhalf = 0.1524  # Span in m of half-wing
c0 = 0.1016  # Root chord in m
lamda = 1.0  # Taper ratio
LamdaLE = 20.0 * np.pi / 180.0
# Sweep at leading edge in rad
roottwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
tiptwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
dihedral = 0.0 * np.pi / 180.0  # Dihedral angle in rad
twistcent = 0.0  # Chordwise axis around which twist is defined
# Chordwise distance of root leading edge from previous
# trapezoidal section's tip leading edge
xledist = 0.0
# Set airfoil name (must be the filename of a function in the Common directory)
airfoil = "nacafourdigit"
# Set airfoil parameters
mpt = 12  # NACA 0012, ignore the leading zeros
teclosed = 1  # 1 for closed trailing edge, 0 otherwise
# Assemble airfoil parameter values
airfoil_params = np.array([mpt, teclosed])
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

# Plot all bodies
fig, axx = plt.subplots(subplot_kw={"projection": "3d"})
for i in range(0, len(body)):
    axx.plot_surface(body["Xp0"][i], body["Yp0"][i], body["Zp0"][i])
# End for
axx.set_proj_type("ortho")  # FOV = 0 deg
axx.axis("equal")
axx.set_xlabel("$x$", labelpad=10)
axx.set_ylabel("$y$", labelpad=10)
axx.set_zlabel("$z$", labelpad=-1)
axx.view_init(26, -120)
plt.show()

# Assemble the indices of the body panels, spanwise body panels, wake
# panels etc. for all bodies.
allbodies = SDPMcalcs.allbodyindex(body)

print("Calculating flutter solutions for all experimental test cases")
for irun in range(0, nruns):
    print("Simulating run " + str(irun + 1))

    # Set Mach number of current run
    Mach = Machdata[irun]
    # Set mean angle of attack
    alpha0 = alpha0data[irun]
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
            install_dir,
        )
    )

    fig, axx = plt.subplots(subplot_kw={"projection": "3d"})
    # Plot SDPM pressure predictions
    axx.plot_surface(
        body["Xc0"][0][:, body["n"][0] // 2 : body["n"][0]],
        body["Yc0"][0][:, body["n"][0] // 2 : body["n"][0]],
        body["cp0"][0][:, body["n"][0] // 2 : body["n"][0]],
        edgecolor="royalblue",
        alpha=0.1,
    )
    # Plot experimental pressure measurements
    axx.scatter(
        mat["x0data"], mat["y0data"], mat["cp0data"][:, irun], marker="o", color="r"
    )
    axx.set_proj_type("ortho")  # FOV = 0 deg
    axx.set_zlim(-1, 0.6)
    axx.set_xlabel("$x/c_0$", labelpad=10)
    axx.set_ylabel("$2y/b$", labelpad=10)
    axx.set_zlabel("$c_p(0)$", labelpad=-1)
    axx.view_init(26, -120)
    plt.title(
        "$M_{\\infty}=$"
        + str(Mach)
        + ", $\\alpha_0$="
        + str(alpha0 * 180 / np.pi)
        + "$^o$"
    )
    plt.show()
# End for

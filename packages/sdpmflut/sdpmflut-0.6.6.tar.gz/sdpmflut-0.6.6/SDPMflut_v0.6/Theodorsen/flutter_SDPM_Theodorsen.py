#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program flutter_SDPM_NACA0012 calculates the flutter boundary of a flat
% plate rectangular wing with pitch and plunge degrees of freedom and
% compares it to Theodorsen theory.

This code is part of the SDPMflut Python distribution.
Copyright (C) 2025 Grigorios Dimitriadis

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
from scipy import linalg
import scipy.special
from SDPMgeometry import SDPMgeometry_trap_fun
import flutsol
import SDPMcalcs

# Create SDPM data types
tp_trap, tp_body, _ = SDPMcalcs.SDPMdtypes()

# Set flight conditions
# Free stream Mach number
Mach = 0.01
# Calculate subsonic compressibility factor
beta = np.sqrt(1 - Mach**2)
# Mean pitch angle
alpha0 = 0.0
# Mean angle of sideslip
beta0 = 0.0
# Free stream air density (kg/m^3)
rho = 1.225
# Total number of runs
nruns = 1

# Select reduced frequency values
kvec = np.array([0.001, 0.01, 0.02, 0.04, 0.06, 0.1, 0.2, 0.4, 0.6, 1.0, 1.4])

# Select airspeed range in m/s
Uv = np.linspace(5, 55, num=101)

# Choose order of pressure coefficient equation
cp_order = 1  # 1 for linear and 2 for second order

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
bhalf = 25  # Span in m of half-wing
c0 = 0.25  # Root chord in m
lamda = 1.0  # Taper ratio
LamdaLE = 0.0 * np.pi / 180.0
# Sweep at leading edge
roottwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
tiptwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
twistcent = 0.0  # Chordwise axis around which twist is defined
dihedral = 0.0 * np.pi / 180.0  # Dihedral angle in rad
# Chordwise distance of root leading edge from previous
# trapezoidal section's tip leading edge
xledist = 0.0
# Coordinates of points through which pitch axis passes
xf0 = 0.4 * c0
yf0 = 0.0
zf0 = 0.0
# Set airfoil name (must be the filename of a function in the Common directory)
airfoil = "flatplate"
# Set airfoil parameters
# Half-thickness of flat plate airfoil
athick = 0.001 / 2.0
# Chordwise length of bevel
bchord = c0 / 5.0
# Assemble airfoil parameter values
airfoil_params = np.array([athick, bchord])

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
halfwing = 0  # halfwing=1: half-wing. halfwing=0: full wing

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

# Structural model parameters
rhometal = 2700.0  # Density of aluminium
b = c0 / 2.0  # Half-chord
thick = 0.02  # Structural thickness (not related to aerodynamic thickness)
xc = 0.5 * c0  # Chordwise position of centre of mass
mass = rhometal * c0 * thick  # Total mass of wing
e = (
    xf0 - c0 / 4.0
) / c0  # Non-dimensional distance between aerodynamic centre and pitch axis
S = mass * (xc - xf0)  # Static imbalance
Ialpha = (
    mass / 3.0 * (c0**2.0 - 3.0 * c0 * xf0 + 3.0 * xf0**2.0)
)  # Second moment of mass around pitch axis axis
Kalpha = (2.0 * np.pi * 8.0) ** 2.0 * Ialpha  # Pitch stiffness
Kh = (2.0 * np.pi * 2.0) ** 2.0 * mass  # Plunge stiffness
a = (xf0 - b) / b  # Theodorsen's non-dimensional measure of position of pitch axis

# Calculate structural matrices
A = np.matrix([[mass, S], [S, Ialpha]])  # Structural mass matrix
E = np.matrix([[Kh, 0.0], [0.0, Kalpha]])  # Structural stiffness matrix
C = np.zeros((2, 2))  # Structural damping matrix
eigvals0, _ = linalg.eig(linalg.solve(A, E))
wn = np.sqrt(eigvals0)  # Wind off natural frequencies
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
        A * 2.0 * bhalf,
        C * 2.0 * bhalf,
        E * 2.0 * bhalf,
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
        dynpressvec[irun] = dynpressflut
        freqflutvec[irun] = freqflut
        kflutvec[irun] = kflut
        # Compare to experimental data
        print("Flutter speed (m/s)")
        print("SDPM")
        print(Uflut)
        print("Flutter frequency (rad/s)")
        print("SDPM")
        print(freqflut)
    else:
        print("Could not find a flutter point for run " + str(irun))
    # End if

    # Calculate Theodorsen flutter solution
    # Initialize array for Theodorsen's unsteady generalized aerodynamic load matrix
    Qtheo = np.zeros((kvec.size, nmodes, nmodes), dtype=complex)
    for ik in range(0, kvec.size):
        k = kvec[ik]
        # Calculate Theodorsen's function at this value of k
        Ctheo = (-scipy.special.j1(k) + 1j * scipy.special.y1(k)) / (
            -(scipy.special.j1(k) + scipy.special.y0(k))
            + 1j * (scipy.special.y1(k) - scipy.special.j0(k))
        )
        # Calculate Theodorsen's generalized aerodynamic load matrix
        Q11 = -4.0 * np.pi * Ctheo * 1j * k + 2 * np.pi * k**2.0
        Q12 = (
            -2.0 * np.pi * c0 * Ctheo
            - 2.0 * np.pi * b * 1j * k
            - 4.0 * np.pi * Ctheo * (3.0 / 4.0 * c0 - xf0) * 1j * k
            - 2.0 * np.pi * a * b * k**2.0
        )
        Q21 = (
            4.0 * np.pi * e * c0 * Ctheo * 1j * k
            - 2.0 * np.pi * (xf0 - c0 / 2.0) * k**2.0
        )
        Q22 = (
            2.0 * np.pi * e * c0**2 * Ctheo
            - 2.0 * (3.0 / 4.0 * c0 - xf0) * np.pi * b * 1j * k
            + 4.0 * np.pi * e * c0 * Ctheo * (3.0 / 4.0 * c0 - xf0) * 1j * k
            + 2.0 * np.pi * (xf0 - c0 / 2.0) ** 2.0 * k**2
            + np.pi * b**2.0 / 4.0 * k**2.0
        )
        Qtheo[ik, :, :] = np.array([(Q11, Q12), (Q21, Q22)])
    # End for
    # Calculate Theodorsen eigenvalues using modified p-k method
    eigvals_Theo = flutsol.pkmethod(A, C, E, Qtheo, kvec, Uv, c0 / 2.0, rho, wn)
    # Calculate natural frequencies and damping ratios
    omega_Theo = np.absolute(eigvals_Theo)
    zeta_Theo = -eigvals_Theo.real / np.absolute(eigvals_Theo)

# End loop for irun

# Plot flutter airspeed
fig, axx = plt.subplots()
axx.plot(Uv, omega[0, :], "b-", label="SDPM")
axx.plot(Uv, omega[1, :], "b-", label="SDPM")
axx.plot(Uv, omega_Theo[0, :], "r--", label="Theodorsen")
axx.plot(Uv, omega_Theo[1, :], "r--", label="Theodorsen")
axx.set_xlabel("Q_{\\infty}$")
axx.set_ylabel("$\\omega_n$ (rad/s)")
axx.grid()
axx.legend(loc="upper left")

# Plot flutter frequency
fig, axx = plt.subplots()
axx.plot(Uv, zeta[0, :], "b-", label="SDPM")
axx.plot(Uv, zeta[1, :], "b-", label="SDPM")
axx.plot(Uv, zeta_Theo[0, :], "r--", label="Theodorsen")
axx.plot(Uv, zeta_Theo[1, :], "r--", label="Theodorsen")
axx.set_xlabel("Q_{\\infty}$")
axx.set_ylabel("$\\zeta$")
axx.grid()
axx.legend(loc="upper left")

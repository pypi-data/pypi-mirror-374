#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program flutter_SDPM_NASATMAX72799 calculates the flutter boundary of the
wing with and without winglets described in NASA TMX 72799.

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
import FEmodes
import SDPMcalcs

# Create SDPM data types
tp_trap, tp_body, _ = SDPMcalcs.SDPMdtypes()

# Winglet choice
winglet = 3  # 1: No winglet
# 2: Light winglet
# 3: Heavy winglet

# Run data from wind tunnel flutter tests of wing without winglets. Source:
# A preliminary study of the effects of vortex diffusers (winglets) on
# wing flutter), R. V. Doggett, Jr and M. G. Farmer, NASA TMX 72799, 1975
if winglet == 1:
    # Measured wind-off natural frequencies
    omega_mes = np.array([5.8, 26.4, 51.4, 66.9]) * 2.0 * np.pi  # In rad/s
    # Measured wing mass in Kg
    wingmass = 3.550
    # Volume of air used for the calculation of the mass ratio in m^3
    wingvol = 6.926e4 / 100.0**3
    # Free stream Mach number
    Machdata = np.array([0.7065, 0.8066, 0.9076, 0.9529])
    # Mass ratio Mh./(pi*rhodata*b*c0^2/4)
    mubardata = np.array([26.9784, 38.2248, 58.9429, 86.6267])
    # Nondimensional flutter speed
    Ustardata = np.array([0.7042, 0.6714, 0.6034, 0.5226])
    # Flutter speed ratio
    freqflutratio = np.array([0.3500, 0.3395, 0.2900, 0.2282])
    # Dynamic pressure data in Pa
    dynpressdata = np.array([11.5794, 10.4899, 8.4669, 6.3553]) * 1000
elif winglet == 2:
    # Measured wind-off natural frequencies
    omega_mes = np.array([5.7, 25.8, 51.1, 0]) * 2.0 * np.pi  # In rad/s
    # Measured wing mass in Kg
    wingmass = 3.5613
    # Volume of air used for the calculation of the mass ratio in m^3
    wingvol = 6.946e4 / 100.0**3
    # Free stream Mach number
    Machdata = np.array([0.7048, 0.8035, 0.9012])
    # Mass ratio Mh./(pi*rhodata*b*c0^2/4)
    mubardata = np.array([25.8143, 37.0509, 57.6784])
    # Nondimensional flutter speed
    Ustardata = np.array([0.7078, 0.6625, 0.5941])
    # Flutter speed ratio
    freqflutratio = np.array([0.3478, 0.3184, 0.2829])
    # Dynamic pressure data in Pa
    dynpressdata = np.array([11.5574, 10.2433, 8.2454]) * 1000
elif winglet == 3:
    # Measured wind-off natural frequencies
    omega_mes = np.array([5.4, 24.0, 50.5, 58.7]) * 2.0 * np.pi  # In rad/s
    # Measured wing mass in Kg
    wingmass = 3.6130
    # Volume of air used for the calculation of the mass ratio in m^3
    wingvol = 6.946e4 / 100.0**3
    # Free stream Mach number
    Machdata = np.array([0.7129, 0.8159, 0.9078, 0.9341])
    # Mass ratio Mh./(pi*rhodata*b*c0^2/4)
    mubardata = np.array([29.9615, 43.7497, 66.1238, 80.7051])
    # Nondimensional flutter speed
    Ustardata = np.array([0.6711, 0.6358, 0.5680, 0.5298])
    # Flutter speed ratio
    freqflutratio = np.array([0.3209, 0.3055, 0.2575, 0.2374])
    # Dynamic pressure data in Pa
    dynpressdata = np.array([10.3205, 9.2556, 7.4888, 6.4732]) * 1000
# End if
# Chordwise reference length in m
cref = 9.36 / 100.0
# Frequency of first torsion mode from experiment
omega_alpha = omega_mes[2]
# Calculate free stream air density in kg/m^3
rhodata = wingmass / wingvol / mubardata
# Calculate flutter frequency in rad/s
freqflutdata = freqflutratio * omega_alpha
# Calculate flutter airspeed data in m/s
Uflutdata = np.sqrt(2.0 * dynpressdata / rhodata)
# Total number of runs
nruns = Machdata.size

# Select reduced frequency values
kvec = np.array([0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 2.0])

# Select airspeed range in m/s
Uv = np.linspace(70, 150, num=101)

# Choose order of pressure coefficient equation
cp_order = 2  # 1 for linear and 2 for second order

# Set values of mean (or steady) angles of attack and sideslip
alpha0 = 0.0 * np.pi / 180.0  # Angle of attack in rad
beta0 = 0.0 * np.pi / 180.0  # Angle of sideslip in rad

# Number of bodies
nbody = 1
# Initialize body struct array
body = np.zeros(nbody, dtype=tp_body)

# Input first body
# Choose numbers of panels for this wing and its wake
nhalf = 20  # Number of spanwise panels per half-wing.
m = 20  # Number of chordwise panels
nchords = 10  # Set length of wake in chord lengths
# Calculate number of chordwise wake rings
mw = m * nchords
# Number of trapezoidal sections
if winglet == 1:
    ntrap = 2
else:
    ntrap = 3
# End if
# Initialize trapezoidal section struct array
trap = np.zeros(ntrap, dtype=tp_trap)

# Define trapezoidal section 1
bhalf = 36.576 / 100.0  # Span in m
c0 = 55.53 / 100.0  # Root chord in m
lamda = 0.5137  # Taper ratio
LamdaLE = 38.2 * np.pi / 180.0  # Sweep at leading edge
roottwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
tiptwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
twistcent = 0.0  # Chordwise axis around which twist is defined
dihedral = 0.0 * np.pi / 180.0  # Dihedral angle in rad
# Chordwise distance of winglet root leading edge from previous
# trapezoidal section's tip leading edge
xledist = 0.0
# Set airfoil name (must be the filename of a function in the Common directory)
airfoil = "flatplate"
# Half-thickness of flat plate airfoil
athick = 0.4826 / 100.0 / 2.0
# Chordwise length of bevel
bchord = 0.0139
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

# Define trapezoidal section 2
bhalf = 0.5486  # Span in m
c0 = 0.2853  # Root chord in m
lamda = 0.3893  # Taper ratio
LamdaLE = 38.2 * np.pi / 180.0  # Sweep at leading edge
roottwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
tiptwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
twistcent = 0.0  # Chordwise axis around which twist is defined
dihedral = 0.0 * np.pi / 180.0  # Dihedral angle in rad
# Chordwise distance of winglet root leading edge from previous
# trapezoidal section's tip leading edge
xledist = 0.0
# Set airfoil name (must be the filename of a function in the Common directory)
airfoil = "flatplate"
# Half-thickness of flat plate airfoil
athick = 0.4826 / 100.0 / 2.0
# Chordwise length of bevel
bchord = 0.0139
# Assemble airfoil parameter values
airfoil_params = np.array([athick, bchord])

trap[1] = np.array(
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

# Define trapezoidal section 3
if winglet > 1:
    bhalf = 11.430 / 100.0  # Span in m
    c0 = 6.858 / 100.0  # Root chord in m
    lamda = 0.33  # Taper ratio
    LamdaLE = 39.9 * np.pi / 180.0  # Sweep at leading edge
    roottwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
    tiptwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
    twistcent = 0.0  # Chordwise axis around which twist is defined
    dihedral = (90 - 17.5) * np.pi / 180.0  # Dihedral angle
    # Chordwise distance of winglet root leading edge from previous
    # trapezoidal section's tip leading edge
    xledist = 0.0425
    # Set airfoil name (must be the filename of a function in the Common directory)
    airfoil = "flatplate"
    # Half-thickness of winglet
    if winglet == 2:
        athick = 0.0813 / 100.0 / 2.0
    elif winglet == 3:
        athick = 0.4826 / 100.0 / 2.0
    # End if
    # Chordwise length of bevel
    bchord = 0.0139
    # Assemble airfoil parameter values
    airfoil_params = np.array([athick, bchord])
    trap[2] = np.array(
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
# End if

# Create wing
ibody = 0  # Index of body
name = "wing"  # Name of body
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

# Calculate panel aspect ratio
panelAR = (body["c0"][0] / body["m"][0]) / (body["b"][0] / body["n"][0])
if panelAR < 0.1:
    sys.exit("Panel aspect ratio too low. Increase n or decrease m.")

# Set characteristic chord length: root chord of wing
c0 = body["c0"][0]

# Choose number of modes to include in the structural model
nmodes = 4  # Cannot exceed number of modes in FE model
# File name of Matlab mat file that contains the structural model
if winglet == 1:
    fname = "modes_NASAwing_no_winglet.mat"
elif winglet == 2:
    fname = "modes_NASAwing_winglet_light.mat"
elif winglet == 3:
    fname = "modes_NASAwing_winglet_heavy.mat"
# End if
zeta0 = np.zeros((1, nmodes))  # Structural damping ratios
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
        install_dir,
    )

    # Print out flutter solution
    if Uflut != 0:  # If there is a flutter point
        # Store flutter data for this run
        Uflutvec[irun] = Uflut
        # Calculate flutter speed index
        Ustarvec[irun] = Uflut / (cref * omega_alpha * np.sqrt(mubar))
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
axx.set_ylabel("$\omega_F$ (rad/s)")
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
axx.legend(loc="upper right")

# Plot flutter frequency ratio
fig, axx = plt.subplots()
axx.plot(Machdata, freqflutvec / omega_alpha, label="SDPM")
axx.plot(
    Machdata,
    freqflutratio,
    "o",
    label="Exp.",
)
axx.set_xlabel("$M_{\infty}$")
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
axx.set_xlabel("$M_{\infty}$")
axx.set_ylabel("$1/2 \\rho_F Q_F^2$")
axx.grid()
axx.legend(loc="upper right")

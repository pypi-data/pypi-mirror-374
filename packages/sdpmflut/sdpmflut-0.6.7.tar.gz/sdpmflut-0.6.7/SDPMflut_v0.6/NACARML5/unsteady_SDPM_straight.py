#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program unsteady_SDPM_straight calculates the aerodynamic stability
derivatives of the straight tapered wing described in NACA RML55A07,
NACA RML55L14 and NACA RML58B26.

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
from SDPMgeometry import SDPMgeometry_trap_fun
from SDPMgeometry import makewingtips
import SDPMcalcs

# Create SDPM data types
tp_trap, tp_body, _ = SDPMcalcs.SDPMdtypes()

# Run data from wind tunnel tests of wing. Sources: NACA RML55A07,
# NACA RML55L14 and NACA RML58B26
# Set dynamic pressure
dynpress = 24.9 * 47.88
# Set air density
rho = 1.225
# Set speed of sound
asound = 340.3
# Set Reynolds number
Re = 696000
# Calcculate free stream airspeed from dynamic pressure and air density
Qinf = np.sqrt(dynpress / (1 / 2.0 * rho))
Mach = Qinf / asound
# Calculate subsonic compressibility factor
beta = np.sqrt(1 - Mach**2)
# Reference chordwise length (Mean Aerodynamic Chord)
cref = 0.2334
# Reference planform area
Sref = 0.2090
# Reference spanwise length
bref = 0.9144

# Wind tunnel test data
# Pitch angles
pitchdata = (
    np.array([-4.05, -2.07, 0.29, 2.15, 4.22, 6.29, 8.40, 10.09, 12.35, 14.45, 16.37])
    * np.pi
    / 180.0
)
# Pitching moment data
Cmdata = np.array(
    [
        0.0282,
        0.0246,
        0.0228,
        0.0242,
        0.0224,
        0.0155,
        -0.0047,
        -0.0448,
        -0.0684,
        -0.0802,
        -0.0887,
    ]
)
# Drag coefficient data
CDdata = np.array(
    [
        0.0500,
        0.0430,
        0.0361,
        0.0392,
        0.0525,
        0.0752,
        0.1073,
        0.1542,
        0.1871,
        0.2285,
        0.2528,
    ]
)
# Lift coefficient data
CLdata = np.array(
    [-0.264, -0.136, 0.009, 0.141, 0.281, 0.406, 0.5220, 0.590, 0.595, 0.643, 0.651]
)
# Stability derivative data
CYrdata = np.array(
    [
        np.nan,
        np.nan,
        0.0000,
        -0.0074,
        -0.0090,
        -0.0086,
        -0.0278,
        -0.0431,
        -0.1936,
        -0.1560,
        -0.1379,
    ]
)
Clrdata_steady = np.array(
    [
        np.nan,
        np.nan,
        -0.0020,
        0.0279,
        0.0518,
        0.0698,
        0.1193,
        0.1942,
        0.3358,
        0.4675,
        0.4974,
    ]
)
Clrdata = np.array(
    [
        np.nan,
        np.nan,
        -0.0118,
        0.0161,
        0.0381,
        0.0659,
        0.0330,
        -0.0548,
        -0.1799,
        -0.2540,
        -0.3477,
    ]
)
Clrdotdata = np.array(
    [
        np.nan,
        np.nan,
        -0.0459,
        -0.0529,
        -0.0736,
        -0.1271,
        -0.1533,
        0.0118,
        0.3763,
        0.8201,
        0.7448,
    ]
)
Cnrdata_steady = np.array(
    [
        np.nan,
        np.nan,
        -0.0091,
        0.0000,
        -0.0108,
        -0.0200,
        -0.0370,
        -0.0339,
        -0.0631,
        -0.1150,
        -0.1432,
    ]
)
Cnrdata = np.array(
    [
        np.nan,
        np.nan,
        0.0039,
        0.0018,
        0.0014,
        -0.0087,
        -0.0056,
        -0.0121,
        0.0153,
        0.0288,
        0.0851,
    ]
)
Cnrdotdata = np.array(
    [
        np.nan,
        np.nan,
        0.0059,
        0.0096,
        0.0074,
        0.0052,
        -0.0705,
        -0.0550,
        -0.0748,
        -0.1506,
        -0.1233,
    ]
)
CYbetadata = np.array(
    [
        -0.0007,
        -0.0005,
        -0.0003,
        -0.0007,
        -0.0009,
        -0.0013,
        -0.0012,
        -0.0015,
        -0.0006,
        -0.0003,
        0.0011,
    ]
)
Clbetadata = np.array(
    [
        np.nan,
        np.nan,
        np.nan,
        -0.0080,
        -0.0223,
        -0.0383,
        -0.0597,
        -0.0942,
        -0.1287,
        -0.2118,
        -0.2992,
    ]
)
Cnbetadata = np.array(
    [
        np.nan,
        np.nan,
        0.0063,
        0.0050,
        0.0047,
        0.0072,
        0.0090,
        0.0210,
        0.0332,
        0.0489,
        0.0778,
    ]
)
Clbetadotdata = np.array(
    [
        np.nan,
        np.nan,
        -0.0356,
        -0.0483,
        -0.0642,
        -0.0592,
        -0.0572,
        -0.0641,
        0.2963,
        0.3634,
        0.3713,
    ]
)
Cnbetadotdata = np.array(
    [
        np.nan,
        np.nan,
        0.0091,
        -0.0059,
        -0.0062,
        -0.0035,
        -0.0009,
        -0.0100,
        -0.0541,
        -0.0486,
        -0.0869,
    ]
)
# Total number of runs
nruns = len(pitchdata)

# Reduced frequency based on wing half-span
kvec = np.array([0.23])
nk = len(kvec)

# Set values of mean angles of attack and sideslip. We are setting up the
# simulation like a wind tunnel experiment, the free stream angles are
# always zero. DO NOT CHANGE THEM.
alpha0 = 0 * np.pi / 180  # Angle of attack in rad
beta0 = 0 * np.pi / 180  # Angle of sideslip in rad

# Choose order of pressure coefficient equation
cp_order = 2  # 1 for linear and 2 for second order

# Number of bodies
nbody = 3
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
bhalf = 0.4572  # Span in m of half-wing
c0 = 0.2858  # Root chord in m
lamda = 0.6  # Taper ratio
LamdaLE = 3.5763 * np.pi / 180.0
# Sweep at leading edge in rad
roottwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
tiptwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
dihedral = 0.0 * np.pi / 180.0  # Dihedral angle in rad
twistcent = 0.0  # Chordwise axis around which twist is defined
# Chordwise distance of root leading edge from previous
# trapezoidal section's tip leading edge
xledist = 0.0
# Set airfoil name (must be the filename of a function in the Common directory)
airfoil = "flatplate"
# Set airfoil parameters
athick = 0.0095  # Half-thickness of flat plate airfoil
bchord = 0.1089  # Cohrdwise length of bevel
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

# Centre of rotation
xf0 = 1 / 4.0 * c0
yf0 = 0.0
zf0 = 0.0
# Calculate position of axis origin (1/4 of the Mean Aerodynamic Chord)
yMAC = (cref - c0) / (lamda * c0 - c0) * bhalf
xLE_MAC = yMAC * np.tan(LamdaLE)
x0 = xLE_MAC + cref / 4.0  # In this case, x0 is equal to xf0
y0 = 0.0
z0 = 0.0

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
rollpitchyaw = np.array([0, 0, 0]) * np.pi / 180.0
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
# Calculate vertices of wingtip panels
body = makewingtips(body, ibody, mirroredwing)

# Plot all bodies
fig, axx = plt.subplots(subplot_kw={"projection": "3d"})
for i in range(0, len(body)):
    axx.plot_surface(body["Xp0"][i], body["Yp0"][i], body["Zp0"][i])
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

# Initialize result arrays
CD = np.zeros((nruns, nk))
CY = np.zeros((nruns, nk))
CL = np.zeros((nruns, nk))
Cl = np.zeros((nruns, nk))
Cm = np.zeros((nruns, nk))
Cn = np.zeros((nruns, nk))
CYv = np.zeros((nruns, nk), dtype=complex)
CYvdot = np.zeros((nruns, nk), dtype=complex)
CYr = np.zeros((nruns, nk), dtype=complex)
Clv = np.zeros((nruns, nk), dtype=complex)
Clvdot = np.zeros((nruns, nk), dtype=complex)
Clr = np.zeros((nruns, nk), dtype=complex)
Clrdot = np.zeros((nruns, nk), dtype=complex)
Cnv = np.zeros((nruns, nk), dtype=complex)
Cnvdot = np.zeros((nruns, nk), dtype=complex)
Cnr = np.zeros((nruns, nk), dtype=complex)
Cnrdot = np.zeros((nruns, nk), dtype=complex)

print("Calculating flutter solutions for all experimental test cases")
for irun in range(0, nruns):
    print("Simulating run " + str(irun + 1))

    # Recreate the body at the current pitch angle value
    # Define roll, pitch and yaw angles
    rollpitchyaw = np.array([0, pitchdata[irun], 0])
    # Define roll, pitch and yaw centre (x,y,z position of rotation centre)
    rollpitchyaw_cent = np.array([xf0, yf0, zf0])
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
    # Calculate vertices of wingtip panels
    body = makewingtips(body, ibody, mirroredwing)

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
            x0,
            y0,
            z0,
            install_dir,
        )
    )

    # Calculate steady aerodynamic load coefficients on the panels
    CD[irun] = np.sum(body["Fx0"][0]) / Sref
    CY[irun] = np.sum(body["Fy0"][0]) / Sref
    CL[irun] = np.sum(body["Fz0"][0]) / Sref
    Cl[irun] = np.sum(body["Mx0"][0]) / Sref / bref
    Cm[irun] = np.sum(body["My0"][0]) / Sref / cref
    Cn[irun] = np.sum(body["Mz0"][0]) / Sref / bref

    for ik in range(0, nk):
        # Convert reduced frequency based on half-span to reduced frequency based on half-chord
        k = kvec[ik] / bhalf * c0 / 2.0
        # Calculate aerodynamic stability derivatives
        stabder = SDPMcalcs.aerostabderiv(
            body,
            allbodies,
            Aphi,
            Bphi,
            Cphi,
            barUinf,
            barVinf,
            barWinf,
            k,
            c0,
            Mach,
            beta,
            cp_order,
            xf0,
            yf0,
            zf0,
            Sref,
            bref,
            cref,
            install_dir,
        )

        # Store required lateral aerodynamic stability derivatives
        CYv[irun, ik] = stabder["CYv"][0]
        CYvdot[irun, ik] = stabder["CYvdot"][0]
        CYr[irun, ik] = stabder["CYr"][0]
        Clv[irun, ik] = stabder["Clv"][0]
        Clvdot[irun, ik] = stabder["Clvdot"][0]
        Clr[irun, ik] = stabder["Clr"][0]
        Clrdot[irun, ik] = stabder["Clrdot"][0]
        Cnv[irun, ik] = stabder["Cnv"][0]
        Cnvdot[irun, ik] = stabder["Cnvdot"][0]
        Cnr[irun, ik] = stabder["Cnr"][0]
        Cnrdot[irun, ik] = stabder["Cnrdot"][0]
    # End for
# End for

fig, axx = plt.subplots()
axx.plot(pitchdata * 180 / np.pi, CL, "b-", label="SDPM")
axx.plot(
    pitchdata * 180 / np.pi,
    CLdata,
    "ro",
    label="Exp. $k_b=0$",
)
axx.set_xlabel("$\\alpha$")
axx.set_ylabel("$C_L$")
axx.grid()
axx.legend(loc="upper left")

fig, axx = plt.subplots()
axx.plot(pitchdata * 180 / np.pi, CD, "b-", label="SDPM")
axx.plot(
    pitchdata * 180 / np.pi,
    CDdata,
    "ro",
    label="Exp. $k_b=0$",
)
axx.set_xlabel("$\\alpha$")
axx.set_ylabel("$C_D$")
axx.grid()
axx.legend(loc="upper left")

fig, axx = plt.subplots()
axx.plot(pitchdata * 180 / np.pi, Cm, "b-", label="SDPM")
axx.plot(
    pitchdata * 180 / np.pi,
    Cmdata,
    "ro",
    label="Exp. $k_b=0$",
)
axx.set_xlabel("$\\alpha$")
axx.set_ylabel("$C_m$")
axx.grid()
axx.legend(loc="lower left")

fig, axx = plt.subplots()
axx.plot(pitchdata * 180 / np.pi, np.real(CYr), "b-", label="SDPM")
axx.plot(
    pitchdata * 180 / np.pi,
    CYrdata,
    "ro",
    label="Exp. $k_b=0$",
)
axx.set_xlabel("$\\alpha$")
axx.set_ylabel("$C_{Y_r}$")
axx.grid()
axx.legend(loc="lower left")

fig, axx = plt.subplots()
axx.plot(pitchdata * 180 / np.pi, np.real(Clr), "b-", label="SDPM")
axx.plot(
    pitchdata * 180 / np.pi,
    Clrdata_steady,
    "ro",
    label="Exp. $k_b=0$",
)
axx.plot(
    pitchdata * 180 / np.pi,
    Clrdata,
    "rx",
    label="Exp. $k_b=0.23$",
)
axx.set_xlabel("$\\alpha$")
axx.set_ylabel("$C_{l_r}$")
axx.grid()
axx.legend(loc="upper left")

fig, axx = plt.subplots()
axx.plot(
    pitchdata * 180 / np.pi, np.real(Clrdot / (1j * kvec[0]) ** 2.0), "b-", label="SDPM"
)
axx.plot(
    pitchdata * 180 / np.pi,
    Clrdotdata,
    "ro",
    label="Exp. $k_b=0$",
)
axx.set_xlabel("$\\alpha$")
axx.set_ylabel("$C_{l_{\dot{r}}}$")
axx.grid()
axx.legend(loc="upper left")

fig, axx = plt.subplots()
axx.plot(pitchdata * 180 / np.pi, np.real(Cnr), "b-", label="SDPM")
axx.plot(
    pitchdata * 180 / np.pi,
    Cnrdata_steady,
    "ro",
    label="Exp. $k_b=0$",
)
axx.plot(
    pitchdata * 180 / np.pi,
    Cnrdata,
    "rx",
    label="Exp. $k_b=0.23$",
)
axx.set_xlabel("$\\alpha$")
axx.set_ylabel("$C_{n_r}$")
axx.grid()
axx.legend(loc="upper left")

fig, axx = plt.subplots()
axx.plot(
    pitchdata * 180 / np.pi, np.real(Cnrdot / (1j * kvec[0]) ** 2.0), "b-", label="SDPM"
)
axx.plot(
    pitchdata * 180 / np.pi,
    Cnrdotdata,
    "ro",
    label="Exp. $k_b=0$",
)
axx.set_xlabel("$\\alpha$")
axx.set_ylabel("$C_{n_{\dot{r}}}$")
axx.grid()
axx.legend(loc="lower left")

fig, axx = plt.subplots()
axx.plot(pitchdata * 180 / np.pi, -np.real(CYv), "b-", label="SDPM")
axx.plot(
    pitchdata * 180 / np.pi,
    CYbetadata,
    "ro",
    label="Exp. $k_b=0$",
)
axx.set_xlabel("$\\alpha$")
axx.set_ylabel("$C_{Y_{\\beta}}$")
axx.grid()
axx.legend(loc="lower left")

fig, axx = plt.subplots()
axx.plot(pitchdata * 180 / np.pi, -np.real(Clv), "b-", label="SDPM")
axx.plot(
    pitchdata * 180 / np.pi,
    Clbetadata,
    "ro",
    label="Exp. $k_b=0$",
)
axx.set_xlabel("$\\alpha$")
axx.set_ylabel("$C_{l_{\\beta}}$")
axx.grid()
axx.legend(loc="lower left")

fig, axx = plt.subplots()
axx.plot(pitchdata * 180 / np.pi, -np.real(Cnv), "b-", label="SDPM")
axx.plot(
    pitchdata * 180 / np.pi,
    Cnbetadata,
    "ro",
    label="Exp. $k_b=0$",
)
axx.set_xlabel("$\\alpha$")
axx.set_ylabel("$C_{n_{\\beta}}$")
axx.grid()
axx.legend(loc="upper left")

fig, axx = plt.subplots()
axx.plot(pitchdata * 180 / np.pi, -np.real(Clvdot), "b-", label="SDPM")
axx.plot(
    pitchdata * 180 / np.pi,
    Clbetadotdata,
    "ro",
    label="Exp. $k_b=0$",
)
axx.set_xlabel("$\\alpha$")
axx.set_ylabel("$C_{l_{\dot{\\beta}}}$")
axx.grid()
axx.legend(loc="upper left")

fig, axx = plt.subplots()
axx.plot(pitchdata * 180 / np.pi, -np.real(Cnvdot), "b-", label="SDPM")
axx.plot(
    pitchdata * 180 / np.pi,
    Cnbetadotdata,
    "ro",
    label="Exp. $k_b=0$",
)
axx.set_xlabel("$\\alpha$")
axx.set_ylabel("$C_{n_{\dot{\\beta}}}$")
axx.grid()
axx.legend(loc="lower left")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program unsteady_SDPM_straight calculates the aerodynamic stability
derivatives of the swept tapered wing described in NACA RML55A07,
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
    np.array(
        [
            -4.04,
            -1.97,
            0.10,
            2.08,
            4.15,
            6.17,
            8.29,
            10.35,
            12.46,
            14.53,
            16.50,
            18.61,
            20.63,
            22.59,
            24.61,
            26.58,
            28.60,
            30.56,
            32.50,
        ]
    )
    * np.pi
    / 180.0
)
# Pitching moment data
Cmdata = (
    np.array(
        [
            -0.0884,
            -0.0871,
            -0.1020,
            -0.1414,
            -0.1237,
            -0.1386,
            -0.1290,
            -0.1031,
            -0.0201,
            0.0957,
            0.3174,
            0.4494,
            0.5161,
            0.4929,
            0.3881,
            0.3569,
            0.2930,
            0.0085,
            np.nan,
        ]
    )
    / 10.0
)
# Drag coefficient data
CDdata = np.array(
    [
        0.0552,
        0.0452,
        0.0451,
        0.0480,
        0.0530,
        0.0648,
        0.1056,
        0.1304,
        0.1671,
        0.2099,
        0.2506,
        0.2953,
        0.3381,
        0.3748,
        0.4096,
        0.4623,
        0.5179,
        0.5378,
        np.nan,
    ]
)
# Lift coefficient data
CLdata = np.array(
    [
        -0.1140,
        0.0024,
        0.1164,
        0.2375,
        0.3468,
        0.4537,
        0.5867,
        0.6841,
        0.7791,
        0.8527,
        0.8979,
        0.9477,
        0.9691,
        0.9572,
        0.9406,
        0.9382,
        0.9739,
        0.9240,
        np.nan,
    ]
)
# Stability derivative data
CYrdata = np.array(
    [
        np.nan,
        np.nan,
        -0.0020,
        np.nan,
        -0.0084,
        np.nan,
        0.0249,
        np.nan,
        -0.0266,
        np.nan,
        -0.0138,
        -0.0252,
        -0.0242,
        np.nan,
        0.0553,
        np.nan,
        0.1144,
        np.nan,
        0.1667,
    ]
)
Clrdata_steady = np.array(
    [
        np.nan,
        np.nan,
        -0.0149,
        np.nan,
        0.0253,
        np.nan,
        0.0179,
        np.nan,
        0.0214,
        np.nan,
        -0.0104,
        -0.0229,
        -0.0097,
        np.nan,
        0.0006,
        np.nan,
        -0.0082,
        np.nan,
        -0.0481,
    ]
)
Cnrdata_steady = np.array(
    [
        np.nan,
        np.nan,
        -0.0134,
        np.nan,
        -0.0141,
        np.nan,
        -0.0014,
        np.nan,
        -0.0129,
        np.nan,
        -0.0136,
        -0.0087,
        -0.0023,
        np.nan,
        -0.0058,
        np.nan,
        -0.0066,
        np.nan,
        -0.0181,
    ]
)
Clrdata = np.array(
    [
        np.nan,
        np.nan,
        0.0068,
        np.nan,
        0.0605,
        np.nan,
        0.1955,
        np.nan,
        0.2994,
        np.nan,
        0.3150,
        np.nan,
        0.3008,
        np.nan,
        0.3002,
        np.nan,
        0.2697,
        np.nan,
        0.1078,
    ]
)
Cnrdata = np.array(
    [
        np.nan,
        np.nan,
        -0.0013,
        np.nan,
        0.0020,
        np.nan,
        -0.0228,
        np.nan,
        -0.0612,
        np.nan,
        -0.0941,
        np.nan,
        -0.1164,
        np.nan,
        -0.1468,
        np.nan,
        -0.1878,
        np.nan,
        -0.0933,
    ]
)
Clrdotdata = np.array(
    [
        np.nan,
        np.nan,
        0.0229,
        np.nan,
        -0.0967,
        np.nan,
        -0.3078,
        np.nan,
        -0.4786,
        np.nan,
        -0.7597,
        np.nan,
        -0.8417,
        np.nan,
        -0.7916,
        np.nan,
        -0.6985,
        np.nan,
        0.0546,
    ]
)
Cnrdotdata = np.array(
    [
        np.nan,
        np.nan,
        0.0339,
        0.0100,
        -0.0001,
        0.0089,
        0.0455,
        np.nan,
        0.1900,
        np.nan,
        0.3097,
        np.nan,
        0.3497,
        np.nan,
        0.4118,
        np.nan,
        0.5342,
        np.nan,
        0.6703,
    ]
)
CYbetadata = np.array(
    [
        -0.0011,
        -0.0009,
        -0.0009,
        -0.0010,
        -0.0010,
        -0.0003,
        -0.0018,
        -0.0018,
        -0.0020,
        -0.0020,
        -0.0024,
        -0.0028,
        -0.0034,
        -0.0041,
        -0.0046,
        -0.0048,
        -0.0046,
        -0.0049,
        np.nan,
    ]
)
Clbetadata = np.array(
    [
        np.nan,
        np.nan,
        -0.0080,
        np.nan,
        -0.0647,
        np.nan,
        -0.0235,
        0.0194,
        0.0336,
        np.nan,
        0.0220,
        0.0062,
        0.0137,
        0.0195,
        0.0167,
        0.0202,
        -0.0097,
        -0.0278,
        np.nan,
    ]
)
Cnbetadata = np.array(
    [
        np.nan,
        np.nan,
        0.0028,
        np.nan,
        0.0103,
        np.nan,
        0.0131,
        0.0190,
        0.0146,
        np.nan,
        0.0115,
        0.0184,
        0.0152,
        0.0111,
        0.0147,
        0.0017,
        -0.0036,
        -0.0017,
        np.nan,
    ]
)
Clbetadotdata = np.array(
    [
        np.nan,
        np.nan,
        -0.0035,
        np.nan,
        -0.0424,
        np.nan,
        -0.1175,
        -0.2493,
        -0.3656,
        np.nan,
        -0.6008,
        -0.6836,
        -0.6061,
        -0.4796,
        -0.4512,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
    ]
)
Cnbetadotdata = np.array(
    [
        np.nan,
        np.nan,
        0.0033,
        np.nan,
        0.0007,
        np.nan,
        0.0184,
        0.0272,
        0.0562,
        np.nan,
        0.1295,
        0.1788,
        0.1826,
        0.1762,
        0.2154,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
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
LamdaLE = 45.0 * np.pi / 180.0
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
xf0 = 11.06 * 0.0254
yf0 = 0.0
zf0 = 0.0
# Calculate position of axis origin (1/4 of the Mean Aerodynamic Chord)
yMAC = (cref - c0) / (lamda * c0 - c0) * bhalf
xLE_MAC = yMAC * np.tan(LamdaLE)
x0 = xLE_MAC + cref / 4.0  # In this case, x0 is not equal to xf0
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
axx.legend(loc="upper left")

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
axx.legend(loc="upper left")

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
axx.legend(loc="lower left")

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
axx.legend(loc="lower left")

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
axx.legend(loc="upper left")

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
axx.legend(loc="lower left")

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
axx.legend(loc="upper left")

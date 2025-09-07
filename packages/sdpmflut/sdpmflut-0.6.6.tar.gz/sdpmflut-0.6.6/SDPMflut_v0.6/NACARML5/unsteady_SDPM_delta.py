#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program unsteady_SDPM_straight calculates the aerodynamic stability
derivatives of the Delta wing described in NACA RML55A07,
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
Re = 1580000
# Calcculate free stream airspeed from dynamic pressure and air density
Qinf = np.sqrt(dynpress / (1 / 2.0 * rho))
Mach = Qinf / asound
# Calculate subsonic compressibility factor
beta = np.sqrt(1 - Mach**2)
# Reference chordwise length (Mean Aerodynamic Chord)
cref = 0.5281
# Reference planform area
Sref = 0.3621
# Reference spanwise length
bref = 0.9144

# Wind tunnel test data
# Pitch angles
pitchdata = (
    np.array(
        [
            -4.36,
            -2.26,
            0.00,
            1.91,
            4.10,
            6.05,
            8.18,
            10.34,
            12.44,
            14.55,
            16.61,
            18.56,
            20.78,
            22.75,
            24.92,
            26.99,
            29.18,
            31.09,
            33.18,
        ]
    )
    * np.pi
    / 180.0
)
# Pitching moment data
Cmdata = (
    np.array(
        [
            0.0889,
            -0.0179,
            -0.1090,
            -0.2002,
            -0.3223,
            -0.3982,
            -0.4585,
            -0.5342,
            -0.5946,
            -0.7013,
            -0.7616,
            -0.8375,
            -0.8746,
            -0.9350,
            -1.0029,
            -1.0864,
            -1.1854,
            -1.2536,
            -1.3680,
        ]
    )
    / 10.0
)
# Drag coefficient data
CDdata = np.array(
    [
        0.0316,
        0.0285,
        0.0255,
        0.0294,
        0.0371,
        0.0502,
        0.0680,
        0.0903,
        0.1203,
        0.1558,
        0.1973,
        0.2405,
        0.2982,
        0.3513,
        0.4175,
        0.4806,
        0.5591,
        0.6176,
        0.6907,
    ]
)
# Lift coefficient data
CLdata = np.array(
    [
        -0.1271,
        -0.0535,
        0.0421,
        0.1221,
        0.2161,
        0.2960,
        0.3885,
        0.4747,
        0.5656,
        0.6628,
        0.7443,
        0.8367,
        0.9041,
        0.9683,
        1.0404,
        1.1109,
        1.1799,
        1.2284,
        1.2425,
    ]
)
# Stability derivative data
CYrdata = np.array(
    [
        np.nan,
        np.nan,
        -0.0151,
        np.nan,
        -0.0065,
        np.nan,
        0.0197,
        np.nan,
        -0.0222,
        0.0318,
        0.0671,
        0.0706,
        0.0748,
        0.0724,
        0.0750,
        0.1095,
        0.2617,
        0.3114,
        0.1913,
    ]
)
Clrdata_steady = np.array(
    [
        np.nan,
        np.nan,
        -0.0254,
        np.nan,
        0.0083,
        np.nan,
        0.0343,
        np.nan,
        0.0261,
        0.0264,
        0.0140,
        0.0108,
        0.0067,
        -0.0180,
        -0.0337,
        -0.0493,
        -0.0675,
        -0.1090,
        -0.1604,
    ]
)
Clrdata = np.array(
    [
        np.nan,
        np.nan,
        0.0145,
        np.nan,
        0.0557,
        np.nan,
        0.1058,
        np.nan,
        0.1626,
        np.nan,
        0.1670,
        np.nan,
        0.2238,
        np.nan,
        0.2224,
        np.nan,
        0.2318,
        np.nan,
        0.2180,
    ]
)
Cnrdata_steady = np.array(
    [
        np.nan,
        np.nan,
        -0.0098,
        np.nan,
        -0.0122,
        np.nan,
        -0.0155,
        np.nan,
        -0.0229,
        -0.0205,
        np.nan,
        -0.0213,
        -0.0304,
        -0.0287,
        -0.0222,
        -0.0099,
        -0.0043,
        0.0316,
        0.1059,
    ]
)
Cnrdata = np.array(
    [
        np.nan,
        np.nan,
        -0.0008,
        np.nan,
        -0.0081,
        np.nan,
        -0.0098,
        np.nan,
        -0.0229,
        np.nan,
        -0.0295,
        np.nan,
        -0.0483,
        np.nan,
        -0.0745,
        np.nan,
        -0.0851,
        np.nan,
        -0.0860,
    ]
)
Clrdotdata = np.array(
    [
        np.nan,
        np.nan,
        -0.0019,
        np.nan,
        -0.1495,
        np.nan,
        -0.2263,
        np.nan,
        -0.4057,
        np.nan,
        -0.4359,
        np.nan,
        -0.5948,
        np.nan,
        -0.7201,
        np.nan,
        -0.7931,
        np.nan,
        -0.8196,
    ]
)
Cnrdotdata = np.array(
    [
        np.nan,
        np.nan,
        0.0681,
        np.nan,
        0.0668,
        np.nan,
        0.0746,
        np.nan,
        0.0880,
        np.nan,
        0.1924,
        np.nan,
        0.2095,
        np.nan,
        0.2397,
        np.nan,
        0.3385,
        np.nan,
        0.4206,
    ]
)
CYbetadata = np.array(
    [
        -0.0007,
        -0.0007,
        -0.0006,
        -0.0006,
        -0.0007,
        -0.0009,
        -0.0011,
        -0.0014,
        -0.0015,
        -0.0017,
        -0.0019,
        -0.0023,
        -0.0026,
        -0.0032,
        -0.0027,
        -0.0031,
        -0.0040,
        -0.0051,
        -0.0068,
    ]
)
Clbetadata = np.array(
    [
        np.nan,
        np.nan,
        -0.0153,
        np.nan,
        -0.0510,
        np.nan,
        -0.0865,
        np.nan,
        -0.1080,
        np.nan,
        -0.1161,
        -0.1020,
        -0.1140,
        -0.1261,
        -0.1303,
        -0.1308,
        -0.1378,
        -0.1431,
        -0.1306,
    ]
)
Cnbetadata = np.array(
    [
        np.nan,
        np.nan,
        0.0021,
        np.nan,
        0.0035,
        np.nan,
        0.0159,
        np.nan,
        0.0322,
        np.nan,
        0.0482,
        0.0630,
        0.0639,
        0.0714,
        0.0847,
        0.0818,
        0.0783,
        0.0729,
        0.0624,
    ]
)
Clbetadotdata = np.array(
    [
        np.nan,
        np.nan,
        -0.0102,
        np.nan,
        -0.0290,
        np.nan,
        -0.0593,
        np.nan,
        -0.1261,
        np.nan,
        -0.1238,
        -0.3175,
        -0.2866,
        -0.3594,
        -0.4840,
        -0.4415,
        -0.4855,
        -0.4795,
        -0.4812,
    ]
)
Cnbetadotdata = np.array(
    [
        np.nan,
        np.nan,
        0.0049,
        np.nan,
        0.0047,
        np.nan,
        0.0104,
        np.nan,
        0.0102,
        np.nan,
        0.0198,
        0.0433,
        0.0649,
        0.0982,
        0.1414,
        0.1275,
        0.1550,
        0.1548,
        0.1882,
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
bhalf = 0.4572  # Span in m of half-wing
c0 = 0.7920  # Root chord in m
lamda = 0.0  # Taper ratio
LamdaLE = 60.0 * np.pi / 180.0
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
xf0 = 0.3960
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

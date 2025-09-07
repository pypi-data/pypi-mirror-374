#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program unsteady_SDPM_NASATND344 calculates the steady and unsteady pressure
distributions around the rectangular wing undergoing forced bending
motion tested by Lessing et al in NASA TN D-344.

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
from forcedbending import modes_NASATND344
import FEmodes
import SDPMcalcs

# Create SDPM data types
tp_trap, tp_body, _ = SDPMcalcs.SDPMdtypes()

# Run data from wind tunnel tests of wing. Source:
# Experimental determination of the pressure distribution on a rectangular
# wing oscillating in the first bending mode for Mach numbers from 0.24 to
# 1.3. H. C. Lessing, J. L. Troutman and G. P. Menees, NASA TN D-344, 1960
# Bending tip amplitude (m)
bendtip_amp = 0.2 * 0.0254
# Bending phase (rad)
Phi_bend = 0.0
# Free stream Mach number
Machdata = np.array(
    [0.24, 0.24, 0.7, 0.7, 0.9, 0.9]
)  # The last two test cases are highly transonic
# Mean angle of attack in degrees
alpha0data = np.array([0.0, 5.0, 0.0, 5.0, 0.0, 5.0]) * np.pi / 180.0
# Reduced frequency
kdata = 0.47 * np.array(
    [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
    ]
)
# Total number of runs
nruns = Machdata.size
# Load experimental pressure data from .mat file
mat = scipy.io.loadmat("dataNASATND344.mat")

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
# Number of trapezoidal sections
ntrap = 1
# Initialize trapezoidal section struct array
trap = np.zeros(ntrap, dtype=tp_trap)

# Input wing geometry
bhalf = 27.44 * 0.0254  # Span in m of half-wing
c0 = 18 * 0.0254  # Root chord in m
lamda = 1.0  # Taper ratio
LamdaLE = 0.0 * np.pi / 180.0
# Sweep at leading edge in rad
roottwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
tiptwist = 0.0 * np.pi / 180.0  # Twist angle at the root in rad
dihedral = 0.0 * np.pi / 180.0  # Dihedral angle in rad
twistcent = 0.0  # Chordwise axis around which twist is defined
# Chordwise distance of root leading edge from previous
# trapezoidal section's tip leading edge
xledist = 0.0
# Set airfoil name (must be the filename of a function in the Common directory)
airfoil = "biconvex"
# Set airfoil parameters
thick = 0.05  # Airfoil thickness to chord ratio
# Assemble airfoil parameter values
airfoil_params = np.array([thick, 0.0])
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

# Choose number of modes to include in the flutter calculation
nmodes = 1  # The wing was forced to oscillate in the first bending mode
# Set up structural modal grid
mFE = 30  # Set desired number of chordwise points
nFE = 30  # Set desired number of spanwise points

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

# Acquire mode shapes (only modeshapesz and its derivative modeshapesRx
# are non-zero)
(
    xxplot,
    yyplot,
    modeshapesx,
    modeshapesy,
    modeshapesz,
    modeshapesRx,
    modeshapesRy,
    modeshapesRz,
) = modes_NASATND344(mFE, nFE)

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

print("Calculating flutter solutions for all experimental test cases")
for irun in range(0, nruns):
    print("Simulating run " + str(irun + 1))

    # Set Mach number of current run
    Mach = Machdata[irun]
    # Set reduced frequency
    k = kdata[irun]
    # Set mean angle of attack
    alpha0 = alpha0data[irun]
    # Calculate subsonic compressibility factor
    beta = np.sqrt(1 - Mach**2)
    # Calculate effective angle of attack at the wingtip
    alpha_h = 2.0 / c0 * k * bendtip_amp

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

    # Plot steady pressures
    fig, axx = plt.subplots(subplot_kw={"projection": "3d"})
    # Plot SDPM pressure predictions
    axx.plot_surface(
        body["Xc0"][0][:, body["n"][0] // 2 : body["n"][0]] / c0,
        body["Yc0"][0][:, body["n"][0] // 2 : body["n"][0]] / bhalf,
        body["cp0"][0][:, body["n"][0] // 2 : body["n"][0]],
        edgecolor="royalblue",
        alpha=0.1,
    )
    # Plot experimental pressure measurements
    axx.scatter(
        mat["x0data"][:, irun],
        mat["y0data"][:, irun],
        mat["cp0data"][:, irun],
        marker="o",
        color="r",
    )
    axx.set_proj_type("ortho")  # FOV = 0 deg
    axx.set_zlim(-1, 0.6)
    axx.set_xlabel("$x/c_0$", labelpad=10)
    axx.set_ylabel("$2y/b$", labelpad=10)
    axx.set_zlabel("$c_p(0)$", labelpad=10)
    axx.zaxis.labelpad = -1
    axx.view_init(26, -120)
    plt.title(
        "$M_{\\infty}=$"
        + str(Mach)
        + ", $\\alpha_0$="
        + str(alpha0 * 180 / np.pi)
        + "$^o$"
    )
    plt.show()

    # Calculate the unsteady pressure coefficients
    cp1, cp_0, cp_1, cp_2 = SDPMcalcs.unsteadysolve_flex(
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
        install_dir,
    )

    # Mulitply cp1 by tip bending amplitude and reshape to a matrix
    cp1mat = (
        bendtip_amp
        / 2.0
        * np.exp(1j * Phi_bend)
        * np.reshape(cp1, (2 * body["m"][0], body["n"][0]), order="C")
    )

    # Calculate pressure jump across the surface
    Dcp1 = np.flipud(cp1mat[0:m, :]) - cp1mat[m : 2 * m, :]

    if irun < 2:
        # For the first two runs, the oscillatory experimental pressure distribution
        # around both the upper and lower surfaces is given
        fig, axx = plt.subplots(subplot_kw={"projection": "3d"})
        # Plot SDPM predictions
        axx.plot_surface(
            body["Xc0"][0][:, body["n"][0] // 2 : body["n"][0]] / c0,
            body["Yc0"][0][:, body["n"][0] // 2 : body["n"][0]] / bhalf,
            2.0 * np.real(cp1mat[:, body["n"][0] // 2 : body["n"][0]]) / alpha_h,
            edgecolor="royalblue",
            alpha=0.1,
        )
        # Plot experimental measurements
        axx.scatter(
            mat["x1rdata"][:, irun],
            mat["y1rdata"][:, irun],
            mat["cp1rdata"][:, irun],
            marker="o",
            color="r",
        )
        axx.set_proj_type("ortho")  # FOV = 0 deg
        axx.set_zlim(-4, 2)
        axx.set_xlabel("$x/c_0$", labelpad=10)
        axx.set_ylabel("$2y/b$", labelpad=10)
        axx.set_zlabel("$\Re(c_p(k))$", labelpad=-5)
        axx.view_init(26, -120)
        plt.title(
            "$M_{\\infty}=$"
            + str(Mach)
            + ", $\\alpha_0$="
            + str(alpha0 * 180 / np.pi)
            + "$^o$"
        )
        plt.show()

        fig, axx = plt.subplots(subplot_kw={"projection": "3d"})
        # Plot SDPM predictions
        axx.plot_surface(
            body["Xc0"][0][:, body["n"][0] // 2 : body["n"][0]] / c0,
            body["Yc0"][0][:, body["n"][0] // 2 : body["n"][0]] / bhalf,
            2.0 * np.imag(cp1mat[:, body["n"][0] // 2 : body["n"][0]]) / alpha_h,
            edgecolor="royalblue",
            alpha=0.1,
        )
        # Plot experimental measurements
        axx.scatter(
            mat["x1idata"][:, irun],
            mat["y1idata"][:, irun],
            mat["cp1idata"][:, irun],
            marker="o",
            color="r",
        )
        axx.set_proj_type("ortho")  # FOV = 0 deg
        axx.set_zlim(-10, 2)
        axx.set_xlabel("$x/c_0$", labelpad=10)
        axx.set_ylabel("$2y/b$", labelpad=10)
        axx.set_zlabel("$\Im(c_p(k))$", labelpad=-5)
        axx.view_init(26, -120)
        plt.title(
            "$M_{\\infty}=$"
            + str(Mach)
            + ", $\\alpha_0$="
            + str(alpha0 * 180 / np.pi)
            + "$^o$"
        )
        plt.show()
    else:
        # For the other runs only the oscillatory pressure jump across the surface
        # is given
        fig, axx = plt.subplots(subplot_kw={"projection": "3d"})
        # Plot SDPM predictions
        axx.plot_surface(
            body["Xc0"][0][m : 2 * m, body["n"][0] // 2 : body["n"][0]] / c0,
            body["Yc0"][0][m : 2 * m, body["n"][0] // 2 : body["n"][0]] / bhalf,
            2.0 * np.abs(Dcp1[:, body["n"][0] // 2 : body["n"][0]]) / alpha_h,
            edgecolor="royalblue",
            alpha=0.1,
        )
        # Plot experimental measurements
        axx.scatter(
            mat["x1absdata"][:, irun],
            mat["y1absdata"][:, irun],
            mat["Dcp1absdata"][:, irun],
            marker="o",
            color="r",
        )
        axx.set_proj_type("ortho")  # FOV = 0 deg
        axx.set_zlim(0, 6)
        axx.set_xlabel("$x/c_0$", labelpad=10)
        axx.set_ylabel("$2y/b$", labelpad=10)
        axx.set_zlabel("$|\Delta c_p(k)|$", labelpad=-6)
        axx.view_init(26, -120)
        plt.title(
            "$M_{\\infty}=$"
            + str(Mach)
            + ", $\\alpha_0$="
            + str(alpha0 * 180 / np.pi)
            + "$^o$"
        )
        plt.show()

        # Calculate phase of pressure jump
        dummy = np.angle(Dcp1[:, body["n"][0] // 2 : body["n"][0]]) * 180.0 / np.pi
        # Unwrap phase of pressure jump
        iko = np.argwhere(dummy < -90)
        for i in range(0, len(iko)):
            dummy[iko[i, :][0], iko[i, :][1]] = dummy[iko[i, :][0], iko[i, :][1]] + 360
        # End for
        fig, axx = plt.subplots(subplot_kw={"projection": "3d"})
        # Plot SDPM predictions
        axx.plot_surface(
            body["Xc0"][0][m : 2 * m, body["n"][0] // 2 : body["n"][0]] / c0,
            body["Yc0"][0][m : 2 * m, body["n"][0] // 2 : body["n"][0]] / bhalf,
            dummy,
            edgecolor="royalblue",
            alpha=0.1,
        )
        # Plot experimental measurements
        axx.scatter(
            mat["x1angdata"][:, irun],
            mat["y1angdata"][:, irun],
            mat["Dcp1angdata"][:, irun],
            marker="o",
            color="r",
        )
        axx.set_proj_type("ortho")  # FOV = 0 deg
        axx.set_zlim(0, 400)
        axx.set_xlabel("$x/c_0$", labelpad=10)
        axx.set_ylabel("$2y/b$", labelpad=10)
        axx.set_zlabel("$angle(\Delta c_p(k))$", labelpad=-3.5)
        axx.view_init(26, -120)
        plt.title(
            "$M_{\\infty}=$"
            + str(Mach)
            + ", $\\alpha_0$="
            + str(alpha0 * 180 / np.pi)
            + "$^o$"
        )
        plt.show()
    # End if
# End for

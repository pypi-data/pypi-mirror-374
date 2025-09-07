#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package SDPMcalcs contains functions to load the influence coeffient matrix
calculation c functions, to apply the Prandtl-Glauert transformation  to a
SDPM grid and to assemble the finite difference matrices and other necessary
matrices and vectors to calculate the flow speeds on the surface.

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

import ctypes
import numpy as np
import platform
from numpy.ctypeslib import ndpointer
from scipy import linalg
import numpy.matlib
from importlib.resources import files
from .SDPMgeometry import SDPM_control_normal_tangential


def _load_shared(basename: str) -> ctypes.CDLL:
    """Load a shared library from the packaged kernels directory."""
    libdir = files("sdpmflut.kernels")
    # Try common suffixes (Windows, Linux, macOS)
    suffixes = [".so", ".pyd", ".dll", ".dylib"]
    # First: exact names like sdpminfso.so / .dll, etc.
    for ext in suffixes:
        p = libdir / f"{basename}{ext}"
        if p.exists():
            return ctypes.CDLL(str(p))
    # Second: glob any ABI-suffixed names (e.g., sdpminfso.cpython-313-x86_64-linux-gnu.so)
    for p in libdir.iterdir():
        if p.name.startswith(basename) and p.suffix in suffixes:
            return ctypes.CDLL(str(p))
    raise RuntimeError(f"Cannot find shared library for {basename} in {libdir}")


def Cfuncs():
    """Load the C functions used by SDPMflut from the packaged kernels.

    Returns:
        tuple: (sdpminf, sdpminf_unsteady_subsonic) - the compiled C functions
    """

    # Load c function to calculate steady SDPM influence coefficients
    lib = _load_shared("sdpminfso")
    sdpminf = lib.sdpminf
    sdpminf.restype = None
    # Define arguments of sdpminf
    sdpminf.argtypes = [
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
    ]

    # Load c function to calculate unsteady SDPM influence coefficients
    libu = _load_shared("sdpminf_unsteadyso")
    sdpminf_unsteady_subsonic = libu.sdpminf_unsteady_subsonic
    sdpminf_unsteady_subsonic.restype = None
    # Define arguments of sdpminf_unsteady_subsonic
    sdpminf_unsteady_subsonic.argtypes = [
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # influenced Xc
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # influenced Yc
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # influenced Zc
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # influencing Xc
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # influencing Yc
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # influencing Zc
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # influencing nx
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # influencing Xcw
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # influencing Ycw
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # influencing Zcw
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # Aphi
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # Bphi
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # Cphi
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # params
        ctypes.c_int,
        ctypes.c_int,  # Influenced m,n
        ctypes.c_int,
        ctypes.c_int,  # Influencing m,n
        ctypes.c_int,
        ctypes.c_int,  # Influencing mw,nw
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # Abarphi_real
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # Abarphi_imag
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # Bbarphi_real
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # Bbarphi_imag
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),  # Cbarphi_real
        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
    ]  # Cbarphi_imag
    return sdpminf, sdpminf_unsteady_subsonic


def SDPMdtypes():
    # Defines all data types used by SDPMflut. These are numpy.dtype variables
    # for numpy arrays.
    # tp_trap: Data type for defining trapezoidal sections of wings
    # tp_body: Data type for defining SDPM grids for bodies
    # tp_allbodies: Data type for concatenating grid and result information for
    #               all bodies in a flow

    # Define trapezoidal section data type
    tp_trap = np.dtype(
        {
            "names": (
                "rootchord",
                "xledist",
                "span",
                "taper",
                "sweepLE",
                "roottwist",
                "tiptwist",
                "twistcent",
                "dihedral",
                "rootairfoil",
                "rootairfoilparams",
                "tipairfoil",
                "tipairfoilparams",
            ),
            "formats": (
                "f8",
                "f8",
                "f8",
                "f8",
                "f8",
                "f8",
                "f8",
                "f8",
                "f8",
                "U25",
                "(2,)f8",
                "U25",
                "(2,)f8",
            ),
        }
    )
    # Define body data type
    tp_body = np.dtype(
        {
            "names": (
                "Xp0",
                "Yp0",
                "Zp0",
                "Xc0",
                "Yc0",
                "Zc0",
                "Xc0all",
                "Yc0all",
                "Zc0all",
                "Xw0",
                "Yw0",
                "Zw0",
                "nx0",
                "ny0",
                "nz0",
                "s0",
                "tauxx0",
                "tauxy0",
                "tauxz0",
                "tauyx0",
                "tauyy0",
                "tauyz0",
                "mw",
                "m",
                "n",
                "c0",
                "yc",
                "AR",
                "S",
                "name",
                "dir_tau",
                "Phi_x",
                "Phi_y",
                "Phi_z",
                "Phi_phi",
                "Phi_theta",
                "Phi_psi",
                "Phi_xall",
                "Phi_yall",
                "Phi_zall",
                "Phi_phiall",
                "Phi_thetaall",
                "Phi_psiall",
                "Xp",
                "Yp",
                "Zp",
                "Xc",
                "Yc",
                "Zc",
                "Xw",
                "Yw",
                "Zw",
                "Xcall",
                "Ycall",
                "Zcall",
                "nx",
                "ny",
                "nz",
                "s",
                "tauxx",
                "tauxy",
                "tauxz",
                "tauyx",
                "tauyy",
                "tauyz",
                "tmx",
                "tmy",
                "tmz",
                "sm",
                "tnx",
                "tny",
                "tnz",
                "sn",
                "Xcw",
                "Ycw",
                "Zcw",
                "nxw",
                "nyw",
                "nzw",
                "tauxxw",
                "tauxyw",
                "tauxzw",
                "tauyxw",
                "tauyyw",
                "tauyzw",
                "nx0all",
                "ny0all",
                "nz0all",
                "nxall",
                "nyall",
                "nzall",
                "s0all",
                "sall",
                "cp0",
                "mu0",
                "muw0",
                "Fx0",
                "Fy0",
                "Fz0",
                "Mx0",
                "My0",
                "Mz0",
                "b",
            ),
            "formats": (
                object,
                object,
                object,  #'Xp0', 'Yp0', 'Zp0'
                object,
                object,
                object,  #'Xc0','Yc0','Zc0'
                object,
                object,
                object,  # 'Xc0all','Yc0all','Zc0all'
                object,
                object,
                object,  # 'Xw0','Yw0','Zw0'
                object,
                object,
                object,
                object,  # 'nx0','ny0','nz0','s0'
                object,
                object,
                object,  # 'tauxx0','tauxy0','tauxz0'
                object,
                object,
                object,  # 'tauyx0','tauyy0','tauyz0'
                np.int64,
                np.int64,
                np.int64,
                np.float64,
                object,  # 'mw','m','n','c0','yc
                np.float64,
                np.float64,
                "S25",
                np.int64,  # 'AR','S','name','dir_tau',
                object,
                object,
                object,  # 'Phi_x','Phi_y','Phi_z'
                object,
                object,
                object,  # 'Phi_phi','Phi_theta','Phi_psi'
                object,
                object,
                object,  # 'Phi_xall','Phi_yall','Phi_zall'
                object,
                object,
                object,  # 'Phi_phiall','Phi_thetaall','Phi_psiall'
                object,
                object,
                object,  # 'Xp','Yp','Zp'
                object,
                object,
                object,  # 'Xc','Yc','Zc'
                object,
                object,
                object,  # 'Xw','Yw','Zw'
                object,
                object,
                object,  # 'Xcall','Ycall','Zcall'
                object,
                object,
                object,
                object,  # 'nx','ny,'nz','s'
                object,
                object,
                object,  # 'tauxx','tauxy','tauxz'
                object,
                object,
                object,  # 'tauyx','tauyy','tauyz'
                object,
                object,
                object,
                object,  # 'tmx','tmy','tmz','sm'
                object,
                object,
                object,
                object,  # 'tnx','tny','tnz','sn'
                object,
                object,
                object,
                object,  # 'Xcw','Ycw','Zcw'
                object,
                object,
                object,
                object,  # 'nxw','nyw','nzw'
                object,
                object,
                object,
                object,  # 'tauxxw','tauxyw','tauxzw'
                object,
                object,
                object,
                object,  # 'tauyxw','tauyyw','tauyzw'
                object,
                object,
                object,
                object,  # 'nx0all','ny0all','nz0all'
                object,
                object,
                object,
                object,  # 'nxall','nyall','nzall'
                object,
                object,
                object,
                object,  # s0all','sall','cp0'
                object,
                object,
                object,
                object,
                object,  # 'mu0','muw0','Fx0','Fy0','Fz0'
                object,
                object,
                object,
                np.float64,
            ),
        }
    )  # 'Mx0','My0','Mz0','b'
    # Define allbodies data type
    tp_allbodies = np.dtype(
        {
            "names": (
                "nbody",
                "bodypanels",
                "bodypanelsn",
                "allpanelsn",
                "wakepanels",
                "allpanels",
                "allpanelsw",
                "inds",
                "indsw",
                "indsn",
                "Xc0all",
                "Yc0all",
                "Zc0all",
                "nx0all",
                "ny0all",
                "nz0all",
                "s0all",
                "Xcall",
                "Ycall",
                "Zcall",
                "nxall",
                "nyall",
                "nzall",
                "Phi_xall",
                "Phi_yall",
                "Phi_zall",
                "Phi_phiall",
                "Phi_thetaall",
                "Phi_psiall",
                "C12",
                "C3",
                "D12",
                "D3",
                "E12",
                "E3",
                "Pc",
                "barphix0",
                "barphiy0",
                "barphiz0",
                "baruc0",
                "barvc0",
                "barwc0",
                "cp0",
                "Fx0",
                "Fy0",
                "Fz0",
                "Mx0",
                "My0",
                "Mz0",
            ),
            "formats": (
                np.int64,
                object,
                object,  # 'nbody', 'bodypanels', 'bodypanelsn'
                np.int64,
                object,
                np.int64,  # 'allpanelsn','wakepanels','allpanels'
                np.int64,
                object,
                object,
                object,  # 'allpanelsw','inds','indsw','indsn'
                object,
                object,
                object,  # 'Xc0all','Yc0all','Zc0all',
                object,
                object,
                object,
                object,  # 'nx0all','ny0all','nz0all','s0all'
                object,
                object,
                object,  # 'Xcall','Ycall','Zcall'
                object,
                object,
                object,  # 'nxall','nyall','nzall'
                object,
                object,
                object,  # 'Phi_xall','Phi_yall','Phi_zall'
                object,
                object,
                object,  # 'Phi_phiall','Phi_thetaall','Phi_psiall'
                object,
                object,
                object,
                object,  # 'C12','C3','D12','D3',
                object,
                object,
                object,  # 'E12','E3','Pc',
                object,
                object,
                object,  # 'barphix0','barphiy0','barphiz0'
                object,
                object,
                object,  # 'baruc0','barvc0','barwc0'
                object,
                object,
                object,
                object,  # 'cp0','Fx0','Fy0','Fz0'
                object,
                object,
                object,
            ),
        }
    )  # 'Mx0','My0','Mz0'
    return tp_trap, tp_body, tp_allbodies


def allbodyindex(body):
    # Calculates the numbers and indices of panels, spanwise panels and wake
    # panels in all bodies stored in struct array body.
    # body: struct array containing the geometry of all the bodies in the flow.
    #       Each element of body describes a different wing, fairing or
    #       fuselage
    # allbodies: struct array containing concatenated information for all the
    #       bodies

    # Total number of bodies
    nbody = len(body)
    # Panel numbers and indexing
    bodypanels = 2 * body["m"] * body["n"]  # Number of panels in each body
    bodypanelsn = body["n"]  # Number of spanwise panels in each body
    allpanelsn = np.sum(body["n"])  # Total number of spanwise body panels
    wakepanels = body["mw"] * body["n"]  # Number of panels in each wake
    allpanels = np.sum(bodypanels)  # Total number of body panels
    allpanelsw = np.sum(wakepanels)  # Total number of wake panels
    # Indices for assigning body-on-body influence coefficient matrices to assembled arrays
    inds = np.zeros(nbody + 1, dtype=int)
    inds[1 : nbody + 1] = np.cumsum(bodypanels)
    # Indices for assigning wake-on-body influence coefficient matrices to assembled arrays
    indsw = np.zeros(nbody + 1, dtype=int)
    indsw[1 : nbody + 1] = np.cumsum(wakepanels)
    # Indices for creating Kutta condition
    indsn = np.zeros(nbody + 1, dtype=int)
    indsn[1 : nbody + 1] = np.cumsum(bodypanelsn)

    # Obtain tp_allbodies data type
    _, _, tp_allbodies = SDPMdtypes()
    # Initialize struct array allbodies
    allbodies = np.zeros(1, dtype=tp_allbodies)
    # Assign panel numbers and indices. The rest of the information in
    # allbodies will be assigned by other functions.
    allbodies["nbody"][0] = nbody
    allbodies["bodypanels"][0] = bodypanels
    allbodies["bodypanelsn"][0] = bodypanelsn
    allbodies["allpanelsn"][0] = allpanelsn
    allbodies["wakepanels"][0] = wakepanels
    allbodies["allpanels"][0] = allpanels
    allbodies["allpanelsw"][0] = allpanelsw
    allbodies["inds"][0] = inds
    allbodies["indsw"][0] = indsw
    allbodies["indsn"][0] = indsn

    return allbodies


def PGtransform(body, beta):
    # Applies Prandtl-Glauert transformation to wing and wake panels
    # body: struct array containing the geometry of all the bodies in the flow.
    #       Each element of body describes a different wing, fairing or
    #       fuselage
    # beta: Subsonic compressibility factor

    # Obtain number of bodies
    nbody = len(body)
    # Apply Prandtl-Glauert transformation to wing and wake panels
    for i in range(0, nbody):
        # Body panel vertices
        body["Xp"][i] = body["Xp0"][i] / beta
        body["Yp"][i] = body["Yp0"][i]
        body["Zp"][i] = body["Zp0"][i]
        # Wake panel vertices
        if body["mw"][i] != 0:
            body["Xw"][i] = body["Xw0"][i] / beta
            body["Yw"][i] = body["Yw0"][i]
            body["Zw"][i] = body["Zw0"][i]
        # End if
        # Calculate control points, bound vortex ring vertices, normal vectors,
        # panel areas, panel flatness, lengths of spanwise and chordwise vortex
        # segments, midpoints on spanwise and chordwise vortex segments of
        # transformed body geometry
        (
            Xc,
            Yc,
            Zc,
            nx,
            ny,
            nz,
            tauxx,
            tauxy,
            tauxz,
            tauyx,
            tauyy,
            tauyz,
            s,
            cpln,
            sm,
            tmx,
            tmy,
            tmz,
            sn,
            tnx,
            tny,
            tnz,
        ) = SDPM_control_normal_tangential(
            body["Xp"][i], body["Yp"][i], body["Zp"][i], body["dir_tau"][i]
        )
        # Reshape transformed control point coordinate matrices into vectors
        Xcall = np.reshape(Xc, (2 * body["m"][i] * body["n"][i], 1), order="C")
        Ycall = np.reshape(Yc, (2 * body["m"][i] * body["n"][i], 1), order="C")
        Zcall = np.reshape(Zc, (2 * body["m"][i] * body["n"][i], 1), order="C")
        # Reshape transformed normal vector component matrices into vectors
        nxall = np.reshape(nx, (2 * body["m"][i] * body["n"][i], 1), order="C")
        nyall = np.reshape(ny, (2 * body["m"][i] * body["n"][i], 1), order="C")
        nzall = np.reshape(nz, (2 * body["m"][i] * body["n"][i], 1), order="C")
        # Assign data to body struct array
        body["Xc"][i] = Xc
        body["Yc"][i] = Yc
        body["Zc"][i] = Zc
        body["Xcall"][i] = Xcall
        body["Ycall"][i] = Ycall
        body["Zcall"][i] = Zcall
        body["nx"][i] = nx
        body["ny"][i] = ny
        body["nz"][i] = nz
        body["nxall"][i] = nxall
        body["nyall"][i] = nyall
        body["nzall"][i] = nzall
        body["tauxx"][i] = tauxx
        body["tauxy"][i] = tauxy
        body["tauxz"][i] = tauxz
        body["tauyx"][i] = tauyx
        body["tauyy"][i] = tauyy
        body["tauyz"][i] = tauyz
        body["s"][i] = s
        body["sm"][i] = sm
        body["tmx"][i] = tmx
        body["tmy"][i] = tmy
        body["tmz"][i] = tmz
        body["sn"][i] = sn
        body["tnx"][i] = tnx
        body["tny"][i] = tny
        body["tnz"][i] = tnz
        # Calculate control points, bound vortex ring vertices, normal vectors,
        # panel areas, panel flatness, lengths of spanwise and chordwise vortex
        # segments, midpoints on spanwise and chordwise vortex segments of
        # transformed wake geometry
        if body["mw"][i] != 0:
            (
                Xcw,
                Ycw,
                Zcw,
                nxw,
                nyw,
                nzw,
                tauxxw,
                tauxyw,
                tauxzw,
                tauyxw,
                tauyyw,
                tauyzw,
                sw,
                cplnw,
                smw,
                tmxw,
                tmyw,
                tmzw,
                snw,
                tnxw,
                tnyw,
                tnzw,
            ) = SDPM_control_normal_tangential(
                body["Xw"][i], body["Yw"][i], body["Zw"][i], body["dir_tau"][i]
            )
            # Assign data to body struct array
            body["Xcw"][i] = Xcw
            body["Ycw"][i] = Ycw
            body["Zcw"][i] = Zcw
            body["nxw"][i] = nxw
            body["nyw"][i] = nyw
            body["nzw"][i] = nzw
            body["tauxxw"][i] = tauxxw
            body["tauxyw"][i] = tauxyw
            body["tauxzw"][i] = tauxzw
            body["tauyxw"][i] = tauyxw
            body["tauyyw"][i] = tauyyw
            body["tauyzw"][i] = tauyzw
        # End if
    # End for
    return body


def normal_assemble(body, allbodies):
    # Concatenates panel normal vector components, areas and control point
    # coordinates for all bodies.
    # body: struct array containing the geometry of all the bodies in the flow.
    #       Each element of body describes a different wing, fairing or
    #       fuselage
    # allbodies: struct array containing concatenated information for all the
    #       bodies

    # Obtain number of bodies
    nbody = allbodies["nbody"][0]
    # Obtain total number of panels in all bodies
    allpanels = allbodies["allpanels"][0]
    # Obtain start and end indices of panels of each body
    inds = allbodies["inds"][0]
    # Initialize concatenated matrices
    nxall = np.zeros((allpanels, 1))
    nyall = np.zeros((allpanels, 1))
    nzall = np.zeros((allpanels, 1))
    nx0all = np.zeros((allpanels, 1))
    ny0all = np.zeros((allpanels, 1))
    nz0all = np.zeros((allpanels, 1))
    s0all = np.zeros((allpanels, 1))
    Xc0all = np.zeros((allpanels, 1))
    Yc0all = np.zeros((allpanels, 1))
    Zc0all = np.zeros((allpanels, 1))
    Xcall = np.zeros((allpanels, 1))
    Ycall = np.zeros((allpanels, 1))
    Zcall = np.zeros((allpanels, 1))
    # Cycle through all the bodies
    for i in range(0, nbody):
        # Panel normal vector components in Prandtl-Glauert coordinates
        nxall[inds[i] : inds[i + 1], 0] = np.ndarray.flatten(body["nxall"][i])
        nyall[inds[i] : inds[i + 1], 0] = np.ndarray.flatten(body["nyall"][i])
        nzall[inds[i] : inds[i + 1], 0] = np.ndarray.flatten(body["nzall"][i])
        # Panel normal vector components in Cartesian coordinates
        nx0all[inds[i] : inds[i + 1], 0] = np.ndarray.flatten(body["nx0all"][i])
        ny0all[inds[i] : inds[i + 1], 0] = np.ndarray.flatten(body["ny0all"][i])
        nz0all[inds[i] : inds[i + 1], 0] = np.ndarray.flatten(body["nz0all"][i])
        # Panel areas in Cartesian coordinates
        s0all[inds[i] : inds[i + 1], 0] = np.ndarray.flatten(body["s0all"][i])
        # Panel control point coordinates in Cartesian coordinates
        Xc0all[inds[i] : inds[i + 1], 0] = np.ndarray.flatten(body["Xc0all"][i])
        Yc0all[inds[i] : inds[i + 1], 0] = np.ndarray.flatten(body["Yc0all"][i])
        Zc0all[inds[i] : inds[i + 1], 0] = np.ndarray.flatten(body["Zc0all"][i])
        # Panel control point coordinates in Prandtl-Glauert coordinates
        Xcall[inds[i] : inds[i + 1], 0] = np.ndarray.flatten(body["Xcall"][i])
        Ycall[inds[i] : inds[i + 1], 0] = np.ndarray.flatten(body["Ycall"][i])
        Zcall[inds[i] : inds[i + 1], 0] = np.ndarray.flatten(body["Zcall"][i])
    # End for

    # Assign concatenated normal vectors, areas and control point coordinates
    # to struct array allbodies
    allbodies["nxall"][0] = nxall
    allbodies["nyall"][0] = nyall
    allbodies["nzall"][0] = nzall
    allbodies["nx0all"][0] = nx0all
    allbodies["ny0all"][0] = ny0all
    allbodies["nz0all"][0] = nz0all
    allbodies["s0all"][0] = s0all
    allbodies["Xc0all"][0] = Xc0all
    allbodies["Yc0all"][0] = Yc0all
    allbodies["Zc0all"][0] = Zc0all
    allbodies["Xcall"][0] = Xcall
    allbodies["Ycall"][0] = Ycall
    allbodies["Zcall"][0] = Zcall

    return allbodies


def modeshape_assemble(body, allbodies, nmodes):
    # Concatenates mode shapes for all bodies
    # body: struct array containing the geometry of all the bodies in the flow.
    #       Each element of body describes a different wing, fairing or
    #       fuselage
    # allbodies: struct array containing concatenated information for all the
    #       bodies
    # nmodes: Number of modes in the structural modal model

    # Obtain number of bodies
    nbody = allbodies["nbody"][0]
    # Obtain total number of panels in all bodies
    allpanels = allbodies["allpanels"][0]
    # Obtain start and end indices of panels of each body
    inds = allbodies["inds"][0]
    # Initialize global matrices
    Phi_xall = np.zeros((allpanels, nmodes))
    Phi_yall = np.zeros((allpanels, nmodes))
    Phi_zall = np.zeros((allpanels, nmodes))
    Phi_phiall = np.zeros((allpanels, nmodes))
    Phi_thetaall = np.zeros((allpanels, nmodes))
    Phi_psiall = np.zeros((allpanels, nmodes))
    for i in range(0, nbody):
        # Mode shapes
        for j in range(0, nmodes):
            Phi_xall[inds[i] : inds[i + 1], j] = body["Phi_xall"][i][:, j]
            Phi_yall[inds[i] : inds[i + 1], j] = body["Phi_yall"][i][:, j]
            Phi_zall[inds[i] : inds[i + 1], j] = body["Phi_zall"][i][:, j]
            Phi_phiall[inds[i] : inds[i + 1], j] = body["Phi_phiall"][i][:, j]
            Phi_thetaall[inds[i] : inds[i + 1], j] = body["Phi_thetaall"][i][:, j]
            Phi_psiall[inds[i] : inds[i + 1], j] = body["Phi_psiall"][i][:, j]
        # End for
    # End for

    # Assign concatenated mode shapes to struct array allbodies
    allbodies["Phi_xall"][0] = Phi_xall
    allbodies["Phi_yall"][0] = Phi_yall
    allbodies["Phi_zall"][0] = Phi_zall
    allbodies["Phi_phiall"][0] = Phi_phiall
    allbodies["Phi_thetaall"][0] = Phi_thetaall
    allbodies["Phi_psiall"][0] = Phi_psiall

    return allbodies


def SDPM_FD_matrices(m, n):
    # Creates finite difference matrices for the calculation of the flow
    # velocities on the surface from the values of the doublet strengths on the
    # surface.
    # m: Number of chordwise panels (there are m panels on the lower and m
    # panels on the upper surface for a total of 2*m panels)
    # n: Number of spanwise panels
    # Dm: Finite difference matrix in chordwise direction
    # Dn: Finite difference matrix in spanwise direction

    Dm = np.zeros((2 * m * n, 2 * m * n))
    # Calculate the elements of Dm using first order finite differences for all
    # trailing edge panels (lower and upper trailing edges)
    for i in range(0, n):
        Dm[i, i] = -1.0
        Dm[i, n + i] = 1.0
        Dm[(2 * m - 1) * n + i, (2 * m - 2) * n + i] = -1.0
        Dm[(2 * m - 1) * n + i, (2 * m - 1) * n + i] = 1.0
    # End for
    # Calculate the elements of Dm using second order finite differences
    # everywhere else
    for i in range(0, (2 * m - 2) * n):
        Dm[n + i, i] = -1.0
        Dm[n + i, 2 * n + i] = 1.0
    # End for
    # Initialize Dn finite difference matrix in equations 6.168
    Dn = np.zeros((2 * m * n, 2 * m * n))
    if n != 1:
        # Calculate the elements of Dn using first order finite differences at the
        # two wingtips
        for i in range(0, 2 * m):
            Dn[i * n, i * n] = -1.0
            Dn[i * n, 1 + i * n] = 1.0
            Dn[(i + 1) * n - 1, (i + 1) * n - 2] = -1.0
            Dn[(i + 1) * n - 1, (i + 1) * n - 1] = 1.0
        # End for
        # Calculate the elements of Dn using second order finite differences
        # everywhere else
        for i in range(0, 2 * m):
            for j in range(1, n - 1):
                Dn[i * n + j, i * n + j - 1] = -1.0
                Dn[i * n + j, i * n + j + 1] = 1.0
            # End for
        # End for
    # End if

    return Dm, Dn


def da1a2(body, i, Dm, Dn):
    # Evaluates the finite difference-related matrices and vectors for
    # calculating the perturbation flow velocities on the surface of bodies.
    # body: struct array containing the geometry of all the bodies in the flow.
    #       Each element of body describes a different wing, fairing or
    #       fuselage
    # i: index of current body
    # Dm: Chordwise finite difference matrix
    # Dn: Spanwise finite difference matrix
    # C12,C3: Finite difference-related matrices in the x direction
    # D12,D3: Finite difference-related matrices in the y direction
    # E12,E3: Finite difference-related matrices in the z direction

    # Obtain necessary data from body struct array
    m = body["m"][i]
    n = body["n"][i]
    nx = body["nxall"][i]
    ny = body["nyall"][i]
    nz = body["nzall"][i]
    tmx = np.reshape(body["tmx"][i], (2 * m * n, 1), order="C")
    tmy = np.reshape(body["tmy"][i], (2 * m * n, 1), order="C")
    tmz = np.reshape(body["tmz"][i], (2 * m * n, 1), order="C")
    sm = np.reshape(body["sm"][i], (2 * m * n, 1), order="C")
    tnx = np.reshape(body["tnx"][i], (2 * m * n, 1), order="C")
    tny = np.reshape(body["tny"][i], (2 * m * n, 1), order="C")
    tnz = np.reshape(body["tnz"][i], (2 * m * n, 1), order="C")
    sn = np.reshape(body["sn"][i], (2 * m * n, 1), order="C")
    # Calculate finite difference matrices
    if n > 1:
        d = (
            nx * tmy * tnz
            - nx * tmz * tny
            - ny * tmx * tnz
            + ny * tmz * tnx
            + nz * tmx * tny
            - nz * tmy * tnx
        )
        a1 = -(ny * tnz - nz * tny) / d
        a2 = (ny * tmz - nz * tmy) / d
        a3 = (tmy * tnz - tmz * tny) / d
        b1 = -(nx * tnz - nz * tnx) / d
        b2 = (nx * tmz - nz * tmx) / d
        b3 = (tmx * tnz - tmz * tnx) / d
        c1 = -(nx * tny - ny * tnx) / d
        c2 = (nx * tmy - ny * tmx) / d
        c3 = (tmx * tny - tmy * tnx) / d
    else:
        # Special case of only one row of panels
        d = tmx * ny - tmy * nx
        a1 = ny / d
        a2 = np.zeros((2 * m, n))
        a3 = -tmy / d
        b1 = -nx / d
        b2 = (nx * tmz - nz * tmx) / d
        b3 = tmx / d
        c1 = np.zeros((2 * m, n))
        c2 = np.zeros((2 * m, n))
        c3 = np.zeros((2 * m, n))
    # End if
    # Reshape all finite difference matrices into column vectors
    d = np.reshape(d, (2 * m * n, 1), order="C")
    a1 = np.reshape(a1, (2 * m * n, 1), order="C")
    a2 = np.reshape(a2, (2 * m * n, 1), order="C")
    a3 = np.reshape(a3, (2 * m * n, 1), order="C")
    b1 = np.reshape(b1, (2 * m * n, 1), order="C")
    b2 = np.reshape(b2, (2 * m * n, 1), order="C")
    b3 = np.reshape(b3, (2 * m * n, 1), order="C")
    c1 = np.reshape(c1, (2 * m * n, 1), order="C")
    c2 = np.reshape(c2, (2 * m * n, 1), order="C")
    c3 = np.reshape(c3, (2 * m * n, 1), order="C")
    # Calculate coefficients in expression for K(0) in equation 6.173
    C12 = a1 / sm * Dm + a2 / sn * Dn
    C3 = np.diag(a3.flatten())
    # For y velocities
    D12 = b1 / sm * Dm + b2 / sn * Dn
    D3 = np.diag(b3.flatten())
    # For z velocities
    E12 = c1 / sm * Dm + c2 / sn * Dn
    E3 = np.diag(c3.flatten())

    return d, a1, a2, a3, b1, b2, b3, c1, c2, c3, C12, C3, D12, D3, E12, E3


def FD_global(body, allbodies):
    # Sets up finite difference-related matrices and vectors for calculating
    # perturbation flow velocities on the surface of the bodies
    # body: struct array containing the geometry of all the bodies in the flow.
    #       Each element of body describes a different wing, fairing or
    #       fuselage
    # allbodies: struct array containing concatenated information for all the
    #       bodies
    # C12,C3: Finite difference-related matrices in the x direction
    # D12,D3: Finite difference-related matrices in the y direction
    # E12,E3: Finite difference-related matrices in the z direction

    # Obtain number of bodies
    nbody = allbodies["nbody"][0]
    # Obtain total number of panels in all bodies
    allpanels = allbodies["allpanels"][0]
    # Obtain start and end indices of panels of each body
    inds = allbodies["inds"][0]

    C12 = np.zeros((allpanels, allpanels))
    C3 = np.zeros((allpanels, allpanels))
    D12 = np.zeros((allpanels, allpanels))
    D3 = np.zeros((allpanels, allpanels))
    E12 = np.zeros((allpanels, allpanels))
    E3 = np.zeros((allpanels, allpanels))
    for i in range(0, nbody):
        Dm, Dn = SDPM_FD_matrices(body["m"][i], body["n"][i])
        (
            d,
            a1,
            a2,
            a3,
            b1,
            b2,
            b3,
            c1,
            c2,
            c3,
            C12dummy,
            C3dummy,
            D12dummy,
            D3dummy,
            E12dummy,
            E3dummy,
        ) = da1a2(body, i, Dm, Dn)
        # Assemble matrices C12, C3, D12, D3, E12, E3
        C12[inds[i] : inds[i + 1], inds[i] : inds[i + 1]] = C12dummy
        C3[inds[i] : inds[i + 1], inds[i] : inds[i + 1]] = C3dummy
        D12[inds[i] : inds[i + 1], inds[i] : inds[i + 1]] = D12dummy
        D3[inds[i] : inds[i + 1], inds[i] : inds[i + 1]] = D3dummy
        E12[inds[i] : inds[i + 1], inds[i] : inds[i + 1]] = E12dummy
        E3[inds[i] : inds[i + 1], inds[i] : inds[i + 1]] = E3dummy
    # End for

    # Assign finite difference matrices to struct array allbodies
    allbodies["C12"][0] = C12
    allbodies["C3"][0] = C3
    allbodies["D12"][0] = D12
    allbodies["D3"][0] = D3
    allbodies["E12"][0] = E12
    allbodies["E3"][0] = E3

    return allbodies


def steady_Kutta(body, allbodies):
    # Sets up the steady Kutta condition for all bodies
    # body: struct array containing the geometry of all the bodies in the flow.
    #       Each element of body describes a different wing, fairing or
    #       fuselage
    # allbodies: struct array containing concatenated information for all the
    #       bodies
    # Pc: Trailing edge panel selector matrix
    # Pe0: Panel wake strength steady exponential decay matrix

    # Obtain number of bodies
    nbody = allbodies["nbody"][0]
    # Obtain total number of panels in all bodies
    allpanels = allbodies["allpanels"][0]
    # Obtain total number of spanwise panels in all bodies
    allpanelsn = allbodies["allpanelsn"][0]
    # Obtain total number of panels in all wakes
    allpanelsw = allbodies["allpanelsw"][0]
    # Obtain start and end indices of panels of each body
    inds = allbodies["inds"][0]
    # Obtain spanwise start and end indices of panels of each body
    indsn = allbodies["indsn"][0]
    # Obtain start and end indices of panels of each wake
    indsw = allbodies["indsw"][0]

    # Initialize all matrices
    Pc = np.zeros((allpanelsn, allpanels))
    Pe0 = np.zeros((allpanelsw, allpanelsn))
    # Cycle through all the bodies
    for i in range(0, nbody):
        if body["mw"][i] != 0.0:
            # Calculate wing trailing edge panel selector matrix
            Pcdummy = np.concatenate(
                (
                    np.zeros((body["n"][i], (2 * body["m"][i] - 1) * body["n"][i])),
                    np.eye(body["n"][i]),
                ),
                axis=1,
            ) - np.concatenate(
                (
                    np.eye(body["n"][i]),
                    np.zeros((body["n"][i], (2 * body["m"][i] - 1) * body["n"][i])),
                ),
                axis=1,
            )
            Pc[indsn[i] : indsn[i + 1], inds[i] : inds[i + 1]] = Pcdummy
            # Calculate steady wake panel strength decay matrix
            Pe0dummy = np.matlib.repmat(np.eye(body["n"][i]), body["mw"][i], 1)
            Pe0[indsw[i] : indsw[i + 1], indsn[i] : indsn[i + 1]] = Pe0dummy
        # End if
    # End for

    # Assign wing trailing edge panel selector matrix to array allbodies
    allbodies["Pc"][0] = Pc

    return allbodies, Pe0


def unsteady_Kutta(body, allbodies, k):
    # Sets up the unsteady Kutta condition for all bodies
    # body: struct array containing the geometry of all the bodies in the flow.
    #       Each element of body describes a different wing, fairing or
    #       fuselage
    # allbodies: struct array containing concatenated information for all the
    #       bodies
    # k: Reduced frequency
    # Pe: Panel wake strength unsteady exponential decay matrix

    # Obtain number of bodies
    nbody = allbodies["nbody"][0]
    # Obtain total number of spanwise panels in all bodies
    allpanelsn = allbodies["allpanelsn"][0]
    # Obtain total number of panels in all wakes
    allpanelsw = allbodies["allpanelsw"][0]
    # Obtain spanwise start and end indices of panels of each body
    indsn = allbodies["indsn"][0]
    # Obtain start and end indices of panels of each wake
    indsw = allbodies["indsw"][0]

    Pe = np.zeros((allpanelsw, allpanelsn), dtype=complex)
    # Calculate matrix Pe(omega) in equation 5.223
    for i in range(0, nbody):
        dummy = np.exp(-1j * 2 * k / body["m"][i] * np.arange(1, body["mw"][i] + 1))
        dummy.shape = (dummy.size, 1)
        Pe[indsw[i] : indsw[i + 1], indsn[i] : indsn[i + 1]] = np.kron(
            dummy, np.eye(body["n"][i])
        )
    # End for
    return Pe


def steady_infcoef(body, allbodies):
    # Calculate steadys body panel influence coefficients on body control points
    # in transformed coordinates
    # body: struct array containing the geometry of all the bodies in the flow.
    #       Each element of body describes a different wing, fairing or
    #       fuselage
    # allbodies: struct array containing concatenated information for all the
    #       bodies
    # Aphi: Steady body-on-body source influence coefficients
    # Bphi: Steady body-on-body doublet influence coefficients
    # Cphi: Steady wake-on-body doublet influence coefficients

    # Load c function to calculate the steady SDPM influence coefficient
    # matrices
    sdpminf, _ = Cfuncs()
    # Obtain number of bodies
    nbody = allbodies["nbody"][0]
    # Obtain total number of panels in all bodies
    allpanels = allbodies["allpanels"][0]
    # Obtain total number of panels in all wakes
    allpanelsw = allbodies["allpanelsw"][0]
    # Obtain start and end indices of panels of each body
    inds = allbodies["inds"][0]
    # Obtain start and end indices of panels of each wake
    indsw = allbodies["indsw"][0]

    # Initialize body source influence coefficient matrix
    Aphi = np.zeros((allpanels, allpanels))
    # Initialize body doublet influence coefficient matrix
    Bphi = np.zeros((allpanels, allpanels))
    # Cycle through the bodies
    for i in range(0, nbody):
        for j in range(0, nbody):
            # Initialize source influence coefficient matrices
            Aphi_ij = np.zeros(
                (2 * body["m"][i] * body["n"][i], 2 * body["m"][j] * body["n"][j])
            )  # Source potential influence
            Au = np.zeros(
                (2 * body["m"][i] * body["n"][i], 2 * body["m"][j] * body["n"][j])
            )  # Source velocity influence in x direction
            Av = np.zeros(
                (2 * body["m"][i] * body["n"][i], 2 * body["m"][j] * body["n"][j])
            )  # Source velocity influence in y direction
            Aw = np.zeros(
                (2 * body["m"][i] * body["n"][i], 2 * body["m"][j] * body["n"][j])
            )  # Source velocity influence in z direction
            # Initialize doublet influence coefficient matrices
            Bphi_ij = np.zeros(
                (2 * body["m"][i] * body["n"][i], 2 * body["m"][j] * body["n"][j])
            )  # Doublet potential influence
            Bu = np.zeros(
                (2 * body["m"][i] * body["n"][i], 2 * body["m"][j] * body["n"][j])
            )  # Doublet velocity influence in x direction
            Bv = np.zeros(
                (2 * body["m"][i] * body["n"][i], 2 * body["m"][j] * body["n"][j])
            )  # Doublet velocity influence in y direction
            Bw = np.zeros(
                (2 * body["m"][i] * body["n"][i], 2 * body["m"][j] * body["n"][j])
            )  # Doublet velocity influence in z direction
            # Calculate all body influence coefficient matrices
            sdpminf(
                body["Xc"][i],
                body["Yc"][i],
                body["Zc"][i],
                body["Xp"][j],
                body["Yp"][j],
                body["Zp"][j],
                body["Xc"][j],
                body["Yc"][j],
                body["Zc"][j],
                body["nx"][j],
                body["ny"][j],
                body["nz"][j],
                body["tauxx"][j],
                body["tauxy"][j],
                body["tauxz"][j],
                body["tauyx"][j],
                body["tauyy"][j],
                body["tauyz"][j],
                2 * body["m"][i],
                body["n"][i],
                2 * body["m"][j],
                body["n"][j],
                Aphi_ij,
                Au,
                Av,
                Aw,
                Bphi_ij,
                Bu,
                Bv,
                Bw,
            )
            Aphi[inds[i] : inds[i + 1], inds[j] : inds[j + 1]] = Aphi_ij
            Bphi[inds[i] : inds[i + 1], inds[j] : inds[j + 1]] = Bphi_ij
        # End for
    # End for

    # Calculate steady wake panel influence coefficients on body control points
    # in transformed coordinates
    # Initialize wake doublet influence coefficient matrix
    Cphi = np.zeros((allpanels, allpanelsw))
    # Cycle through the bodies
    for i in range(0, nbody):
        for j in range(0, nbody):
            if body["mw"][j] != 0.0:
                # Initialize source influence coefficient matrices
                Aphiw_ij = np.zeros(
                    (2 * body["m"][i] * body["n"][i], body["mw"][j] * body["n"][j])
                )  # Source potential influence
                Auw = np.zeros(
                    (2 * body["m"][i] * body["n"][i], body["mw"][j] * body["n"][j])
                )  # Source velocity influence in x direction
                Avw = np.zeros(
                    (2 * body["m"][i] * body["n"][i], body["mw"][j] * body["n"][j])
                )  # Source velocity influence in y direction
                Aww = np.zeros(
                    (2 * body["m"][i] * body["n"][i], body["mw"][j] * body["n"][j])
                )  # Source velocity influence in z direction
                # Initialize doublet influence coefficient matrices
                Cphi_ij = np.zeros(
                    (2 * body["m"][i] * body["n"][i], body["mw"][j] * body["n"][j])
                )  # Doublet potential influence
                Cu = np.zeros(
                    (2 * body["m"][i] * body["n"][i], body["mw"][j] * body["n"][j])
                )  # Doublet velocity influence in x direction
                Cv = np.zeros(
                    (2 * body["m"][i] * body["n"][i], body["mw"][j] * body["n"][j])
                )  # Doublet velocity influence in y direction
                Cw = np.zeros(
                    (2 * body["m"][i] * body["n"][i], body["mw"][j] * body["n"][j])
                )  # Doublet velocity influence in z direction
                # Calculate all body influence coefficient matrices
                sdpminf(
                    body["Xc"][i],
                    body["Yc"][i],
                    body["Zc"][i],
                    body["Xw"][j],
                    body["Yw"][j],
                    body["Zw"][j],
                    body["Xcw"][j],
                    body["Ycw"][j],
                    body["Zcw"][j],
                    body["nxw"][j],
                    body["nyw"][j],
                    body["nzw"][j],
                    body["tauxxw"][j],
                    body["tauxyw"][j],
                    body["tauxzw"][j],
                    body["tauyxw"][j],
                    body["tauyyw"][j],
                    body["tauyzw"][j],
                    2 * body["m"][i],
                    body["n"][i],
                    body["mw"][j],
                    body["n"][j],
                    Aphiw_ij,
                    Auw,
                    Avw,
                    Aww,
                    Cphi_ij,
                    Cu,
                    Cv,
                    Cw,
                )
                Cphi[inds[i] : inds[i + 1], indsw[j] : indsw[j + 1]] = Cphi_ij
            # End if
    # End for
    # End for

    return Aphi, Bphi, Cphi


def unsteady_infcoef(body, allbodies, Omega, Mach, Aphi, Bphi, Cphi):
    # Calculates unsteady body and wake panel influence coefficients on body
    # control points in transformed coordinates
    # body: struct array containing the geometry of all the bodies in the flow.
    #       Each element of body describes a different wing, fairing or
    #       fuselage
    # allbodies: struct array containing concatenated information for all the
    #       bodies
    # Omega: Scaled frequency
    # Mach: Mach number
    # Aphi: Steady body-on-body source influence coefficients
    # Bphi: Steady body-on-body doublet influence coefficients
    # Cphi: Steady wake-on-body doublet influence coefficients
    # Abarphi: Unsteady body-on-body source influence coefficients
    # Bbarphi: Unsteady body-on-body doublet influence coefficients
    # Cbarphi: Unsteady wake-on-body doublet influence coefficients

    # Load c function to calculate the steady SDPM influence coefficient
    # matrices
    _, sdpminf_unsteady_subsonic = Cfuncs()
    # Obtain number of bodies
    nbody = allbodies["nbody"][0]
    # Obtain total number of panels in all bodies
    allpanels = allbodies["allpanels"][0]
    # Obtain total number of panels in all wakes
    allpanelsw = allbodies["allpanelsw"][0]
    # Obtain start and end indices of panels of each body
    inds = allbodies["inds"][0]
    # Obtain start and end indices of panels of each wake
    indsw = allbodies["indsw"][0]

    # Initialize body source influence coefficient matrix
    Abarphi = np.zeros((allpanels, allpanels), dtype=complex)
    # Initialize body doublet influence coefficient matrix
    Bbarphi = np.zeros((allpanels, allpanels), dtype=complex)
    # Initialize wkae doublet influence coefficient matrix
    Cbarphi = np.zeros((allpanels, allpanelsw), dtype=complex)
    # Cycle through the bodies
    for i in range(0, nbody):
        for j in range(0, nbody):
            Abarphi_real = np.zeros(
                (2 * body["m"][i] * body["n"][i], 2 * body["m"][j] * body["n"][j])
            )  # Initialize real part of unsteady source influence coefficient matrix
            Abarphi_imag = np.zeros(
                (2 * body["m"][i] * body["n"][i], 2 * body["m"][j] * body["n"][j])
            )  # Initialize imaginary part of unsteady source influence coefficient matrix
            Bbarphi_real = np.zeros(
                (2 * body["m"][i] * body["n"][i], 2 * body["m"][j] * body["n"][j])
            )  # Initialize real part of unsteady wing doublet influence coefficient matrix
            Bbarphi_imag = np.zeros(
                (2 * body["m"][i] * body["n"][i], 2 * body["m"][j] * body["n"][j])
            )  # Initialize imaginary part of unsteady wing doublet influence coefficient matrix
            Cbarphi_real = np.zeros(
                (2 * body["m"][i] * body["n"][i], body["mw"][j] * body["n"][j])
            )  # Initialize real part of unsteady wake doublet influence coefficient matrix
            Cbarphi_imag = np.zeros(
                (2 * body["m"][i] * body["n"][i], body["mw"][j] * body["n"][j])
            )  # Initialize imaginary part of unsteady wake doublet influence coefficient matrix
            params = np.array([Omega, Mach])  # Set Omega and Mach values
            # Obtain corresponding steady influence coefficient matrices
            Aphi_ij = np.ascontiguousarray(
                Aphi[inds[i] : inds[i + 1], inds[j] : inds[j + 1]]
            )
            Bphi_ij = np.ascontiguousarray(
                Bphi[inds[i] : inds[i + 1], inds[j] : inds[j + 1]]
            )
            Cphi_ij = np.ascontiguousarray(
                Cphi[inds[i] : inds[i + 1], indsw[j] : indsw[j + 1]]
            )
            # Calculate real and imaginary parts of all unsteady influence coefficient
            # matrices
            sdpminf_unsteady_subsonic(
                body["Xc"][i],
                body["Yc"][i],
                body["Zc"][i],
                body["Xc"][j],
                body["Yc"][j],
                body["Zc"][j],
                body["nx"][j],
                np.array(body["Xcw"][j] * 1.0),
                np.array(body["Ycw"][j] * 1.0),
                np.array(body["Zcw"][j] * 1.0),
                Aphi_ij,
                Bphi_ij,
                Cphi_ij,
                params,
                2 * body["m"][i],
                body["n"][i],
                2 * body["m"][j],
                body["n"][j],
                body["mw"][j],
                body["n"][j],
                Abarphi_real,
                Abarphi_imag,
                Bbarphi_real,
                Bbarphi_imag,
                Cbarphi_real,
                Cbarphi_imag,
            )
            # Calculate complex source influence coefficient matrices
            Abarphi[inds[i] : inds[i + 1], inds[j] : inds[j + 1]] = (
                Abarphi_real + 1j * Abarphi_imag
            )
            Bbarphi[inds[i] : inds[i + 1], inds[j] : inds[j + 1]] = (
                Bbarphi_real + 1j * Bbarphi_imag
            )
            Cbarphi[inds[i] : inds[i + 1], indsw[j] : indsw[j + 1]] = (
                Cbarphi_real + 1j * Cbarphi_imag
            )
        # End for
    # End for
    return Abarphi, Bbarphi, Cbarphi


def aeroforces(
    cp, nx0all, ny0all, nz0all, s0all, Xc0all, Yc0all, Zc0all, xf0, yf0, zf0
):
    # Calculates rigid body aerodynamic loads acting on all panels. The moments
    # are taken around point xf0,yf0,zf0
    Fx = -cp * nx0all * s0all  # Force in x direction
    Fy = -cp * ny0all * s0all  # Force in y direction
    Fz = -cp * nz0all * s0all  # Force in z direction
    Mx = (Yc0all - yf0) * Fz - (Zc0all - zf0) * Fy  # Rolling moment
    My = -(Xc0all - xf0) * Fz + (Zc0all - zf0) * Fx  # Pitching moment
    Mz = (Xc0all - xf0) * Fy - (Yc0all - yf0) * Fx  # Yawing moment

    return Fx, Fy, Fz, Mx, My, Mz


def steadysolve(body, allbodies, cp_order, Mach, beta, alpha0, beta0, xf0, yf0, zf0):
    # Calculates the steady aerodynamic pressure and loads acting on the
    # panel control points of the bodies described in struct array body.
    # body: struct array containing the geometry of all the bodies in the flow.
    #       Each element of body describes a different wing, fairing or
    #       fuselage
    # allbodies: struct array containing concatenated information for all the
    #       bodies
    # cp_order: Order of pressure calculation. cp_order=1: first order
    #       calculation. cp_order=2: second order calculation
    # Mach: Free stream Mach number
    # beta: Subsonic compressibility factor
    # alpha0: Free stream angle of attack
    # beta0: Free stream sideslip angle
    # Aphi: Steady body-on-body source influence coefficients
    # Bphi: Steady body-on-body doublet influence coefficients
    # Cphi: Steady wake-on-body doublet influence coefficients
    # barUinf: Component of non-dimensional free stream velocity in the x
    #       direction
    # barVinf: Component of non-dimensional free stream velocity in the y
    #       direction
    # barWinf: Component of non-dimensional free stream velocity in the z
    #       direction

    # Calculate non-dimensional free stream velocity
    barUinf = np.cos(alpha0) * np.cos(beta0)
    barVinf = -np.sin(beta0)
    barWinf = np.sin(alpha0) * np.cos(beta0)

    # Apply Prandtl-Glauert transformation to wing and wake panels
    body = PGtransform(body, beta)

    # Assemble normal vector components and areas for all bodies into global
    # matrices
    allbodies = normal_assemble(body, allbodies)

    # Finite difference-related matrices and vectors for calculating
    # perturbation flow velocities on the surface of the bodies
    allbodies = FD_global(body, allbodies)

    # Set up steady Kutta condition
    allbodies, Pe0 = steady_Kutta(body, allbodies)

    # Calculate steady body panel influence coefficients on body control points
    # in transformed coordinates
    Aphi, Bphi, Cphi = steady_infcoef(body, allbodies)

    # Set up Green's third identity of equation 6.89 for zero frequency
    K0 = linalg.solve(
        Bphi
        - np.eye(allbodies["allpanels"][0]) / 2.0
        + Cphi @ Pe0 @ allbodies["Pc"][0],
        Aphi,
    )
    Kx0 = -1 / beta * (allbodies["C12"][0] @ K0 - allbodies["C3"][0])
    Ky0 = allbodies["D12"][0] @ K0 - allbodies["D3"][0]
    Kz0 = -(allbodies["E12"][0] @ K0 - allbodies["E3"][0])

    # Non-dimensional normal derivative of the doublet strength
    barmun0 = -(
        barUinf * allbodies["nxall"][0] / beta
        + barVinf * allbodies["nyall"][0]
        + barWinf * allbodies["nzall"][0]
    )
    mu0 = -K0 @ barmun0
    muw0 = Pe0 @ allbodies["Pc"][0] @ barmun0

    # Zero frequency solution
    allbodies["barphix0"][0] = Kx0 @ barmun0
    allbodies["barphiy0"][0] = Ky0 @ barmun0
    allbodies["barphiz0"][0] = Kz0 @ barmun0
    # Add free stream to obtain total flow velocities on control points
    allbodies["baruc0"][0] = barUinf + allbodies["barphix0"][0]
    allbodies["barvc0"][0] = barVinf + allbodies["barphiy0"][0]
    allbodies["barwc0"][0] = barWinf + allbodies["barphiz0"][0]

    # Calculate steady pressure coefficient on control points
    if cp_order == 1:
        # Linear pressure calculation
        cp0 = -2.0 * allbodies["barphix0"][0]
    else:
        # Second order pressure calculation
        cp0 = (
            1
            - allbodies["baruc0"][0] ** 2
            - allbodies["barvc0"][0] ** 2
            - allbodies["barwc0"][0] ** 2
            + Mach**2 * allbodies["barphix0"][0] ** 2
        )
    # End if

    # Calculate steady aerodynamic loads on the panels
    Fx0, Fy0, Fz0, Mx0, My0, Mz0 = aeroforces(
        cp0,
        allbodies["nx0all"][0],
        allbodies["ny0all"][0],
        allbodies["nz0all"][0],
        allbodies["s0all"][0],
        allbodies["Xc0all"][0],
        allbodies["Yc0all"][0],
        allbodies["Zc0all"][0],
        xf0,
        yf0,
        zf0,
    )

    # Assign concatenated steady pressure coefficient and aerodynamic loads to
    # struct array allbodies
    allbodies["cp0"][0] = cp0
    allbodies["Fx0"][0] = Fx0
    allbodies["Fy0"][0] = Fy0
    allbodies["Fz0"][0] = Fz0
    allbodies["Mx0"][0] = Mx0
    allbodies["My0"][0] = My0
    allbodies["Mz0"][0] = Mz0

    # Assign steady pressure coefficient and aerodynamic loads to respective
    # elements of struct array body
    for i in range(0, allbodies["nbody"][0]):
        body["cp0"][i] = np.reshape(
            cp0[allbodies["inds"][0][i] : allbodies["inds"][0][i + 1], 0],
            (2 * body["m"][i], body["n"][i]),
            order="C",
        )
        body["mu0"][i] = np.reshape(
            mu0[allbodies["inds"][0][i] : allbodies["inds"][0][i + 1], 0],
            (2 * body["m"][i], body["n"][i]),
            order="C",
        )
        body["muw0"][i] = np.reshape(
            muw0[allbodies["indsw"][0][i] : allbodies["indsw"][0][i + 1], 0],
            (body["mw"][i], body["n"][i]),
            order="C",
        )
        body["Fx0"][i] = np.reshape(
            Fx0[allbodies["inds"][0][i] : allbodies["inds"][0][i + 1], 0],
            (2 * body["m"][i], body["n"][i]),
            order="C",
        )
        body["Fy0"][i] = np.reshape(
            Fy0[allbodies["inds"][0][i] : allbodies["inds"][0][i + 1], 0],
            (2 * body["m"][i], body["n"][i]),
            order="C",
        )
        body["Fz0"][i] = np.reshape(
            Fz0[allbodies["inds"][0][i] : allbodies["inds"][0][i + 1], 0],
            (2 * body["m"][i], body["n"][i]),
            order="C",
        )
        body["Mx0"][i] = np.reshape(
            Mx0[allbodies["inds"][0][i] : allbodies["inds"][0][i + 1], 0],
            (2 * body["m"][i], body["n"][i]),
            order="C",
        )
        body["My0"][i] = np.reshape(
            My0[allbodies["inds"][0][i] : allbodies["inds"][0][i + 1], 0],
            (2 * body["m"][i], body["n"][i]),
            order="C",
        )
        body["Mz0"][i] = np.reshape(
            Mz0[allbodies["inds"][0][i] : allbodies["inds"][0][i + 1], 0],
            (2 * body["m"][i], body["n"][i]),
            order="C",
        )
    # End if

    return body, allbodies, Aphi, Bphi, Cphi, barUinf, barVinf, barWinf


def unsteadysolve_flex(
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
):
    # Calculates the steady aerodynamic pressure and loads acting on the
    # panel control points of the bodies described in struct array body. The
    # motion of the bodies is flexible and parallel to pre-defined mode shapes.
    # This function is part of the SDPMflut Matlab distribution.
    # body: struct array containing the geometry of all the bodies in the flow.
    #       Each element of body describes a different wing, fairing or
    #       fuselage
    # allbodies: struct array containing concatenated information for all the
    #       bodies
    # Aphi: Steady body-on-body source influence coefficients
    # Bphi: Steady body-on-body doublet influence coefficients
    # Cphi: Steady wake-on-body doublet influence coefficients
    # barUinf: Component of non-dimensional free stream velocity in the x
    #       direction
    # barVinf: Component of non-dimensional free stream velocity in the y
    #       direction
    # barWinf: Component of non-dimensional free stream velocity in the z
    #       direction
    # k: Reduced frequency
    # c0: Characteristic chord length
    # Mach: Free stream Mach number
    # beta: Subsonic compressibility factor
    # cp_order: Order of pressure calculation. cp_order=1: first order
    #       calculation. cp_order=2: second order calculation
    # cp1: Total pressure coefficient per generalized coordinate acting on the
    #       control points of all bodies in the flow
    # cp_0: Stiffness pressure coefficient per generalized coordinate acting on
    #       the control points of all bodies in the flow
    # cp_1: Damping pressure coefficient per generalized coordinate acting on
    #       the control points of all bodies in the flow
    # cp_2: Mass pressure coefficient per generalized coordinate acting on the
    #       control points of all bodies in the flow

    # Calculate scaled frequency in equation 6.65
    Omega = 2.0 * k * Mach / c0 / beta

    # Set up unsteady Kutta condition
    Pe = unsteady_Kutta(body, allbodies, k)

    # Calculate unsteady influence coefficient matrices
    Abarphi, Bbarphi, Cbarphi = unsteady_infcoef(
        body, allbodies, Omega, Mach, Aphi, Bphi, Cphi
    )

    # Calculate K(omega) from equations 6.178
    K = linalg.solve(
        1j * Omega * Mach * Abarphi * allbodies["nxall"][0]
        + Bbarphi
        - np.eye(allbodies["allpanels"][0]) / 2.0
        + Cbarphi @ Pe @ allbodies["Pc"][0],
        Abarphi,
    )  # Dimensions are meters

    # Calculate Kx, Ky and Kz matrices
    Kx = -1 / beta * (allbodies["C12"][0] @ K - allbodies["C3"][0])
    Ky = allbodies["D12"][0] @ K - allbodies["D3"][0]
    Kz = -(allbodies["E12"][0] @ K - allbodies["E3"][0])

    if cp_order == 1:
        # Linear pressure calculation
        # Calculate pressure derivatives with respect to modes of vibration
        # Displacements
        cpphi = (
            2.0
            * Kx
            @ (
                barWinf * allbodies["Phi_phiall"][0] * allbodies["nyall"][0]
                - barVinf * allbodies["Phi_phiall"][0] * allbodies["nzall"][0]
            )
        )
        cptheta = (
            2.0
            * Kx
            @ (
                -barWinf * allbodies["Phi_thetaall"][0] * allbodies["nxall"][0] / beta
                + barUinf * allbodies["Phi_thetaall"][0] * allbodies["nzall"][0]
            )
        )
        cppsi = (
            2.0
            * Kx
            @ (
                barVinf * allbodies["Phi_psiall"][0] * allbodies["nxall"][0]
                - barUinf * allbodies["Phi_psiall"][0] * allbodies["nyall"][0]
            )
        )
        # Velocities
        cpxdot = (
            -2.0
            * Kx
            @ ((2.0 / c0) * allbodies["Phi_xall"][0] * allbodies["nxall"][0] / beta)
        )
        cpydot = (
            -2.0 * Kx @ ((2.0 / c0) * allbodies["Phi_yall"][0] * allbodies["nyall"][0])
        )
        cpzdot = (
            -2.0 * Kx @ ((2.0 / c0) * allbodies["Phi_zall"][0] * allbodies["nzall"][0])
        )
        cpphidot = (
            -4.0
            / c0
            * K
            @ (
                barWinf * allbodies["Phi_phiall"][0] * allbodies["nyall"][0]
                - barVinf * allbodies["Phi_phiall"][0] * allbodies["nzall"][0]
            )
        )
        cpthetadot = (
            -4.0
            / c0
            * K
            @ (
                -barWinf * allbodies["Phi_thetaall"][0] * allbodies["nxall"][0] / beta
                + barUinf * allbodies["Phi_thetaall"][0] * allbodies["nzall"][0]
            )
        )
        cppsidot = (
            -4
            / c0
            * K
            @ (
                barVinf * allbodies["Phi_psiall"][0] * allbodies["nxall"][0] / beta
                - barUinf * allbodies["Phi_psiall"][0] * allbodies["nyall"][0]
            )
        )
        # Accelerations
        cpx2dot = (
            8.0
            / c0**2.0
            * K
            @ (allbodies["Phi_xall"][0] * allbodies["nxall"][0] / beta)
        )
        cpy2dot = 8.0 / c0**2.0 * K @ (allbodies["Phi_yall"][0] * allbodies["nyall"][0])
        cpz2dot = 8.0 / c0**2.0 * K @ (allbodies["Phi_zall"][0] * allbodies["nzall"][0])
    else:
        # Pressure coefficient matrices
        barC0 = (
            2.0 * Mach**2.0 * Kx * allbodies["barphix0"][0]
            - 2.0 * Kx * allbodies["baruc0"][0]
            - 2.0 * Ky * allbodies["barvc0"][0]
            - 2.0 * Kz * allbodies["barwc0"][0]
        )
        barC1 = 2.0 * K - 2 * Mach**2.0 * K * allbodies["barphix0"][0]
        # Calculate pressure derivatives with respect to modes of vibration
        # Displacements
        cpphi = (
            -barWinf * barC0 @ (allbodies["Phi_phiall"][0] * allbodies["nyall"][0])
            - 2 * barWinf * allbodies["Phi_phiall"][0] * allbodies["barvc0"][0]
            + barVinf * barC0 @ (allbodies["Phi_phiall"][0] * allbodies["nzall"][0])
            + 2 * barVinf * allbodies["Phi_phiall"][0] * allbodies["barwc0"][0]
        )
        cptheta = (
            barWinf
            / beta
            * barC0
            @ (allbodies["Phi_thetaall"][0] * allbodies["nxall"][0])
            + 2 * barWinf * allbodies["Phi_thetaall"][0] * allbodies["baruc0"][0]
            - barUinf * barC0 @ (allbodies["Phi_thetaall"][0] * allbodies["nzall"][0])
            - 2 * barUinf * allbodies["Phi_thetaall"][0] * allbodies["barwc0"][0]
        )
        cppsi = (
            -barVinf
            / beta
            * barC0
            @ (allbodies["Phi_psiall"][0] * allbodies["nxall"][0])
            - 2 * barVinf * allbodies["Phi_psiall"][0] * allbodies["baruc0"][0]
            + barUinf * barC0 @ (allbodies["Phi_psiall"][0] * allbodies["nyall"][0])
            + 2 * barUinf * allbodies["Phi_psiall"][0] * allbodies["barvc0"][0]
        )
        # Velocities
        cpxdot = (
            2.0
            / c0
            * (
                1 / beta * barC0 @ (allbodies["Phi_xall"][0] * allbodies["nxall"][0])
                + 2 * allbodies["Phi_xall"][0] * allbodies["baruc0"][0]
            )
        )
        cpydot = (
            2.0
            / c0
            * (
                barC0 @ (allbodies["Phi_yall"][0] * allbodies["nyall"][0])
                + 2 * allbodies["Phi_yall"][0] * allbodies["barvc0"][0]
            )
        )
        cpzdot = (
            2.0
            / c0
            * (
                barC0 @ (allbodies["Phi_zall"][0] * allbodies["nzall"][0])
                + 2 * allbodies["Phi_zall"][0] * allbodies["barwc0"][0]
            )
        )
        cpphidot = (
            2.0
            / c0
            * (
                -barWinf * barC1 @ (allbodies["Phi_phiall"][0] * allbodies["nyall"][0])
                + barVinf * barC1 @ (allbodies["Phi_phiall"][0] * allbodies["nzall"][0])
            )
        )
        cpthetadot = (
            2.0
            / c0
            * (
                barWinf
                / beta
                * barC1
                @ (allbodies["Phi_thetaall"][0] * allbodies["nxall"][0])
                - barUinf
                * barC1
                @ (allbodies["Phi_thetaall"][0] * allbodies["nzall"][0])
            )
        )
        cppsidot = (
            2.0
            / c0
            * (
                -barVinf
                / beta
                * barC1
                @ (allbodies["Phi_psiall"][0] * allbodies["nxall"][0])
                + barUinf * barC1 @ (allbodies["Phi_psiall"][0] * allbodies["nyall"][0])
            )
        )
        # Accelerations
        cpx2dot = (
            4.0
            / (c0**2.0 * beta)
            * barC1
            @ (allbodies["Phi_xall"][0] * allbodies["nxall"][0])
        )
        cpy2dot = (
            4.0 / c0**2.0 * barC1 @ (allbodies["Phi_yall"][0] * allbodies["nyall"][0])
        )
        cpz2dot = (
            4.0 / c0**2.0 * barC1 @ (allbodies["Phi_zall"][0] * allbodies["nzall"][0])
        )
    # End if

    # Calculate oscillatory pressure components
    cp_0 = cpphi + cptheta + cppsi  # Displacement component
    cp_1 = (
        cpxdot + cpydot + cpzdot + cpphidot + cpthetadot + cppsidot
    )  # Velocity component
    cp_2 = cpx2dot + cpy2dot + cpz2dot  # Acceleration component
    # Calculate total oscillatory pressure
    cp1 = cp_0 + (1j * k) * cp_1 + (1j * k) ** 2 * cp_2

    return cp1, cp_0, cp_1, cp_2


def unsteadysolve_pitchplunge(
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
    xf,
    yf,
    zf,
):
    # Calculates the steady aerodynamic pressure and loads acting on the
    # panel control points of the bodies described in struct array body. The
    # motion of the bodies is rigid pitch and plunge.
    # body: struct array containing the geometry of all the bodies in the flow.
    #       Each element of body describes a different wing, fairing or
    #       fuselage
    # allbodies: struct array containing concatenated information for all the
    #       bodies
    # Aphi: Steady body-on-body source influence coefficients
    # Bphi: Steady body-on-body doublet influence coefficients
    # Cphi: Steady wake-on-body doublet influence coefficients
    # barUinf: Component of non-dimensional free stream velocity in the x
    #       direction
    # barVinf: Component of non-dimensional free stream velocity in the y
    #       direction
    # barWinf: Component of non-dimensional free stream velocity in the z
    #       direction
    # k: Reduced frequency
    # c0: Characteristic chord length
    # Mach: Free stream Mach number
    # beta: Subsonic compressibility factor
    # cp_order: Order of pressure calculation. cp_order=1: first order
    #       calculation. cp_order=2: second order calculation
    # xf,yf,zf: Position of pitch axis in Prandtl-Glauert coordinates
    # cpalpha: Pressure derivative with respect to pitch
    # cphdot: Pressure derivative with respect to plunge velocity
    # cpalphadot: Pressure derivative with respect to pitch velocity
    # cph2dot: Pressure derivative with respect to plunge acceleration
    # cpalpha2dot: Pressure derivative with respect to pitch acceleration

    # Calculate scaled frequency in equation 6.65
    Omega = 2.0 * k * Mach / c0 / beta

    # Set up unsteady Kutta condition
    Pe = unsteady_Kutta(body, allbodies, k)

    # Calculate unsteady influence coefficient matrices
    Abarphi, Bbarphi, Cbarphi = unsteady_infcoef(
        body, allbodies, Omega, Mach, Aphi, Bphi, Cphi
    )

    # Calculate K(omega) from equations 6.178
    K = linalg.solve(
        1j * Omega * Mach * Abarphi * allbodies["nxall"][0]
        + Bbarphi
        - np.eye(allbodies["allpanels"][0]) / 2.0
        + Cbarphi @ Pe @ allbodies["Pc"][0],
        Abarphi,
    )  # Dimensions are meters

    # Calculate Kx, Ky and Kz matrices
    Kx = -1 / beta * (allbodies["C12"][0] @ K - allbodies["C3"][0])
    Ky = allbodies["D12"][0] @ K - allbodies["D3"][0]
    Kz = -(allbodies["E12"][0] @ K - allbodies["E3"][0])

    if cp_order == 1:
        # First order pressure calculation
        # Calculate pressure derivatives with respect to degrees of freedom
        # Displacements
        cpalpha = (
            -2.0 * barWinf / beta * Kx @ allbodies["nxall"][0]
            + 2.0 * barUinf * Kx @ allbodies["nzall"][0]
        )
        # Velocities
        cphdot = 4.0 / c0 * Kx @ allbodies["nzall"][0]
        cpalphadot = (
            -4.0
            / c0
            / beta
            * Kx
            @ (allbodies["nxall"][0] * (allbodies["Zcall"][0] - zf))
            + 4.0 / c0 * Kx @ (allbodies["nzall"][0] * (allbodies["Xcall"][0] - xf))
            + 4.0 * barWinf / c0 / beta * K @ allbodies["nxall"][0]
            - 4.0 * barUinf / c0 * K @ allbodies["nzall"][0]
        )
        # Accelerations
        cph2dot = -8.0 / c0**2 * K @ allbodies["nzall"][0]
        cpalpha2dot = 8.0 / c0**2 / beta * K @ (
            allbodies["nxall"][0] * (allbodies["Zcall"][0] - zf)
        ) - 8.0 / c0**2 * K @ (allbodies["nzall"][0] * (allbodies["Xcall"][0] - xf))
    else:
        # Pressure coefficient matrices
        barC0 = (
            2.0 * Mach**2.0 * Kx * allbodies["barphix0"][0]
            - 2.0 * Kx * allbodies["baruc0"][0]
            - 2.0 * Ky * allbodies["barvc0"][0]
            - 2.0 * Kz * allbodies["barwc0"][0]
        )
        barC1 = 2.0 * K - 2.0 * Mach**2.0 * K * allbodies["barphix0"][0]
        # Calculate pressure derivatives with respect to degrees of freedom
        # Displacements
        cpalpha = barWinf * (
            1 / beta * barC0 @ allbodies["nxall"][0] + 2 * allbodies["baruc0"][0]
        ) - barUinf * (barC0 @ allbodies["nzall"][0] + 2 * allbodies["barwc0"][0])
        # Velocities
        cphdot = (
            -2.0 / c0 * (barC0 @ allbodies["nzall"][0] + 2 * allbodies["barwc0"][0])
        )
        cpalphadot = (
            2.0
            / c0
            * (
                1.0
                / beta
                * barC0
                @ (allbodies["nxall"][0] * (allbodies["Zcall"][0] - zf))
                - barC0 @ (allbodies["nzall"][0] * (allbodies["Xcall"][0] - xf))
                - barUinf * barC1 @ allbodies["nzall"][0]
                + 2.0 * allbodies["baruc0"][0] * (allbodies["Zcall"][0] - zf)
                - 2 * allbodies["barwc0"][0] * (allbodies["Xcall"][0] - xf)
            )
        )
        # Accelerations
        cph2dot = -((2.0 / c0) ** 2.0) * barC1 @ allbodies["nzall"][0]
        cpalpha2dot = (2.0 / c0) ** 2.0 * (
            1.0 / beta * barC1 @ (allbodies["nxall"][0] * (allbodies["Zcall"][0] - zf))
            - barC1 @ (allbodies["nzall"][0] * (allbodies["Xcall"][0] - xf))
        )
    # End if

    return cpalpha, cphdot, cpalphadot, cph2dot, cpalpha2dot


def aerostabderiv(
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
    xf,
    yf,
    zf,
    Sref,
    bref,
    cref,
):
    # Calculates the steady aerodynamic pressure and loads acting on the
    # panel control points of the bodies described in struct array body. The
    # motion of the bodies is rigid pitch and plunge.
    # body: struct array containing the geometry of all the bodies in the flow.
    #       Each element of body describes a different wing, fairing or
    #       fuselage
    # allbodies: struct array containing concatenated information for all the
    #       bodies
    # Aphi: Steady body-on-body source influence coefficients
    # Bphi: Steady body-on-body doublet influence coefficients
    # Cphi: Steady wake-on-body doublet influence coefficients
    # barUinf: Component of non-dimensional free stream velocity in the x
    #       direction
    # barVinf: Component of non-dimensional free stream velocity in the y
    #       direction
    # barWinf: Component of non-dimensional free stream velocity in the z
    #       direction
    # k: Reduced frequency
    # c0: Root chord length
    # Mach: Free stream Mach number
    # beta: Subsonic compressibility factor
    # cp_order: Order of pressure calculation. cp_order=1: first order
    #       calculation. cp_order=2: second order calculation
    # xf,yf,zf: Position of pitch axis in Prandtl-Glauert coordinates
    # Sref: Reference planform area
    # bref: Reference span length
    # cref: Reference chord length
    # stabder: Struct array containing the values of the longitudinal and
    #       lateral stability derivatives

    # Calculate scaled frequency in equation 6.65
    Omega = 2.0 * k * Mach / c0 / beta

    # Set up unsteady Kutta condition
    Pe = unsteady_Kutta(body, allbodies, k)

    # Calculate unsteady influence coefficient matrices
    Abarphi, Bbarphi, Cbarphi = unsteady_infcoef(
        body, allbodies, Omega, Mach, Aphi, Bphi, Cphi
    )

    # Calculate K(omega) from equations 6.178
    K = linalg.solve(
        1j * Omega * Mach * Abarphi * allbodies["nxall"][0]
        + Bbarphi
        - np.eye(allbodies["allpanels"][0]) / 2.0
        + Cbarphi @ Pe @ allbodies["Pc"][0],
        Abarphi,
    )  # Dimensions are meters

    # Calculate Kx, Ky and Kz matrices
    Kx = -1 / beta * (allbodies["C12"][0] @ K - allbodies["C3"][0])
    Ky = allbodies["D12"][0] @ K - allbodies["D3"][0]
    Kz = -(allbodies["E12"][0] @ K - allbodies["E3"][0])

    # Calculate distances from centre of rotation
    Xc = allbodies["Xc0all"][0] - xf
    Yc = allbodies["Yc0all"][0] - yf
    Zc = allbodies["Zc0all"][0] - zf

    if cp_order == 1:
        print("First order aerodynamic stability derivatives not coded yet")
    else:
        # Pressure coefficient matrices
        barC0 = (
            2.0 * Mach**2.0 * Kx * allbodies["barphix0"][0]
            - 2.0 * Kx * allbodies["baruc0"][0]
            - 2.0 * Ky * allbodies["barvc0"][0]
            - 2.0 * Kz * allbodies["barwc0"][0]
        )
        barC1 = 2.0 * K - 2.0 * Mach**2.0 * K * allbodies["barphix0"][0]
        # Calculate pressure derivatives with respect to degrees of freedom
        # Displacements
        cpphi = -barWinf * (
            barC0 @ allbodies["nyall"][0] + 2.0 * allbodies["barvc0"][0]
        ) + barVinf * (barC0 @ allbodies["nzall"][0] + 2.0 * allbodies["barwc0"][0])
        cptheta = barWinf * (
            1 / beta * barC0 @ allbodies["nxall"][0] + 2.0 * allbodies["baruc0"][0]
        ) - barUinf * (barC0 @ allbodies["nzall"][0] + 2.0 * allbodies["barwc0"][0])
        cppsi = -barVinf * (
            1 / beta * barC0 @ allbodies["nxall"][0] + 2.0 * allbodies["baruc0"][0]
        ) + barUinf * (barC0 @ allbodies["nyall"][0] + 2.0 * allbodies["barvc0"][0])
        # Velocities
        cpu = 1.0 / beta * barC0 @ allbodies["nxall"][0] + 2.0 * allbodies["baruc0"][0]
        cpv = barC0 @ allbodies["nyall"][0] + 2.0 * allbodies["barvc0"][0]
        cpw = barC0 @ allbodies["nzall"][0] + 2.0 * allbodies["barwc0"][0]
        cpp = (2.0 / bref) * (
            -barC0 @ (allbodies["nyall"][0] * Zc)
            - 2.0 * allbodies["barvc0"][0] * Zc
            + barC0 @ (allbodies["nzall"][0] * Yc)
            + 2.0 * allbodies["barwc0"][0] * Yc
            - barWinf * barC1 @ allbodies["nyall"][0]
            + barVinf * barC1 @ allbodies["nzall"][0]
        )
        cpq = (2.0 / c0) * (
            1.0 / beta * barC0 @ (allbodies["nxall"][0] * Zc)
            + 2.0 * allbodies["baruc0"][0] * Zc
            - barC0 @ (allbodies["nzall"][0] * Xc)
            - 2.0 * allbodies["barwc0"][0] * Xc
            + barWinf / beta * barC1 @ allbodies["nxall"][0]
            - barUinf * barC1 @ allbodies["nzall"][0]
        )
        cpr = (2.0 / bref) * (
            -1.0 / beta * barC0 @ (allbodies["nxall"][0] * Yc)
            - 2.0 * allbodies["baruc0"][0] * Yc
            + barC0 @ (allbodies["nyall"][0] * Xc)
            + 2.0 * allbodies["barvc0"][0] * Xc
            - barVinf / beta * barC1 @ allbodies["nxall"][0]
            + barUinf * barC1 @ allbodies["nyall"][0]
        )
        # Accelerations
        cpudot = 2.0 / c0 / beta * barC1 @ allbodies["nxall"][0]
        cpvdot = 2.0 / bref * barC1 @ allbodies["nyall"][0]
        cpwdot = 2.0 / c0 * barC1 @ allbodies["nzall"][0]
        cppdot = (2.0 / bref) ** 2 * (
            -barC1 @ (allbodies["nyall"][0] * Zc) + barC1 @ (allbodies["nzall"][0] * Yc)
        )
        cpqdot = (2.0 / c0) ** 2 * (
            1 / beta * barC1 @ (allbodies["nxall"][0] * Yc)
            - barC1 @ (allbodies["nzall"][0] * Xc)
        )
        cprdot = (2.0 / bref) ** 2 * (
            -1 / beta * barC1 @ (allbodies["nxall"][0] * Yc)
            + barC1 @ (allbodies["nyall"][0] * Xc)
        )
    # End if

    # Calculate aerodynamic load derivatives on the panels
    CXphi, CYphi, CZphi, Clphi, Cmphi, Cnphi = aeroforces(
        cpphi,
        allbodies["nx0all"][0],
        allbodies["ny0all"][0],
        allbodies["nz0all"][0],
        allbodies["s0all"][0],
        allbodies["Xc0all"][0],
        allbodies["Yc0all"][0],
        allbodies["Zc0all"][0],
        xf,
        yf,
        zf,
    )
    CXtheta, CYtheta, CZtheta, Cltheta, Cmtheta, Cntheta = aeroforces(
        cptheta,
        allbodies["nx0all"][0],
        allbodies["ny0all"][0],
        allbodies["nz0all"][0],
        allbodies["s0all"][0],
        allbodies["Xc0all"][0],
        allbodies["Yc0all"][0],
        allbodies["Zc0all"][0],
        xf,
        yf,
        zf,
    )
    CXpsi, CYpsi, CZpsi, Clpsi, Cmpsi, Cnpsi = aeroforces(
        cppsi,
        allbodies["nx0all"][0],
        allbodies["ny0all"][0],
        allbodies["nz0all"][0],
        allbodies["s0all"][0],
        allbodies["Xc0all"][0],
        allbodies["Yc0all"][0],
        allbodies["Zc0all"][0],
        xf,
        yf,
        zf,
    )
    CXu, CYu, CZu, Clu, Cmu, Cnu = aeroforces(
        cpu,
        allbodies["nx0all"][0],
        allbodies["ny0all"][0],
        allbodies["nz0all"][0],
        allbodies["s0all"][0],
        allbodies["Xc0all"][0],
        allbodies["Yc0all"][0],
        allbodies["Zc0all"][0],
        xf,
        yf,
        zf,
    )
    CXv, CYv, CZv, Clv, Cmv, Cnv = aeroforces(
        cpv,
        allbodies["nx0all"][0],
        allbodies["ny0all"][0],
        allbodies["nz0all"][0],
        allbodies["s0all"][0],
        allbodies["Xc0all"][0],
        allbodies["Yc0all"][0],
        allbodies["Zc0all"][0],
        xf,
        yf,
        zf,
    )
    CXw, CYw, CZw, Clw, Cmw, Cnw = aeroforces(
        cpw,
        allbodies["nx0all"][0],
        allbodies["ny0all"][0],
        allbodies["nz0all"][0],
        allbodies["s0all"][0],
        allbodies["Xc0all"][0],
        allbodies["Yc0all"][0],
        allbodies["Zc0all"][0],
        xf,
        yf,
        zf,
    )
    CXp, CYp, CZp, Clp, Cmp, Cnp = aeroforces(
        cpp,
        allbodies["nx0all"][0],
        allbodies["ny0all"][0],
        allbodies["nz0all"][0],
        allbodies["s0all"][0],
        allbodies["Xc0all"][0],
        allbodies["Yc0all"][0],
        allbodies["Zc0all"][0],
        xf,
        yf,
        zf,
    )
    CXq, CYq, CZq, Clq, Cmq, Cnq = aeroforces(
        cpq,
        allbodies["nx0all"][0],
        allbodies["ny0all"][0],
        allbodies["nz0all"][0],
        allbodies["s0all"][0],
        allbodies["Xc0all"][0],
        allbodies["Yc0all"][0],
        allbodies["Zc0all"][0],
        xf,
        yf,
        zf,
    )
    CXr, CYr, CZr, Clr, Cmr, Cnr = aeroforces(
        cpr,
        allbodies["nx0all"][0],
        allbodies["ny0all"][0],
        allbodies["nz0all"][0],
        allbodies["s0all"][0],
        allbodies["Xc0all"][0],
        allbodies["Yc0all"][0],
        allbodies["Zc0all"][0],
        xf,
        yf,
        zf,
    )
    CXudot, CYudot, CZudot, Cludot, Cmudot, Cnudot = aeroforces(
        cpudot,
        allbodies["nx0all"][0],
        allbodies["ny0all"][0],
        allbodies["nz0all"][0],
        allbodies["s0all"][0],
        allbodies["Xc0all"][0],
        allbodies["Yc0all"][0],
        allbodies["Zc0all"][0],
        xf,
        yf,
        zf,
    )
    CXvdot, CYvdot, CZvdot, Clvdot, Cmvdot, Cnvdot = aeroforces(
        cpvdot,
        allbodies["nx0all"][0],
        allbodies["ny0all"][0],
        allbodies["nz0all"][0],
        allbodies["s0all"][0],
        allbodies["Xc0all"][0],
        allbodies["Yc0all"][0],
        allbodies["Zc0all"][0],
        xf,
        yf,
        zf,
    )
    CXwdot, CYwdot, CZwdot, Clwdot, Cmwdot, Cnwdot = aeroforces(
        cpwdot,
        allbodies["nx0all"][0],
        allbodies["ny0all"][0],
        allbodies["nz0all"][0],
        allbodies["s0all"][0],
        allbodies["Xc0all"][0],
        allbodies["Yc0all"][0],
        allbodies["Zc0all"][0],
        xf,
        yf,
        zf,
    )
    CXpdot, CYpdot, CZpdot, Clpdot, Cmpdot, Cnpdot = aeroforces(
        cppdot,
        allbodies["nx0all"][0],
        allbodies["ny0all"][0],
        allbodies["nz0all"][0],
        allbodies["s0all"][0],
        allbodies["Xc0all"][0],
        allbodies["Yc0all"][0],
        allbodies["Zc0all"][0],
        xf,
        yf,
        zf,
    )
    CXqdot, CYqdot, CZqdot, Clqdot, Cmqdot, Cnqdot = aeroforces(
        cpqdot,
        allbodies["nx0all"][0],
        allbodies["ny0all"][0],
        allbodies["nz0all"][0],
        allbodies["s0all"][0],
        allbodies["Xc0all"][0],
        allbodies["Yc0all"][0],
        allbodies["Zc0all"][0],
        xf,
        yf,
        zf,
    )
    CXrdot, CYrdot, CZrdot, Clrdot, Cmrdot, Cnrdot = aeroforces(
        cprdot,
        allbodies["nx0all"][0],
        allbodies["ny0all"][0],
        allbodies["nz0all"][0],
        allbodies["s0all"][0],
        allbodies["Xc0all"][0],
        allbodies["Yc0all"][0],
        allbodies["Zc0all"][0],
        xf,
        yf,
        zf,
    )

    # Define stabder data type
    tp_stabder = np.dtype(
        {
            "names": (
                "CXu",
                "CZu",
                "Cmu",
                "CXw",
                "CZw",
                "Cmw",
                "CXudot",
                "CZudot",
                "Cmudot",
                "CXwdot",
                "CZwdot",
                "Cmwdot",
                "CXtheta",
                "CZtheta",
                "Cmtheta",
                "CXq",
                "CZq",
                "Cmq",
                "CXqdot",
                "CZqdot",
                "Cmqdot",
                "CYv",
                "Clv",
                "Cnv",
                "CYvdot",
                "Clvdot",
                "Cnvdot",
                "CYphi",
                "Clphi",
                "Cnphi",
                "CYpsi",
                "Clpsi",
                "Cnpsi",
                "CYp",
                "Clp",
                "Cnp",
                "CYr",
                "Clr",
                "Cnr",
                "CYpdot",
                "Clpdot",
                "Cnpdot",
                "CYrdot",
                "Clrdot",
                "Cnrdot",
            ),
            "formats": (
                object,
                object,
                object,  # 'CXu', 'CZu', 'Cmu'
                object,
                object,
                object,  # 'CXw', 'CZw', 'Cmw'
                object,
                object,
                object,  # 'CXudot', 'CZudot', 'Cmudot'
                object,
                object,
                object,  # 'CXwdot', 'CZwdot', 'Cmwdot'
                object,
                object,
                object,  # 'CXtheta','CZtheta','Cmtheta'
                object,
                object,
                object,  # 'CXq', 'CZq', 'Cmq'
                object,
                object,
                object,  # 'CXqdot', 'CZqdot', 'Cmqdot'
                object,
                object,
                object,  # 'CYv','Clv','Cnv'
                object,
                object,
                object,  # 'CYvdot','Clvdot','Cnvdot'
                object,
                object,
                object,  # 'CYphi','Clphi','Cnphi'
                object,
                object,
                object,  # 'CYpsi','Clpsi','Cnpsi'
                object,
                object,
                object,  # 'CYp', 'Clp', 'Cnp'
                object,
                object,
                object,  # 'CYr', 'Clr', 'Cnr'
                object,
                object,
                object,  # 'CYpdot', 'Clpdot', 'Cnpdot'
                object,
                object,
                object,
            ),
        }
    )  # 'CYrdot', 'Clrdot', 'Cnrdot'

    # Initialize stabder struct array
    stabder = np.zeros(1, dtype=tp_stabder)

    # Calculate total longitudinal stability derivatives
    stabder["CXu"][0] = np.sum(CXu) / Sref
    stabder["CZu"][0] = np.sum(CZu) / Sref
    stabder["Cmu"][0] = np.sum(Cmu) / Sref / cref
    stabder["CXw"][0] = np.sum(CXw) / Sref
    stabder["CZw"][0] = np.sum(CZw) / Sref
    stabder["Cmw"][0] = np.sum(Cmw) / Sref / cref
    stabder["CXudot"][0] = np.sum(CXudot) / Sref
    stabder["CZudot"][0] = np.sum(CZudot) / Sref
    stabder["Cmudot"][0] = np.sum(Cmudot) / Sref / cref
    stabder["CXwdot"][0] = np.sum(CXwdot) / Sref
    stabder["CZwdot"][0] = np.sum(CZwdot) / Sref
    stabder["Cmwdot"][0] = np.sum(Cmwdot) / Sref / cref
    stabder["CXtheta"][0] = np.sum(CXtheta) / Sref
    stabder["CZtheta"][0] = np.sum(CZtheta) / Sref
    stabder["Cmtheta"][0] = np.sum(Cmtheta) / Sref / cref
    stabder["CXq"][0] = np.sum(CXq) / Sref
    stabder["CZq"][0] = np.sum(CZq) / Sref
    stabder["Cmq"][0] = np.sum(Cmq) / Sref / cref
    stabder["CXqdot"][0] = np.sum(CXqdot) / Sref
    stabder["CZqdot"][0] = np.sum(CZqdot) / Sref
    stabder["Cmqdot"][0] = np.sum(Cmqdot) / Sref / cref

    # Calculate total lateral stability derivatives
    stabder["CYv"][0] = np.sum(CYv) / Sref
    stabder["Clv"][0] = np.sum(Clv) / Sref / bref
    stabder["Cnv"][0] = np.sum(Cnv) / Sref / bref
    stabder["CYvdot"][0] = np.sum(CYvdot) / Sref
    stabder["Clvdot"][0] = np.sum(Clvdot) / Sref / bref
    stabder["Cnvdot"][0] = np.sum(Cnvdot) / Sref / bref
    stabder["CYphi"][0] = np.sum(CYphi) / Sref
    stabder["Clphi"][0] = np.sum(Clphi) / Sref / bref
    stabder["Cnphi"][0] = np.sum(Cnphi) / Sref / bref
    stabder["CYpsi"][0] = np.sum(CYpsi) / Sref
    stabder["Clpsi"][0] = np.sum(Clpsi) / Sref / bref
    stabder["Cnpsi"][0] = np.sum(Cnpsi) / Sref / bref
    stabder["CYp"][0] = np.sum(CYp) / Sref
    stabder["Clp"][0] = np.sum(Clp) / Sref / bref
    stabder["Cnp"][0] = np.sum(Cnp) / Sref / bref
    stabder["CYr"][0] = np.sum(CYr) / Sref
    stabder["Clr"][0] = np.sum(Clr) / Sref / bref
    stabder["Cnr"][0] = np.sum(Cnr) / Sref / bref
    stabder["CYpdot"][0] = np.sum(CYpdot) / Sref
    stabder["Clpdot"][0] = np.sum(Clpdot) / Sref / bref
    stabder["Cnpdot"][0] = np.sum(Cnpdot) / Sref / bref
    stabder["CYrdot"][0] = np.sum(CYrdot) / Sref
    stabder["Clrdot"][0] = np.sum(Clrdot) / Sref / bref
    stabder["Cnrdot"][0] = np.sum(Cnrdot) / Sref / bref

    return stabder

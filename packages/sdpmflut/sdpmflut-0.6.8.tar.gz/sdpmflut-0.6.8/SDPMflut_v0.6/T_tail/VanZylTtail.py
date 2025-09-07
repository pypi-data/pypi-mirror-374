#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package that contains functions to create grids for the Source and Doublet Panel 
Method for the fin fairing of the Van Zyl T-tail and to interpolate the structural mode 
shapes onto all grids.

This code is part of the SDPMflut Matlab distribution.
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
import numpy as np
import numpy.matlib
import airfoils
from SDPMgeometry import SDPM_control_normal_tangential
from scipy.interpolate import Rbf

def finfairing(body,airfoil_fairing,airfoil_params_fairing,z_root_tip,x0Root,c0Fair):
    # Create the SDPM grid for the fin fairing of the Van Zyl T-tail. This code
    # is very specific, it works but cannot be used for any other purpose. 
    # There are two fin fairing bodies, one lower and one upper, separated by 
    # the chordline of the horizontal tailplanes. The airfoil of the fin is 
    # NACA 0012 up to the junction with the tailplanes, where it becomes flat. 
    # Downstream of the tailplane trailing edge, the fin fairing airfoil 
    # becomes a triangle coming to a point at the fairing trailing edge. At the 
    # intersection between the fairing and the tailplanes, the grids are 
    # identical.
	# body: struct array containing the SDPM grids for the fin and the two
	# horizontal tailplanes
	# airfoil: string containing the airfoil name. 
	# airfoil_params: 1*2 array containing the NACA number of the airfoil, 
	#    mpt, and the parameter to define if the trailing edge will be open or 
	#    closed, teclosed
	# z_root_tip: 1*2 array containing the z coordinate of the root and tip of
	#    the fin fairing, respectively
	# x0Root: x coordinate of the root leading edge of the fairing
	# c0Fair: root chord of the fairing
    
    # Create lower fairing
    name='FairLo';
    ibody=3
    
    # x-coordinates of points from fairing trailing edge to tailplane root
    # trailing edge
    x1=np.linspace(x0Root+c0Fair,body['Xp0'][1][0,0],body['m'][1]//2+1)
    # x-coordinates of points from tailplane root trailing edge to tailplane 
    # root leading edge
    x2=body['Xp0'][1][0:body['m'][1]+1,0]
    # x-coordinates of points from tailplane root leading edge to fairing 
    # leading edge
    x3=np.linspace(body['Xp0'][1][body['m'][1],0],x0Root,body['m'][1]//2+1)
    
    # y-coordinates of points from fairing trailing edge to tailplane root
    # trailing edge. Linear variation from zero to root trailing edge of 
    # taiplane.
    y1=(0.0-body['Yp0'][1][0,0])/(x1[0]-x1[body['m'][1]//2])*(x1-x1[body['m'][1]//2])+body['Yp0'][1][0,0]
    # y-coordinates of points from tailplane root trailing edge to tailplane 
    # root leading edge
    y2=body['Yp0'][1][0:body['m'][1]+1,0]
    # Non-dimensionalise x3 by the fairing chord to calculate the airfoil
    # section of the fairing upstream of the tailiplane root leading edge
    xp=(x3-x3[body['m'][1]//2])/c0Fair
    xp=np.concatenate([xp[0:body['m'][1]//2], np.flip(xp)])
    if airfoil_fairing == 'nacafourdigit':
        yp,_=airfoils.nacafourdigit(xp,body['m'][1]//2,airfoil_params_fairing[0],airfoil_params_fairing[1])
    # End if
    # y-coordinates of points from tailplane root leading edge to fairing 
    # leading edge
    y3=-yp[0:body['m'][1]//2+1]*c0Fair

    # Upper edge of lower fin fairing. Lower edge of fin fairing is constant.
    # z-coordinates of points from fairing trailing edge to tailplane root
    # trailing edge. All equal to z coordinate of tailplane root trailing edge.
    z1=np.ones(body['m'][1]//2+1)*body['Zp0'][1][0,0]
    # z-coordinates of points from tailplane root trailing edge to tailplane 
    # root leading edge
    z2=body['Zp0'][1][0:body['m'][1]+1,0]
    # z-coordinates of points from tailplane root leading edge to fairing 
    # leading edge. All equal to z coordinate of tailplane root leading edge.
    z3=np.ones(body['m'][1]//2+1)*body['Zp0'][1][body['m'][1],0]

    # Assemble all coordinates of one side of fairing
    xtot=np.concatenate([x1[0:body['m'][1]//2],x2,x3[1:body['m'][1]//2+1]])
    ytot=np.concatenate([y1[0:body['m'][1]//2],y2,y3[1:body['m'][1]//2+1]])
    ztot=np.concatenate([z1[0:body['m'][1]//2],z2,z3[1:body['m'][1]//2+1]])

    # Create SDPM grid of panel vertices
    xx=np.concatenate([xtot[0:2*body['m'][1]],np.flip(xtot)])
    yy=np.concatenate([ytot[0:2*body['m'][1]],-np.flip(ytot)])
    zz=np.concatenate([ztot[0:2*body['m'][1]],np.flip(ztot)])
    Xp0=np.zeros((4*body['m'][1]+1,2))
    Yp0=np.zeros((4*body['m'][1]+1,2))
    Zp0=np.ones((4*body['m'][1]+1,2))*z_root_tip[0]
    for i in range(0,2):
        Xp0[:,i]=xx
        Yp0[:,i]=yy
        if i == 1:
            Zp0[:,i]=zz
        # End if
    # End if

    # Calculate control points, normal vectors and areas
    dir_tau=3
    Xc0,Yc0,Zc0,nx0,ny0,nz0,tauxx0,tauxy0,tauxz0,tauyx0,tauyy0,tauyz0,s0,cpln0,sm0,tmx0,tmy0,tmz0,sn0,tnx0,tny0,tnz0=SDPM_control_normal_tangential(Xp0,Yp0,Zp0,dir_tau)

    # Create wake
    dx=c0Fair/(2*body['m'][1])     # Chordwise length of wake doublet panels, use root chord to calculate it
    Xw0=np.zeros((2*body['mw'][1]+1,1+1))       # Initialize wake doublet panel vertices
    Xw0[0,:]=Xp0[4*body['m'][1],:]             # Leading edge of first row of wake doublet panels
    # Cycle through the chordwise number of wake  doublet panels
    for i in range (1,2*body['mw'][1]+1):
        # Calculate x-coordinates of ith row of doublet panels
        Xw0[i,:]=Xw0[i-1,:]+dx
    # Set y-coordinates of all spanwise wake doublet panels to corresponding
    # spanwise y-coordinates of wing panels
    Yw0=np.matlib.repmat(Yp0[4*body['m'][1],:],2*body['mw'][1]+1,1)
    # Set z-coordinates of all wake  doublet panel vertices to corresponding
    # bound trailing edge spanwise vortex segment z-coordinates
    Zw0=np.matlib.repmat(Zp0[4*body['m'][1],:],2*body['mw'][1]+1,1)
    
    # Assign data to body struct array
    body['Xp0'][ibody]=Xp0
    body['Yp0'][ibody]=Yp0
    body['Zp0'][ibody]=Zp0
    body['Xc0'][ibody]=Xc0
    body['Yc0'][ibody]=Yc0
    body['Zc0'][ibody]=Zc0 
    body['Xc0all'][ibody]=Xc0   # As the body only has one of row of panels Xc0all=Xc0
    body['Yc0all'][ibody]=Yc0   # As the body only has one of row of panels Yc0all=Yc0
    body['Zc0all'][ibody]=Zc0   # As the body only has one of row of panels Zc0all=Zc0
    body['Xw0'][ibody]=Xw0
    body['Yw0'][ibody]=Yw0
    body['Zw0'][ibody]=Zw0
    body['mw'][ibody]=2*body['mw'][1]
    body['nx0'][ibody]=nx0
    body['ny0'][ibody]=ny0
    body['nz0'][ibody]=nz0
    body['tauxx0'][ibody]=tauxx0
    body['tauxy0'][ibody]=tauxy0
    body['tauxz0'][ibody]=tauxz0
    body['tauyx0'][ibody]=tauyx0
    body['tauyy0'][ibody]=tauyy0
    body['tauyz0'][ibody]=tauyz0
    body['nx0all'][ibody]=nx0   # As the body only has one of row of panels nx0all=nx0
    body['ny0all'][ibody]=ny0   # As the body only has one of row of panels ny0all=ny0
    body['nz0all'][ibody]=nz0   # As the body only has one of row of panels nz0all=nz0
    body['s0'][ibody]=s0
    body['s0all'][ibody]=s0     # As the body only has one of row of panels s0all=s0
    body['m'][ibody]=2*body['m'][1]
    body['n'][ibody]=1
    body['c0'][ibody]=c0Fair
    body['b'][ibody]=Zp0[0,1]-Zp0[0,0]
    body['yc'][ibody]=0
    body['AR'][ibody]=0
    body['S'][ibody]=0
    body['name'][ibody]=name
    body['dir_tau'][ibody]=dir_tau    
    
    # Create upper fairing
    name='FairUp';
    ibody=4

    # x-coordinates of points from fairing leading edge to tailplane root
    # leading edge
    x1=np.linspace(x0Root,body['Xp0'][1][body['m'][1],0],body['m'][1]//2+1)
    # x-coordinates of points from tailplane root leading edge to tailplane 
    # root trailing edge
    x2=body['Xp0'][1][body['m'][1]:2*body['m'][1]+1,0]
    # x-coordinates of points from tailplane root trailing edge to fairing 
    # trailing edge
    x3=np.linspace(body['Xp0'][1][2*body['m'][1],0],x0Root+c0Fair,body['m'][1]//2+1)

    # Non-dimensionalise x1 by the fairing chord to calculate the airfoil
    # section of the fairing upstream of the tailiplane root leading edge
    xp=(x1-x1[0])/c0Fair
    xp=np.concatenate([np.flip(xp), xp[1:body['m'][1]//2+1]])
    if airfoil_fairing == 'nacafourdigit':
        yp,_=airfoils.nacafourdigit(xp,body['m'][1]//2,airfoil_params_fairing[0],airfoil_params_fairing[1])
    # End if
    # y-coordinates of points from fairing leading edge to tailplane root
    # leading edge
    y1=yp[body['m'][1]//2:body['m'][1]+1]*c0Fair
    # y-coordinates of points from tailplane root leading edge to tailplane 
    # root trailing edge
    y2=body['Yp0'][1][body['m'][1]:2*body['m'][1]+1,0]
    # y-coordinates of points from tailplane root trailing edge to fairing 
    # trailing edge. Linear variation from root trailing edge of taiplane to
    # zero.
    y3=(0.0-body['Yp0'][1][2*body['m'][1],0])/(x3[body['m'][1]//2]-x3[0])*(x3-x3[0])+body['Yp0'][1][2*body['m'][1],0]

    # Lower edge of upper fin fairing. Upper edge of fin fairing is constant.
    # z-coordinates of points from fairing leading edge to tailplane root
    # leading edge. All equal to z coordinate of tailplane root leading edge.
    z1=np.ones(body['m'][1]//2+1)*body['Zp0'][1][body['m'][1],0]
    # z-coordinates of points from tailplane root leading edge to tailplane 
    # root trailing edge
    z2=body['Zp0'][1][body['m'][1]:2*body['m'][1]+1,0]
    # z-coordinates of points from tailplane root trailing edge to fairing 
    # trailing edge. All equal to z coordinate of tailplane root trailing edge.
    z3=np.ones(body['m'][1]//2+1)*body['Zp0'][1][2*body['m'][1],0]

    # Assemble all coordinates of one side of fairing
    xtot=np.concatenate([x1[0:body['m'][1]//2],x2,x3[1:body['m'][1]//2+1]])
    ytot=np.concatenate([y1[0:body['m'][1]//2],y2,y3[1:body['m'][1]//2+1]])
    ztot=np.concatenate([z1[0:body['m'][1]//2],z2,z3[1:body['m'][1]//2+1]])

    # Create SDPM grid of panel vertices
    xx=np.concatenate([np.flip(xtot),xtot[1:2*body['m'][1]+1]])
    yy=np.concatenate([np.flip(ytot),-ytot[1:2*body['m'][1]+1]])
    zz=np.concatenate([np.flip(ztot),ztot[1:2*body['m'][1]+1]])
    Xp0=np.zeros((4*body['m'][1]+1,2))
    Yp0=np.zeros((4*body['m'][1]+1,2))
    Zp0=np.ones((4*body['m'][1]+1,2))*z_root_tip[1]
    for i in range(0,2):
        Xp0[:,i]=xx
        Yp0[:,i]=yy
        if i == 0:
            Zp0[:,i]=zz
        # End if
    # End if

    # Calculate control points, normal vectors and areas
    dir_tau=3
    Xc0,Yc0,Zc0,nx0,ny0,nz0,tauxx0,tauxy0,tauxz0,tauyx0,tauyy0,tauyz0,s0,cpln0,sm0,tmx0,tmy0,tmz0,sn0,tnx0,tny0,tnz0=SDPM_control_normal_tangential(Xp0,Yp0,Zp0,dir_tau)

    # Create wake
    dx=c0Fair/(2*body['m'][1])     # Chordwise length of wake doublet panels, use root chord to calculate it
    Xw0=np.zeros((2*body['mw'][1]+1,1+1))       # Initialize wake doublet panel vertices
    Xw0[0,:]=Xp0[4*body['m'][1],:]             # Leading edge of first row of wake doublet panels
    # Cycle through the chordwise number of wake  doublet panels
    for i in range (1,2*body['mw'][1]+1):
        # Calculate x-coordinates of ith row of doublet panels
        Xw0[i,:]=Xw0[i-1,:]+dx
    # Set y-coordinates of all spanwise wake doublet panels to corresponding
    # spanwise y-coordinates of wing panels
    Yw0=np.matlib.repmat(Yp0[4*body['m'][1],:],2*body['mw'][1]+1,1)
    # Set z-coordinates of all wake  doublet panel vertices to corresponding
    # bound trailing edge spanwise vortex segment z-coordinates
    Zw0=np.matlib.repmat(Zp0[4*body['m'][1],:],2*body['mw'][1]+1,1)
    
    # Assign data to body struct array
    body['Xp0'][ibody]=Xp0
    body['Yp0'][ibody]=Yp0
    body['Zp0'][ibody]=Zp0
    body['Xc0'][ibody]=Xc0
    body['Yc0'][ibody]=Yc0
    body['Zc0'][ibody]=Zc0 
    body['Xc0all'][ibody]=Xc0   # As the body only has one of row of panels Xc0all=Xc0
    body['Yc0all'][ibody]=Yc0   # As the body only has one of row of panels Yc0all=Yc0
    body['Zc0all'][ibody]=Zc0   # As the body only has one of row of panels Zc0all=Zc0
    body['Xw0'][ibody]=Xw0
    body['Yw0'][ibody]=Yw0
    body['Zw0'][ibody]=Zw0
    body['mw'][ibody]=2*body['mw'][1]
    body['nx0'][ibody]=nx0
    body['ny0'][ibody]=ny0
    body['nz0'][ibody]=nz0
    body['tauxx0'][ibody]=tauxx0
    body['tauxy0'][ibody]=tauxy0
    body['tauxz0'][ibody]=tauxz0
    body['tauyx0'][ibody]=tauyx0
    body['tauyy0'][ibody]=tauyy0
    body['tauyz0'][ibody]=tauyz0
    body['nx0all'][ibody]=nx0   # As the body only has one of row of panels nx0all=nx0
    body['ny0all'][ibody]=ny0   # As the body only has one of row of panels ny0all=ny0
    body['nz0all'][ibody]=nz0   # As the body only has one of row of panels nz0all=nz0
    body['s0'][ibody]=s0
    body['s0all'][ibody]=s0     # As the body only has one of row of panels s0all=s0
    body['m'][ibody]=2*body['m'][1]
    body['n'][ibody]=1
    body['c0'][ibody]=c0Fair
    body['yc'][ibody]=0
    body['AR'][ibody]=0
    body['S'][ibody]=0
    body['name'][ibody]=name
    body['dir_tau'][ibody]=dir_tau        
    
    return body

def ttailmodesinterp(body,z_root_tip,nmodes,xxplot,yyplot,zzplot,modeshapesx,modeshapesy,modeshapesz,modeshapesRx,modeshapesRy,modeshapesRz):
	# Interpolates the beam mode shapes of the Van Zyl T-tail onto the SDPM
	# grid. This code is very specific, it works but cannot be used for any
	# other purpose.
	# body: struct array containing the SDPM grids for the fin, fin farings and
	# horizontal tailplanes
	# z_root_tip: 1*2 array containing the z coordinate of the root and tip of
	#    the fin fairing, respectively
	# nmodes: number of modes to use in calculating the solution
	# airfoil_params: 1*2 array containing the NACA number of the airfoil,
	# grdf: x, y and z coordinates of the structural grid points
	# modeshapesx,modeshapesy,modeshapesz: matrices containing the rotation
	# mode shapes in the x, y and z directions, respectively
	# modeshapesphi,modeshapestheta,modeshapespsi: matrices containing the 
	# rotation mode shapes around the x, y and z axes, respectively
	
    # Select interpolation method
    rbfmethod="linear"
    # Acquire number of bodies in body struct array
    nbody=len(body)
    for ibody in range(0,nbody):
    	# Acquire size of panel control point arrays of current body
        m,n=body['Xc0'][ibody].shape
        m=m//2 # Number of chordwise panels on the upper surface only
        # Initialize arrays to hold the mode shapes
        Phi_xall=np.zeros((2*m*n,nmodes))
        Phi_yall=np.zeros((2*m*n,nmodes))
        Phi_zall=np.zeros((2*m*n,nmodes))
        Phi_phiall=np.zeros((2*m*n,nmodes))
        Phi_thetaall=np.zeros((2*m*n,nmodes))
        Phi_psiall=np.zeros((2*m*n,nmodes))
        # Define coordinate 1 to interpolate to
        X1=np.reshape(body['Xc0'][ibody],2*m*n,order='C')
        # Set up interpolation for each body 
        if ibody == 0:
        	# Fin
            # Select all points of the structural grid that lie on y=0; they
            # belong to the fin
            iko=np.argwhere(yyplot == 0.0)
            # Define coordinates of data to interpolate
            xyplot=np.concatenate((xxplot[iko[:,0]],zzplot[iko[:,0]]),axis=1)
            # Define coordinate 2 to interpolate to
            X2=np.reshape(body['Zc0'][ibody],2*m*n,order='C')
            # Find indices of SDPM control panels that lie lower than the
            # lowest structural grid point
            zmin=np.min(zzplot)
            izero=np.argwhere(X2 <= zmin)
        elif ibody == 1 or ibody == 2:
        	# Horizontal taiplanes
            # Select all points of the structural grid that do not lie on y=0;
            # they belong to the tailplanes
            iko=np.argwhere(yyplot != 0.0)
            # Define coordinates of data to interpolate
            xyplot=np.concatenate((xxplot[iko[:,0]],yyplot[iko[:,0]]),axis=1)
            # Define coordinate 2 to interpolate to
            X2=np.reshape(body['Yc0'][ibody],2*m*n,order='C')
        elif ibody == 3 or ibody == 4:
        	# Fin fairings
            # Select all points of the structural grid that lie on y=0 and are
            # higher than the root of the fairing; they belong to the fairing.
            iko=np.argwhere((zzplot >= z_root_tip[0])*(yyplot == 0.0))
            # Define coordinates of data to interpolate
            xyplot=np.concatenate((xxplot[iko[:,0]],zzplot[iko[:,0]]),axis=1)
            # Define coordinate 2 to interpolate to
            X2=np.reshape(body['Zc0'][ibody],2*m*n,order='C')
        # End if    
        # Cycle over the modes    
        for imode in range(0,nmodes):
            # Translation in x
            fitresult = Rbf(xyplot[:,0], xyplot[:,1], -modeshapesx[iko[:,0],imode], function=rbfmethod)    
            Phi_xall[:,imode]=fitresult(X1, X2)
            # Translation in y
            fitresult = Rbf(xyplot[:,0], xyplot[:,1], -modeshapesy[iko[:,0],imode], function=rbfmethod)    
            Phi_yall[:,imode]=fitresult(X1, X2)
            # Translation in z
            fitresult = Rbf(xyplot[:,0], xyplot[:,1], -modeshapesz[iko[:,0],imode], function=rbfmethod)    
            Phi_zall[:,imode]=fitresult(X1, X2)
            # Rotation around x
            fitresult = Rbf(xyplot[:,0], xyplot[:,1],-modeshapesRx[iko[:,0],imode], function=rbfmethod)    
            Phi_phiall[:,imode]=fitresult(X1, X2)        
            # Rotation around y
            fitresult = Rbf(xyplot[:,0], xyplot[:,1],-modeshapesRy[iko[:,0],imode], function=rbfmethod)    
            Phi_thetaall[:,imode]=fitresult(X1, X2)     
            # Rotation around z
            fitresult = Rbf(xyplot[:,0], xyplot[:,1],-modeshapesRz[iko[:,0],imode], function=rbfmethod)    
            Phi_psiall[:,imode]=fitresult(X1, X2)     
        # End for
        if ibody == 0:
            # Set to zero all modal displacements that lie lower than the
            # lowest structural grid point
            Phi_xall[izero,:]=0.0
            Phi_yall[izero,:]=0.0
            Phi_zall[izero,:]=0.0
            Phi_phiall[izero,:]=0.0
            Phi_thetaall[izero,:]=0.0
            Phi_psiall[izero,:]=0.0
        # End if
        # Store interpolated mode shapes in body struct array
        body['Phi_xall'][ibody]=Phi_xall
        body['Phi_yall'][ibody]=Phi_yall
        body['Phi_zall'][ibody]=Phi_zall
        body['Phi_phiall'][ibody]=Phi_phiall
        body['Phi_thetaall'][ibody]=Phi_thetaall
        body['Phi_psiall'][ibody]=Phi_psiall
    # End for

    return body

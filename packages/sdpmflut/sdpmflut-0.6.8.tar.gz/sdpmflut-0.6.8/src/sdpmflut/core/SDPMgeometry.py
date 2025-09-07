#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package SDPMgeometry contains functions to create grids for the Source and 
Doublet Panel Method.

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
from scipy import linalg
from . import airfoils

def normalarea(x,y,z):
    # Calculates the unit normal vector and surface area of a near-planar 
    # quadrilateral panel. The vertices of the quadrilateral are stored in 
    # vectors x, y and z. Also calculates a measure of the coplanarity of the 
    # four vertices.

    # Normal vector from diagonals 13 and 24. The vector is normal to these two
    # diagonals. Equation 5.90
    normal=np.cross(np.array([x[2]-x[0], y[2]-y[0], z[2]-z[0]]),np.array([x[1]-x[3], y[1]-y[3], z[1]-z[3]]))
    normal=normal/linalg.norm(normal)
    # Calculate a second normal from edges 12 and 13. The vector is normal to 
    # these two edges.
    normal2=np.cross(np.array([x[2]-x[0], y[2]-y[0], z[2]-z[0]]),np.array([x[1]-x[0], y[1]-y[0], z[1]-z[0]]))
    mag2=linalg.norm(normal2)
    # Test if the normal and normal2 are colinear. If they are, their cross 
    # product will be equal to zero. Store the magnitude of the cross product 
    # in cpln.
    if mag2 != 0.0:
        normal2=normal2/mag2
        cpln=np.cross(normal,normal2)
        cpln=linalg.norm(cpln)
    else:
        cpln=0.0
    # Enf if
    # Calculate a third normal from diagonal 13 and edge 14. The vector is 
    # normal to these two segments.
    normal3=np.cross(np.array([x[2]-x[0], y[2]-y[0], z[2]-z[0]]),np.array([x[3]-x[0], y[3]-y[0], z[3]-z[0]]))
    mag3=linalg.norm(normal3)
    # Calculate panel area from equation 5.91
    s=mag2/2.0+mag3/2.0;
    
    return normal,s,cpln

def SDPMgeometry_trap_fun(body,ibody,m,mw,nhalf,mirroredwing,linchord,linspan,trap,name,dir_tau,rollpitchyaw,rollpitchyaw_cent,lexyz,nmin):
    # Calculates the coordinates of the panel vertices for the Source and
    # Doublet Panel method.    
       
    # Calculate half span
    bhalf=np.sum(trap['span'])
    # Incremental array of half spans
    bsum=np.zeros(len(trap) + 1)
    bsum[1:len(trap) + 1]=np.cumsum(trap['span'])

    # Calculate the planform area of each trapezoidal section
    Strap=(trap['rootchord']+trap['rootchord']*trap['taper'])*trap['span']/2.0
    # Calculate wing planform area
    S=np.sum(Strap)
    # Calculate wing aspect ratio
    AR=(2.0*bhalf)**2/(2.0*S)

    # Define chordwise panel grid 
    if linchord == 1:
        # Linearly spaced non-dimensional chordwise panel vertex coordinates
        xp=np.linspace(0,1,num=m+1) 
        xp=np.concatenate([np.flip(xp),xp[1:m+1]])
    else:
        # Nonlinearly spaced non-dimensional chordwise panel vertex coordinates from equation 5.182
        xp=1-np.sin(np.linspace(0,np.pi,num=2*m+1))
    # End if
    
    # Distribute spanwise panels over the trapezoidal sections
    n_sec=np.round(trap['span']/bhalf*nhalf)
    n_sec=n_sec.astype(int)
    # Ensure that none of the sections have fewer than nmin spanwise panels
    iko=np.argwhere(n_sec <= nmin)
    if len(iko) > 0:
        n_sec[iko]=3
    # End if
    # Update spanwise panel number
    nhalf=np.sum(n_sec)
 
    if mirroredwing == 2:
        n=2*nhalf # Number of spanwise panels for the full wing
    else:
        n=nhalf
    # end if
    
    # Initialize grid
    Xp0=np.zeros((2*m+1,nhalf+1))
    Yp0=np.zeros((2*m+1,nhalf+1))
    Zp0=np.zeros((2*m+1,nhalf+1))
    
    # Cumulative sum of panels
    nsum=np.zeros(len(trap) + 1,dtype=int)
    nsum[1:len(trap) + 1]=np.cumsum(n_sec)
    # Set root x-coordinate of first section to zero
    xrootle=0.0
    # Cycle over the trapezoidal sections
    for i in range(0,len(trap)): 
        # Set up spanwise panel grid
        if linspan == 1:
            # Linearly spaced non-dimensional spanwise panel vertex coordinates
            yp=np.linspace(0,1,num=n_sec[i]+1) 
        else:
            # Nonlinearly spaced non-dimensional spanwise panel vertex coordinates from equation 5.183
            theta=np.linspace(np.pi,0,num=n_sec[i]+1)
            yp=(1+np.cos(theta))/2.0
        # End if        
        # Calculate linear variation of chord length over the trapezoidal section
        cvar=(trap['taper'][i]-1)*trap['rootchord'][i]*np.absolute(yp)+trap['rootchord'][i]
        # Calculate leading edge x-coordinate variation along the section due
        # to sweep
        xsweep=np.tan(trap['sweepLE'][i])*abs(yp)*trap['span'][i]
        # Calculate x-coordinates of panel vertices
        Xp0[:,nsum[i]:nsum[i+1]+1]=np.transpose(np.matlib.repmat(xp,n_sec[i]+1,1))*np.matlib.repmat(cvar,2*m+1,1)+\
            np.matlib.repmat(xsweep+xrootle,2*m+1,1)+trap['xledist'][i]
        # Calculate y-coordinates of panel vertices
        Yp0[:,nsum[i]:nsum[i+1]+1]=np.matlib.repmat(yp,2*m+1,1)*trap['span'][i]+bsum[i]
        
        # Calculate non-dimensional root airfoil shape    
        if trap['rootairfoil'][i] == 'nacafourdigit':
            zp1,zpcamb=airfoils.nacafourdigit(xp,m,trap['rootairfoilparams'][i][0],trap['rootairfoilparams'][i][1])
        elif trap['rootairfoil'][i] == 'nacafivedigit':
            zp1,zpcamb=airfoils.nacafivedigit(xp,m,trap['rootairfoilparams'][i][0],trap['rootairfoilparams'][i][1])
        elif trap['rootairfoil'][i] == 'NACA65A004':
            zp1,zpcamb=airfoils.NACA65A004(xp,m,trap['rootairfoilparams'][i][0])    
        elif trap['rootairfoil'][i] == 'NASASC20414':
            zp1,zpcamb=airfoils.NASASC20414(xp,m,trap['rootairfoilparams'][i][0])    
        elif trap['rootairfoil'][i] == 'NACA64A010':
            zp1,zpcamb=airfoils.NACA64A010(xp,m,trap['rootairfoilparams'][i][0])   
        elif trap['rootairfoil'][i] == 'flatplate':
            zp1,zpcamb=airfoils.flatplate(xp,m)  
        elif trap['rootairfoil'][i] == 'biconvex':
            zp1,zpcamb=airfoils.biconvex(xp,m,trap['rootairfoilparams'][i][0])  
        # End if       
        
        # Calculate non-dimensional tip airfoil shape    
        if trap['tipairfoil'][i] == 'nacafourdigit':
            zp2,zpcamb=airfoils.nacafourdigit(xp,m,trap['tipairfoilparams'][i][0],trap['tipairfoilparams'][i][1])
        elif trap['tipairfoil'][i] == 'nacafivedigit':
            zp2,zpcamb=airfoils.nacafivedigit(xp,m,trap['tipairfoilparams'][i][0],trap['tipairfoilparams'][i][1])
        elif trap['tipairfoil'][i] == 'NACA65A004':
            zp2,zpcamb=airfoils.NACA65A004(xp,m,trap['tipairfoilparams'][i][0])    
        elif trap['tipairfoil'][i] == 'NASASC20414':
            zp2,zpcamb=airfoils.NASASC20414(xp,m,trap['tipairfoilparams'][i][0])  
        elif trap['tipairfoil'][i] == 'NACA64A010':
            zp2,zpcamb=airfoils.NACA64A010(xp,m,trap['tipairfoilparams'][i][0])  
        elif trap['tipairfoil'][i] == 'flatplate':
            zp2,zpcamb=airfoils.flatplate(xp,m)  
        elif trap['tipairfoil'][i] == 'biconvex':
            zp2,zpcamb=airfoils.biconvex(xp,m,trap['tipairfoilparams'][i][0])  
        # End if        
        # Interpolate linearly between the root and tip airfoils  
        zpmat=np.zeros((2*m+1,n_sec[i]+1))
        for iy in range(0,n_sec[i]+1): 
            zpmat[:,iy]=(zp2-zp1)*yp[iy]+zp1
        # End for
        
        # Calculate z-coordinates of panel vertices
        if trap['rootairfoil'][i] == 'flatplate':
            Zp0[:,nsum[i]:nsum[i+1]+1]=zpmat*trap['tipairfoilparams'][i][0]
        else:
            Zp0[:,nsum[i]:nsum[i+1]+1]=zpmat*np.matlib.repmat(cvar,2*m+1,1)
        # End for
        # Calculate  root x-coordinate of next section
        xrootle=xrootle+xsweep[n_sec[i]]+trap['xledist'][i]
    # End for
    
    # Only executed for flat plate airfoils
    if trap['rootairfoil'][0] == 'flatplate':
        # We assume that if the first trapezoidal section is a flat plate, the
        # entire wing is a flat plate of the same thickness. We then round off the
        # leading edge and bevel the trailing edge.
        # Bevel angle of airfoil (rounded to nearest degree)
        bangle=round(np.arctan(trap['rootairfoilparams'][0][0]/trap['rootairfoilparams'][0][1])*180.0/np.pi)*np.pi/180.0
        # Round off leading edge
        for i in range(0,nhalf+1):
            # Determine x coordinates of points that lie in the rounded off
            # section    
            iko=np.argwhere(Xp0[:,i]-Xp0[m,i] <= trap['rootairfoilparams'][0][0])
            # Radius of circle
            rcirc=trap['rootairfoilparams'][0][0]
            # Centre of circle
            xcent=Xp0[m,i]+rcirc
            zcent=0.0
            # Circle equation
            zz=zcent+np.sqrt(rcirc**2-(Xp0[iko,i]-xcent)**2+1e-16) # Add 1e-16 to avoid tiny negative argument in square root
            # Calculate z coordinates of points lying on a circle centred on
            # the chordline, one airfoil thickness behind the leading edge.
            Zp0[iko,i]=zz*np.sign(Zp0[iko,i])
        # End for
        # Bevel the trailing edge
        for i in range(0,nhalf+1):
            # Determine x coordinates of points that lie in the beveled
            # section            
            iko=np.argwhere(Xp0[0,i]-Xp0[:,i] <= trap['rootairfoilparams'][0][1])
            if len(iko) == 2:
                # There are no such points except for the trailing edge.
                # Move the x coordinates of the penultimate trailing edge
                # points to the edge of the bevel.
                Xp0[1,i]=Xp0[0,i]-trap['rootairfoilparams'][0][1]
                Xp0[2*m-1,i]=Xp0[0,i]-trap['rootairfoilparams'][0][1]
            else:
                # Calculate z coordinates of points lying on a straight line
                # passing from the trailing edge and parallel to the bevel
                # angle. 
                dummy=-(Xp0[iko,i]-Xp0[0,i])*np.tan(bangle)*np.sign(iko-m)+Zp0[0,i]
                # Only apply bevel at a point whose current Z coordinate is higher 
                # than the bevelled Z coordinate.
                dd=np.concatenate([Zp0[iko,i],dummy],axis=1)
                Zp0[iko,i]=np.expand_dims(np.min(np.abs(dd),axis=1),axis=1)*np.sign(Zp0[iko,i])
            # End if
        # End for
    # End if
        
    # Apply the twist angle variation
    for i in range(0,len(trap)): 
        # Set up spanwise panel grid
        if linspan == 1:
            # Linearly spaced non-dimensional spanwise panel vertex coordinates
            yp=np.linspace(0,1,num=n_sec[i]+1) 
        else:
            # Nonlinearly spaced non-dimensional spanwise panel vertex coordinates from equation 5.183
            theta=np.linspace(np.pi,0,num=n_sec[i]+1)
            yp=(1+np.cos(theta))/2.0
        # End if        
        # Calculate linear variation of chord length over the trapezoidal section
        cvar=(trap['taper'][i]-1)*trap['rootchord'][i]*np.absolute(yp)+trap['rootchord'][i]
        # Calculate linear twist variation from root to tip of trapezoidal
        # section
        epsilonvar=trap['roottwist'][i]+(trap['tiptwist'][i]-trap['roottwist'][i])*np.absolute(yp)
        # Rotate the airfoil
        for iy in range(1,n_sec[i]+1): 
            # Calculate rotation matrix for the current spanwise station
            Ry=np.array([[np.cos(epsilonvar[iy]), np.sin(epsilonvar[iy])],[-np.sin(epsilonvar[iy]), np.cos(epsilonvar[iy])]])
            # Calculate rotation centre
            xyzcent=np.array([Xp0[m,nsum[i]+iy], Yp0[m,nsum[i]+iy], Zp0[m,nsum[i]+iy]])+\
                trap['twistcent'][i]*np.array([cvar[iy], 0.0, 0.0])
            # Apply twist rotation around twistcent at the current spanwise station
            dummy=Ry @ np.array([Xp0[:,nsum[i]+iy]-xyzcent[0],Zp0[:,nsum[i]+iy]]-xyzcent[2])
            # Assign rotated coordinates
            Xp0[:,nsum[i]+iy]=dummy[0,:]+xyzcent[0]    # x-coordinates of panel vertices
            Zp0[:,nsum[i]+iy]=dummy[1,:]+xyzcent[2]    # z-coordinates of panel vertices
        # End for
    # End for

    # Calculate non-dimensional spanwise coordinates of all wing panel vertices
    yp=Yp0[0,:]/bhalf

    # Dihedral calculation
    # Calculate the difference in dihedral angle between sections
    if len(trap) == 1:
        dihedral_diff=np.array(trap['dihedral'][0],ndmin=1)
    else:
        dihedral_diff=np.concatenate([np.array([trap['dihedral'][0]]), np.diff(trap['dihedral'])])  
    # End if
    # Apply dihedral angle
    for i in range(0,len(trap)): 
        # Centre of rotation (root leading edge of trapezoidal section)
        xyzcent=np.array([Xp0[m,nsum[i]], Yp0[m,nsum[i]], Zp0[m,nsum[i]]])
        # Rotation matrix
        Rx=np.array([[1, 0, 0],[0, np.cos(dihedral_diff[i]), -np.sin(dihedral_diff[i])], \
                     [0, np.sin(dihedral_diff[i]), np.cos(dihedral_diff[i])]])
        # Apply dihedral rotation around root leading edge of trapezoidal section
        xx=np.reshape(Xp0[:,nsum[i]+1:nhalf+1],(1,(2*m+1)*(nhalf-nsum[i])),order='C')-xyzcent[0]
        yy=np.reshape(Yp0[:,nsum[i]+1:nhalf+1],(1,(2*m+1)*(nhalf-nsum[i])),order='C')-xyzcent[1]
        zz=np.reshape(Zp0[:,nsum[i]+1:nhalf+1],(1,(2*m+1)*(nhalf-nsum[i])),order='C')-xyzcent[2]
        dummy=Rx @ np.concatenate((xx,yy,zz),axis=0)
        # Assign rotated coordinates
        Xp0[:,nsum[i]+1:nhalf+1]=np.reshape(dummy[0,:],(2*m+1,nhalf-nsum[i]),order='C')+xyzcent[0]
        Yp0[:,nsum[i]+1:nhalf+1]=np.reshape(dummy[1,:],(2*m+1,nhalf-nsum[i]),order='C')+xyzcent[1]
        Zp0[:,nsum[i]+1:nhalf+1]=np.reshape(dummy[2,:],(2*m+1,nhalf-nsum[i]),order='C')+xyzcent[2]
        if i > 0:
            # Also rotate the root of the current trapezoidal section (tip of
            # previous trapezoidal section) by half the dihedral angle
            # difference.
            # Rotation matrix
            Rx=np.array([[1, 0, 0],[0, np.cos(dihedral_diff[i]/2.0), -np.sin(dihedral_diff[i]/2.0)], \
                        [0, np.sin(dihedral_diff[i]/2.0), np.cos(dihedral_diff[i]/2.0)]])
            # Apply dihedral rotation around root leading edge of trapezoidal section
            xyz=np.zeros((3,2*m+1))
            xyz[0,:]=Xp0[:,nsum[i]]-xyzcent[0]
            xyz[1,:]=Yp0[:,nsum[i]]-xyzcent[1]
            xyz[2,:]=Zp0[:,nsum[i]]-xyzcent[2]
            dummy=Rx @ xyz
            # Assign rotated coordinates
            Xp0[:,nsum[i]]=dummy[0,:]+xyzcent[0]
            Yp0[:,nsum[i]]=dummy[1,:]+xyzcent[1]
            Zp0[:,nsum[i]]=dummy[2,:]+xyzcent[2]
    # End for
    
    # Re-arrange wing panels if necessary 
    if mirroredwing == -1:
        # Left half-wing has been requested, mirror panel vertices
        Xp0=np.flip(Xp0,axis=1)
        Yp0=-np.flip(Yp0,axis=1)
        yp=-np.flip(yp)
        Zp0=np.flip(Zp0,axis=1)
    elif mirroredwing == 2:
        # Full wing has been requested, mirror panel vertices and concatenate with original
        Xp0=np.concatenate([np.flip(Xp0,axis=1),Xp0[:,1:nhalf+1]],axis=1)
        Yp0=np.concatenate([-np.flip(Yp0,axis=1),Yp0[:,1:nhalf+1]],axis=1)
        yp=np.concatenate([-np.flip(yp),yp[1:nhalf+1]],axis=0)
        Zp0=np.concatenate([np.flip(Zp0,axis=1),Zp0[:,1:nhalf+1]],axis=1)
    # End if
    
    # Move entire wing to required leading edge position
    Xp0=Xp0+lexyz[0]
    Yp0=Yp0+lexyz[1]
    Zp0=Zp0+lexyz[2]

    # Roll the entire wing
    if rollpitchyaw[0] != 0.0 :
        # Rotation angle
        rollangle=rollpitchyaw[0]
        # Rotation centre
        xf=rollpitchyaw_cent[0]
        yf=rollpitchyaw_cent[1]
        zf=rollpitchyaw_cent[2]
        # Rotation matrix
        Rx=np.array([[1.0, 0.0, 0.0], \
                     [0.0, np.cos(rollangle), -np.sin(rollangle)], \
                     [0.0, np.sin(rollangle), np.cos(rollangle)]])
        # Apply roll rotation around rotation centre
        xx=np.reshape(Xp0,(1,(2*m+1)*(n+1)),order='C')-xf
        yy=np.reshape(Yp0,(1,(2*m+1)*(n+1)),order='C')-yf
        zz=np.reshape(Zp0,(1,(2*m+1)*(n+1)),order='C')-zf
        dummy=Rx @ np.concatenate((xx,yy,zz),axis=0)
        # Assign rotated coordinates
        Xp0=np.reshape(dummy[0,:],(2*m+1,n+1),order='C')+xf
        Yp0=np.reshape(dummy[1,:],(2*m+1,n+1),order='C')+yf
        Zp0=np.reshape(dummy[2,:],(2*m+1,n+1),order='C')+zf
    # End if
    
    # Pitch the entire wing
    if rollpitchyaw[1] != 0.0 :
        # Rotation angle
        pitchangle=rollpitchyaw[1]
        # Rotation centre
        xf=rollpitchyaw_cent[0]
        yf=rollpitchyaw_cent[1]
        zf=rollpitchyaw_cent[2]
        # Rotation matrix
        Ry=np.array([[np.cos(pitchangle), 0.0, np.sin(pitchangle)], \
                     [0.0, 1.0, 0.0], \
                     [-np.sin(pitchangle), 0.0, np.cos(pitchangle)]])
        # Apply pitch rotation around rotation centre
        xx=np.reshape(Xp0,(1,(2*m+1)*(n+1)),order='C')-xf
        yy=np.reshape(Yp0,(1,(2*m+1)*(n+1)),order='C')-yf
        zz=np.reshape(Zp0,(1,(2*m+1)*(n+1)),order='C')-zf
        dummy=Ry @ np.concatenate((xx,yy,zz),axis=0)
        # Assign rotated coordinates
        Xp0=np.reshape(dummy[0,:],(2*m+1,n+1),order='C')+xf
        Yp0=np.reshape(dummy[1,:],(2*m+1,n+1),order='C')+yf
        Zp0=np.reshape(dummy[2,:],(2*m+1,n+1),order='C')+zf
    # End if

    # Yaw the entire wing
    if rollpitchyaw[2] != 0.0 :
        # Rotation angle
        yawangle=rollpitchyaw[2]
        # Rotation centre
        xf=rollpitchyaw_cent[0]
        yf=rollpitchyaw_cent[1]
        zf=rollpitchyaw_cent[2]
        # Rotation matrix
        Rz=np.array([[np.cos(yawangle), -np.sin(yawangle),0.0], \
                     [np.sin(yawangle), np.cos(yawangle),0.0], \
                     [0.0, 0.0, 1.0]])
        # Apply yaw rotation around rotation centre
        xx=np.reshape(Xp0,(1,(2*m+1)*(n+1)),order='C')-xf
        yy=np.reshape(Yp0,(1,(2*m+1)*(n+1)),order='C')-yf
        zz=np.reshape(Zp0,(1,(2*m+1)*(n+1)),order='C')-zf
        dummy=Rz @ np.concatenate((xx,yy,zz),axis=0)
        # Assign rotated coordinates
        Xp0=np.reshape(dummy[0,:],(2*m+1,n+1),order='C')+xf
        Yp0=np.reshape(dummy[1,:],(2*m+1,n+1),order='C')+yf
        Zp0=np.reshape(dummy[2,:],(2*m+1,n+1),order='C')+zf
    # End if
    
    # Non-dimensional spanwise control points coordinates
    yc=(yp[1:n+1]+yp[0:n])/2.0
    
    # Calculate control points, normal vectors and areas
    Xc0,Yc0,Zc0,nx0,ny0,nz0,tauxx0,tauxy0,tauxz0,tauyx0,tauyy0,tauyz0,s0,cpln0,sm0,tmx0,tmy0,tmz0,sn0,tnx0,tny0,tnz0=SDPM_control_normal_tangential(Xp0,Yp0,Zp0,dir_tau)
   
    # Reshape control point coordinate matrices into vectors
    Xc0all=np.reshape(Xc0,(2*m*n,1),order='C')
    Yc0all=np.reshape(Yc0,(2*m*n,1),order='C')
    Zc0all=np.reshape(Zc0,(2*m*n,1),order='C')
    # Reshape normal vector component matrices into vectors
    nx0all=np.reshape(nx0,(2*m*n,1),order='C')
    ny0all=np.reshape(ny0,(2*m*n,1),order='C')
    nz0all=np.reshape(nz0,(2*m*n,1),order='C')
    # Reshape panel area matrix into a vector
    s0all=np.reshape(s0,(2*m*n,1),order='C')

    # Create wake
    dx=trap['rootchord'][0]/m     # Chordwise length of wake doublet panels, use root chord to calculate it
    Xw0=np.zeros((mw+1,n+1))       # Initialize wake doublet panel vertices
    Xw0[0,:]=Xp0[2*m,:]             # Leading edge of first row of wake doublet panels
    # Cycle through the chordwise number of wake  doublet panels
    for i in range (1,mw+1):
        # Calculate x-coordinates of ith row of doublet panels
        Xw0[i,:]=Xw0[i-1,:]+dx
    # Set y-coordinates of all spanwise wake doublet panels to corresponding
    # spanwise y-coordinates of wing panels
    Yw0=np.matlib.repmat(Yp0[2*m,:],mw+1,1)
    # Set z-coordinates of all wake  doublet panel vertices to corresponding
    # bound trailing edge spanwise vortex segment z-coordinates
    Zw0=np.matlib.repmat(Zp0[2*m,:],mw+1,1)
    
    # Assign data to body struct array
    body['Xp0'][ibody]=Xp0
    body['Yp0'][ibody]=Yp0
    body['Zp0'][ibody]=Zp0
    body['Xc0'][ibody]=Xc0
    body['Yc0'][ibody]=Yc0
    body['Zc0'][ibody]=Zc0 
    body['Xc0all'][ibody]=Xc0all
    body['Yc0all'][ibody]=Yc0all
    body['Zc0all'][ibody]=Zc0all 
    body['Xw0'][ibody]=Xw0
    body['Yw0'][ibody]=Yw0
    body['Zw0'][ibody]=Zw0
    body['mw'][ibody]=mw
    body['nx0'][ibody]=nx0
    body['ny0'][ibody]=ny0
    body['nz0'][ibody]=nz0
    body['tauxx0'][ibody]=tauxx0
    body['tauxy0'][ibody]=tauxy0
    body['tauxz0'][ibody]=tauxz0
    body['tauyx0'][ibody]=tauyx0
    body['tauyy0'][ibody]=tauyy0
    body['tauyz0'][ibody]=tauyz0
    body['nx0all'][ibody]=nx0all
    body['ny0all'][ibody]=ny0all
    body['nz0all'][ibody]=nz0all
    body['s0'][ibody]=s0
    body['s0all'][ibody]=s0all
    body['m'][ibody]=m
    body['n'][ibody]=n
    body['c0'][ibody]=trap['rootchord'][0]
    body['b'][ibody]=2*bhalf
    body['yc'][ibody]=yc
    body['AR'][ibody]=AR
    body['S'][ibody]=S
    body['name'][ibody]=name
    body['dir_tau'][ibody]=dir_tau

    return body

def SDPM_control_normal_tangential(Xp,Yp,Zp,dir_tau):   
    # Calculates the control points, normal unit vectors, tangent unit vectors,
    # surface areas, flatness, chordwise lengths, chordwise unit vectors,
    # spanwise lengths and spanwise unit vectors of the quadrilateral panels
    # whose endpoints are given in matrices Xp, Yp and Zp. The control points
    # lie on the mean of the x, y and z coordinates of each panel; this code is
    # therefore only compatiple with the Source and Doublet Panel Method.

    # Calculate m+1 and n+1
    mp1,np1=Xp.shape
    # Calculate m and n
    m=mp1-1
    n=np1-1
    # Set up all arrays. Xc, Yc and Zc are set up as matrices because I 
    # can't concatenate arrays properly yet. They are converted to arrays before
    # being returned
    Xc=np.matrix(np.zeros((m, n)))
    Yc=np.matrix(np.zeros((m, n)))
    Zc=np.matrix(np.zeros((m, n)))
    nx=np.zeros((m, n))
    ny=np.zeros((m, n))
    nz=np.zeros((m, n))
    tauxx=np.zeros((m, n))
    tauxy=np.zeros((m, n))
    tauxz=np.zeros((m, n))
    tauyx=np.zeros((m, n))
    tauyy=np.zeros((m, n))
    tauyz=np.zeros((m, n))
    s=np.zeros((m, n))
    cpln=np.zeros((m, n))
    # Calculate control points, surfaces, normal and tangent vectors
    for i in range(0,m): 
        for j in range(0,n): 
            # Calculate control points
            x=np.array([Xp[i,j], Xp[i,j+1], Xp[i+1,j+1], Xp[i+1,j]])
            y=np.array([Yp[i,j], Yp[i,j+1], Yp[i+1,j+1], Yp[i+1,j]])
            z=np.array([Zp[i,j], Zp[i,j+1], Zp[i+1,j+1], Zp[i+1,j]])
            Xc[i,j]=np.mean(x)
            Yc[i,j]=np.mean(y)
            Zc[i,j]=np.mean(z)
            # Calculate the normal vectors and panel areas
            N,ss,cplnn=normalarea(x,y,z)
            nx[i,j]  = N[0]
            ny[i,j]  = N[1]
            nz[i,j]  = N[2]
            s[i,j] = ss
            cpln[i,j] = cplnn
            
            if dir_tau == 1:
                # Calculate tangential vector with zero x-component
                tauxx[i,j]=0.0                              # x-component of vector
                tauxy[i,j]=1/np.sqrt(1+(N[1]/N[2])**2)      # y-component of vector
                tauxz[i,j]=-N[1]/N[2]*tauxy[i,j]            # z-component of vector
            elif dir_tau == 2:
                # Calculate tangential vector with zero y-component
                tauxx[i,j]=1/np.sqrt(1+(N[0]/N[2])**2)      # x-component of vector
                tauxy[i,j]=0.0                              # y-component of vector
                tauxz[i,j]=-N[0]/N[2]*tauxx[i,j]            # z-component of vector
            elif dir_tau == 3:
                # Calculate tangential vector with zero z-component
                tauxx[i,j]=1/np.sqrt(1+(N[0]/N[1])**2)      # x-component of vector
                tauxy[i,j]=-N[0]/N[1]*tauxx[i,j]            # y-component of vector
                tauxz[i,j]=0.0                              # z-component of vector
            # End if     

            # Calculate a second tangential vector, perpendicular to the normal
            # and first tangential vector from equation 5.185
            tauy_xyz=np.cross(N,np.array([tauxx[i,j], tauxy[i,j], tauxz[i,j]]))
            tauyx[i,j]=tauy_xyz[0]     # x-component of vector
            tauyy[i,j]=tauy_xyz[1]     # y-component of vector
            tauyz[i,j]=tauy_xyz[2]     # z-component of vector
        # End if
    # End if
            
    # Now calculate normals and lengths necessary for caclulation of surface velocities
    # Calculate chordwise lengths of panels. They are also converted to arrays from matrices
    dXm=np.array(np.concatenate((Xc[1,:]-Xc[0,:],Xc[2:m,:]-Xc[0:m-2,:],Xc[m-1,:]-Xc[m-2,:]),axis=0))  # In x direction
    dYm=np.array(np.concatenate((Yc[1,:]-Yc[0,:],Yc[2:m,:]-Yc[0:m-2,:],Yc[m-1,:]-Yc[m-2,:]),axis=0))  # In y direction
    dZm=np.array(np.concatenate((Zc[1,:]-Zc[0,:],Zc[2:m,:]-Zc[0:m-2,:],Zc[m-1,:]-Zc[m-2,:]),axis=0))  # In z direction
    sm=np.sqrt(np.square(dXm)+np.square(dYm)+np.square(dZm))      # Total length
    # Calculate chordwise tangent unit vectors from equations 5.191
    tmx=np.divide(dXm,sm)    # x-component
    tmy=np.divide(dYm,sm)    # y-component
    tmz=np.divide(dZm,sm)    # z-component
        
    # Calculate spanwise lengths of panels.  They are also converted to arrays from matrices
    if n > 2:
        dXn=np.array(np.concatenate((Xc[:,1]-Xc[:,0],Xc[:,2:n]-Xc[:,0:n-2],Xc[:,n-1]-Xc[:,n-2]),axis=1))  # In x direction
        dYn=np.array(np.concatenate((Yc[:,1]-Yc[:,0],Yc[:,2:n]-Yc[:,0:n-2],Yc[:,n-1]-Yc[:,n-2]),axis=1))  # In x direction
        dZn=np.array(np.concatenate((Zc[:,1]-Zc[:,0],Zc[:,2:n]-Zc[:,0:n-2],Zc[:,n-1]-Zc[:,n-2]),axis=1))  # In x direction
        sn=np.sqrt(np.square(dXn)+np.square(dYn)+np.square(dZn))      # Total length
        # Calculate spanwise tangent unit vectors from equations 5.193
        tnx=np.divide(dXn,sn)    # x-component
        tny=np.divide(dYn,sn)    # x-component
        tnz=np.divide(dZn,sn)    # x-component
    elif n == 2:
        dXn=np.array(np.concatenate((Xc[:,1]-Xc[:,0],Xc[:,n-1]-Xc[:,n-2]),axis=1))  # In x direction
        dYn=np.array(np.concatenate((Yc[:,1]-Yc[:,0],Yc[:,n-1]-Yc[:,n-2]),axis=1))  # In x direction
        dZn=np.array(np.concatenate((Zc[:,1]-Zc[:,0],Zc[:,n-1]-Zc[:,n-2]),axis=1))  # In x direction
        sn=np.sqrt(np.square(dXn)+np.square(dYn)+np.square(dZn))      # Total length
        # Calculate spanwise tangent unit vectors from equations 5.193
        tnx=np.divide(dXn,sn)    # x-component
        tny=np.divide(dYn,sn)    # x-component
        tnz=np.divide(dZn,sn)    # x-component
    else:
        # It is impossible to calculate derivatives in the spanwise
        # direction
        sn=np.ones((m,n))
        tnx=np.zeros((m,n))
        tny=np.zeros((m,n))
        tnz=np.zeros((m,n))
    # End if    
    
    Xc=np.array(Xc)
    Yc=np.array(Yc)
    Zc=np.array(Zc)

    return Xc,Yc,Zc,nx,ny,nz,tauxx,tauxy,tauxz,tauyx,tauyy,tauyz,s,cpln,sm,tmx,tmy,tmz,sn,tnx,tny,tnz

def makewingtips(body,ibody,mirroredwing):
    # Creates SDPM grids for wingtips for the wing stored in body(ibody).
    # body: struct array describing the bodies present in the flow
    # ibody: index of body for which to create wingtips
    # mirroredwing: determines if the body(ibody) is a left-sided, right-sided
    #       or two-sided wing
    # IMPORTANT: makewingtips stors the winglets in positions ibody+1 and
    # ibody+2 of the body struct array. If any other data is stored in these
    # positions it will be over-written. Run makewingtips just after creating
    # body(ibody).
    
    # Get number of chordwise panels
    m=body['m'][ibody]
    # Set number of heightwise panels
    n=2
    # Determine direction of taux tangential vector
    if body['dir_tau'][ibody] == 2:
        dir_tau=3
    elif body['dir_tau'][ibody] == 3:
        dir_tau=1
    # End if
    
    if mirroredwing == 2:
        # Create left wingtip
        # Acquire leftmost panel vertex coordinates 
        X=body['Xp0'][ibody][:,0]
        Y=body['Yp0'][ibody][:,0]
        Z=body['Zp0'][ibody][:,0]
        # Calculate tip chord
        c0=np.sqrt((X[0]-X[m])**2+(Y[0]-Y[m])**2+(Z[0]-Z[m])**2)
        # Create SDPM grid for left wingtip
        Xp0=np.zeros((m+1,3))
        Yp0=np.zeros((m+1,3))
        Zp0=np.zeros((m+1,3))
        Xp0[:,0]=np.flipud(X[0:m+1])
        Xp0[:,1]=(np.flipud(X[0:m+1])+X[m:2*m+1])/2.0
        Xp0[:,2]=X[m:2*m+1]
        Yp0[:,0]=np.flipud(Y[0:m+1])
        Yp0[:,1]=(np.flipud(Y[0:m+1])+Y[m:2*m+1])/2.0
        Yp0[:,2]=Y[m:2*m+1]
        Zp0[:,0]=np.flipud(Z[0:m+1])
        Zp0[:,1]=(np.flipud(Z[0:m+1])+Z[m:2*m+1])/2.0
        Zp0[:,2]=Z[m:2*m+1]
        # Calculate control points, normal vectors and areas
        Xc0,Yc0,Zc0,nx0,ny0,nz0,tauxx0,tauxy0,tauxz0,tauyx0,tauyy0,tauyz0,s0,cpln0,sm0,tmx0,tmy0,tmz0,sn0,tnx0,tny0,tnz0=SDPM_control_normal_tangential(Xp0,Yp0,Zp0,dir_tau)
        
        # Reshape control point coordinate matrices into vectors
        Xc0all=np.reshape(Xc0,(m*n,1),order='C')
        Yc0all=np.reshape(Yc0,(m*n,1),order='C')
        Zc0all=np.reshape(Zc0,(m*n,1),order='C')
        # Reshape normal vector component matrices into vectors
        nx0all=np.reshape(nx0,(m*n,1),order='C')
        ny0all=np.reshape(ny0,(m*n,1),order='C')
        nz0all=np.reshape(nz0,(m*n,1),order='C')
        # Reshape panel area matrix into a vector
        s0all=np.reshape(s0,(m*n,1),order='C')
        
        # Assign data to body struct array
        body['Xp0'][ibody+1]=Xp0
        body['Yp0'][ibody+1]=Yp0
        body['Zp0'][ibody+1]=Zp0
        body['Xc0'][ibody+1]=Xc0
        body['Yc0'][ibody+1]=Yc0
        body['Zc0'][ibody+1]=Zc0 
        body['Xc0all'][ibody+1]=Xc0all
        body['Yc0all'][ibody+1]=Yc0all
        body['Zc0all'][ibody+1]=Zc0all 
        body['mw'][ibody+1]=0
        body['nx0'][ibody+1]=nx0
        body['ny0'][ibody+1]=ny0
        body['nz0'][ibody+1]=nz0
        body['tauxx0'][ibody+1]=tauxx0
        body['tauxy0'][ibody+1]=tauxy0
        body['tauxz0'][ibody+1]=tauxz0
        body['tauyx0'][ibody+1]=tauyx0
        body['tauyy0'][ibody+1]=tauyy0
        body['tauyz0'][ibody+1]=tauyz0
        body['nx0all'][ibody+1]=nx0all
        body['ny0all'][ibody+1]=ny0all
        body['nz0all'][ibody+1]=nz0all
        body['s0'][ibody+1]=s0
        body['s0all'][ibody+1]=s0all
        body['m'][ibody+1]=m//2
        body['n'][ibody+1]=n
        body['c0'][ibody+1]=c0
        body['name'][ibody+1]='left_wingtip'
        body['dir_tau'][ibody+1]=dir_tau

        # Create right wingtip
        # Acquire rightmost panel vertex coordinates 
        X=body['Xp0'][ibody][:,body['n'][ibody]]
        Y=body['Yp0'][ibody][:,body['n'][ibody]]
        Z=body['Zp0'][ibody][:,body['n'][ibody]]
        # Calculate tip chord
        c0=np.sqrt((X[0]-X[m])**2+(Y[0]-Y[m])**2+(Z[0]-Z[m])**2)
        # Create SDPM grid for left wingtip
        Xp0=np.zeros((m+1,3))
        Yp0=np.zeros((m+1,3))
        Zp0=np.zeros((m+1,3))
        Xp0[:,0]=X[m:2*m+1]
        Xp0[:,1]=(np.flipud(X[0:m+1])+X[m:2*m+1])/2.0
        Xp0[:,2]=np.flipud(X[0:m+1])
        Yp0[:,0]=Y[m:2*m+1]
        Yp0[:,1]=(np.flipud(Y[0:m+1])+Y[m:2*m+1])/2.0
        Yp0[:,2]=np.flipud(Y[0:m+1])
        Zp0[:,0]=Z[m:2*m+1]
        Zp0[:,1]=(np.flipud(Z[0:m+1])+Z[m:2*m+1])/2.0
        Zp0[:,2]=np.flipud(Z[0:m+1])
        # Calculate control points, normal vectors and areas
        Xc0,Yc0,Zc0,nx0,ny0,nz0,tauxx0,tauxy0,tauxz0,tauyx0,tauyy0,tauyz0,s0,cpln0,sm0,tmx0,tmy0,tmz0,sn0,tnx0,tny0,tnz0=SDPM_control_normal_tangential(Xp0,Yp0,Zp0,dir_tau)
        
        # Reshape control point coordinate matrices into vectors
        Xc0all=np.reshape(Xc0,(m*n,1),order='C')
        Yc0all=np.reshape(Yc0,(m*n,1),order='C')
        Zc0all=np.reshape(Zc0,(m*n,1),order='C')
        # Reshape normal vector component matrices into vectors
        nx0all=np.reshape(nx0,(m*n,1),order='C')
        ny0all=np.reshape(ny0,(m*n,1),order='C')
        nz0all=np.reshape(nz0,(m*n,1),order='C')
        # Reshape panel area matrix into a vector
        s0all=np.reshape(s0,(m*n,1),order='C')
        
        # Assign data to body struct array
        body['Xp0'][ibody+2]=Xp0
        body['Yp0'][ibody+2]=Yp0
        body['Zp0'][ibody+2]=Zp0
        body['Xc0'][ibody+2]=Xc0
        body['Yc0'][ibody+2]=Yc0
        body['Zc0'][ibody+2]=Zc0 
        body['Xc0all'][ibody+2]=Xc0all
        body['Yc0all'][ibody+2]=Yc0all
        body['Zc0all'][ibody+2]=Zc0all 
        body['mw'][ibody+2]=0
        body['nx0'][ibody+2]=nx0
        body['ny0'][ibody+2]=ny0
        body['nz0'][ibody+2]=nz0
        body['tauxx0'][ibody+2]=tauxx0
        body['tauxy0'][ibody+2]=tauxy0
        body['tauxz0'][ibody+2]=tauxz0
        body['tauyx0'][ibody+2]=tauyx0
        body['tauyy0'][ibody+2]=tauyy0
        body['tauyz0'][ibody+2]=tauyz0
        body['nx0all'][ibody+2]=nx0all
        body['ny0all'][ibody+2]=ny0all
        body['nz0all'][ibody+2]=nz0all
        body['s0'][ibody+2]=s0
        body['s0all'][ibody+2]=s0all
        body['m'][ibody+2]=m//2
        body['n'][ibody+2]=n
        body['c0'][ibody+2]=c0
        body['name'][ibody+2]='left_wingtip'
        body['dir_tau'][ibody+2]=dir_tau     
    elif mirroredwing == -1:
        # Create left wingtip
        # Acquire leftmost panel vertex coordinates 
        X=body['Xp0'][ibody][:,0]
        Y=body['Yp0'][ibody][:,0]
        Z=body['Zp0'][ibody][:,0]
        # Calculate tip chord
        c0=np.sqrt((X[0]-X[m])**2+(Y[0]-Y[m])**2+(Z[0]-Z[m])**2)
        # Create SDPM grid for left wingtip
        Xp0=np.zeros((m+1,3))
        Yp0=np.zeros((m+1,3))
        Zp0=np.zeros((m+1,3))
        Xp0[:,0]=np.flipud(X[0:m+1])
        Xp0[:,1]=(np.flipud(X[0:m+1])+X[m:2*m+1])/2.0
        Xp0[:,2]=X[m:2*m+1]
        Yp0[:,0]=np.flipud(Y[0:m+1])
        Yp0[:,1]=(np.flipud(Y[0:m+1])+Y[m:2*m+1])/2.0
        Yp0[:,2]=Y[m:2*m+1]
        Zp0[:,0]=np.flipud(Z[0:m+1])
        Zp0[:,1]=(np.flipud(Z[0:m+1])+Z[m:2*m+1])/2.0
        Zp0[:,2]=Z[m:2*m+1]
        # Calculate control points, normal vectors and areas
        Xc0,Yc0,Zc0,nx0,ny0,nz0,tauxx0,tauxy0,tauxz0,tauyx0,tauyy0,tauyz0,s0,cpln0,sm0,tmx0,tmy0,tmz0,sn0,tnx0,tny0,tnz0=SDPM_control_normal_tangential(Xp0,Yp0,Zp0,dir_tau)
        
        # Reshape control point coordinate matrices into vectors
        Xc0all=np.reshape(Xc0,(m*n,1),order='C')
        Yc0all=np.reshape(Yc0,(m*n,1),order='C')
        Zc0all=np.reshape(Zc0,(m*n,1),order='C')
        # Reshape normal vector component matrices into vectors
        nx0all=np.reshape(nx0,(m*n,1),order='C')
        ny0all=np.reshape(ny0,(m*n,1),order='C')
        nz0all=np.reshape(nz0,(m*n,1),order='C')
        # Reshape panel area matrix into a vector
        s0all=np.reshape(s0,(m*n,1),order='C')
        
        # Assign data to body struct array
        body['Xp0'][ibody+1]=Xp0
        body['Yp0'][ibody+1]=Yp0
        body['Zp0'][ibody+1]=Zp0
        body['Xc0'][ibody+1]=Xc0
        body['Yc0'][ibody+1]=Yc0
        body['Zc0'][ibody+1]=Zc0 
        body['Xc0all'][ibody+1]=Xc0all
        body['Yc0all'][ibody+1]=Yc0all
        body['Zc0all'][ibody+1]=Zc0all 
        body['mw'][ibody+1]=0
        body['nx0'][ibody+1]=nx0
        body['ny0'][ibody+1]=ny0
        body['nz0'][ibody+1]=nz0
        body['tauxx0'][ibody+1]=tauxx0
        body['tauxy0'][ibody+1]=tauxy0
        body['tauxz0'][ibody+1]=tauxz0
        body['tauyx0'][ibody+1]=tauyx0
        body['tauyy0'][ibody+1]=tauyy0
        body['tauyz0'][ibody+1]=tauyz0
        body['nx0all'][ibody+1]=nx0all
        body['ny0all'][ibody+1]=ny0all
        body['nz0all'][ibody+1]=nz0all
        body['s0'][ibody+1]=s0
        body['s0all'][ibody+1]=s0all
        body['m'][ibody+1]=m//2
        body['n'][ibody+1]=n
        body['c0'][ibody+1]=c0
        body['name'][ibody+1]='left_wingtip'
        body['dir_tau'][ibody+1]=dir_tau
    elif mirroredwing == 1:
        # Create right wingtip
        # Acquire rightmost panel vertex coordinates 
        X=body['Xp0'][ibody][:,body['n'][ibody]]
        Y=body['Yp0'][ibody][:,body['n'][ibody]]
        Z=body['Zp0'][ibody][:,body['n'][ibody]]
        # Calculate tip chord
        c0=np.sqrt((X[0]-X[m])**2+(Y[0]-Y[m])**2+(Z[0]-Z[m])**2)
        # Create SDPM grid for left wingtip
        Xp0=np.zeros((m+1,3))
        Yp0=np.zeros((m+1,3))
        Zp0=np.zeros((m+1,3))
        Xp0[:,0]=X[m:2*m+1]
        Xp0[:,1]=(np.flipud(X[0:m+1])+X[m:2*m+1])/2.0
        Xp0[:,2]=np.flipud(X[0:m+1])
        Yp0[:,0]=Y[m:2*m+1]
        Yp0[:,1]=(np.flipud(Y[0:m+1])+Y[m:2*m+1])/2.0
        Yp0[:,2]=np.flipud(Y[0:m+1])
        Zp0[:,0]=Z[m:2*m+1]
        Zp0[:,1]=(np.flipud(Z[0:m+1])+Z[m:2*m+1])/2.0
        Zp0[:,2]=np.flipud(Z[0:m+1])
        # Calculate control points, normal vectors and areas
        Xc0,Yc0,Zc0,nx0,ny0,nz0,tauxx0,tauxy0,tauxz0,tauyx0,tauyy0,tauyz0,s0,cpln0,sm0,tmx0,tmy0,tmz0,sn0,tnx0,tny0,tnz0=SDPM_control_normal_tangential(Xp0,Yp0,Zp0,dir_tau)
        
        # Reshape control point coordinate matrices into vectors
        Xc0all=np.reshape(Xc0,(m*n,1),order='C')
        Yc0all=np.reshape(Yc0,(m*n,1),order='C')
        Zc0all=np.reshape(Zc0,(m*n,1),order='C')
        # Reshape normal vector component matrices into vectors
        nx0all=np.reshape(nx0,(m*n,1),order='C')
        ny0all=np.reshape(ny0,(m*n,1),order='C')
        nz0all=np.reshape(nz0,(m*n,1),order='C')
        # Reshape panel area matrix into a vector
        s0all=np.reshape(s0,(m*n,1),order='C')
        
        # Assign data to body struct array
        body['Xp0'][ibody+1]=Xp0
        body['Yp0'][ibody+1]=Yp0
        body['Zp0'][ibody+1]=Zp0
        body['Xc0'][ibody+1]=Xc0
        body['Yc0'][ibody+1]=Yc0
        body['Zc0'][ibody+1]=Zc0 
        body['Xc0all'][ibody+1]=Xc0all
        body['Yc0all'][ibody+1]=Yc0all
        body['Zc0all'][ibody+1]=Zc0all 
        body['mw'][ibody+1]=0
        body['nx0'][ibody+1]=nx0
        body['ny0'][ibody+1]=ny0
        body['nz0'][ibody+1]=nz0
        body['tauxx0'][ibody+1]=tauxx0
        body['tauxy0'][ibody+1]=tauxy0
        body['tauxz0'][ibody+1]=tauxz0
        body['tauyx0'][ibody+1]=tauyx0
        body['tauyy0'][ibody+1]=tauyy0
        body['tauyz0'][ibody+1]=tauyz0
        body['nx0all'][ibody+1]=nx0all
        body['ny0all'][ibody+1]=ny0all
        body['nz0all'][ibody+1]=nz0all
        body['s0'][ibody+1]=s0
        body['s0all'][ibody+1]=s0all
        body['m'][ibody+1]=m//2
        body['n'][ibody+1]=n
        body['c0'][ibody+1]=c0
        body['name'][ibody+1]='left_wingtip'
        body['dir_tau'][ibody+1]=dir_tau     
    # End if
    return body

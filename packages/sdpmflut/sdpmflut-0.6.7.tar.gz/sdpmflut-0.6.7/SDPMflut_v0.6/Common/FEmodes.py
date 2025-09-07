#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package FEmodes contains functions to read structural modal model data from
a Matlab mat file and to interpolate the mode shapes onto the SDPM grid. 

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

import numpy as np
from scipy.interpolate import griddata
import scipy.io

def FE_matrices(fname,zeta0,nmodes):
    # Convert structural mode data in Matlab mat file. This function works for 
    # wing plate modes, whereby the wing is flat and lies on the z=0 plane.
    # Load modal matrices and mode shapes
    mat = scipy.io.loadmat(fname)
    # Extract modal matrices
    Mmodal = np.diag(mat['Mmodal'])*1.0
    Kmodal = np.diag(mat['Kmodal'])
    # Initialize structural mass and stifness matrices
    A=np.zeros((nmodes,nmodes))
    E=np.zeros((nmodes,nmodes))
    # Modal matrices are diagonal with negligible off-diagonal elements. Set 
    # the latter to zero.
    # Calculate diagonal elements of structural damping and stifness matrices
    for i in range (0,nmodes):
        A[i,i]=Mmodal[i]
        E[i,i]=Kmodal[i]
    # End for 
    # Wind off natural frequencies
    wn=np.sort(np.sqrt(np.diag(np.linalg.solve(A,E))))
    # Critical damping at wind-off conditions
    ccrit=2*np.diag(A)*wn
    # Structural damping matrix
    C=np.diag(ccrit*zeta0)
    
    # Extract FE grid matrices
    xxplot=mat['xxplot']
    yyplot=mat['yyplot']
    zzplot=mat['zzplot']
    # Extract and truncate mode shape matrices
    modeshapesx=mat['modeshapesx'][:,0:nmodes]
    modeshapesy=mat['modeshapesy'][:,0:nmodes]
    modeshapesz=mat['modeshapesz'][:,0:nmodes]
    modeshapesRx=mat['modeshapesRx'][:,0:nmodes]
    modeshapesRy=mat['modeshapesRy'][:,0:nmodes]
    modeshapesRz=mat['modeshapesRz'][:,0:nmodes]
    
    return A, C, E, wn, xxplot, yyplot, zzplot, modeshapesx, modeshapesy, modeshapesz, modeshapesRx, modeshapesRy, modeshapesRz

def SDPMmodeinterp(xxplot,yyplot,modeshapesx,modeshapesy,modeshapesz,modeshapesRx,modeshapesRy,modeshapesRz,body):
    # function body=SDPMmodeinterp(xxplot,yyplot,modeshapesx,modeshapesy,modeshapesz,modeshapesRx,modeshapesRy,body)
    # Interpolates structural modes shapes from the structural grid to the
    # control points of the SDPM grid. 
    # xxplot: (mFE*nFE)*1 array that contains the x coordinates of the structural model 
    # xxplot: (mFE*nFE)*1 array that contains the y coordinates of the structural model 
    # modeshapesx: mFE*nFE*nmodes array that contains the modal displacements
    # in the x direction.
    # modeshapesy: (mFE*nFE)*nmodes array that contains the modal displacements
    # in the y direction.
    # modeshapesz: (mFE*nFE)*nmodes array that contains the modal displacements
    # in the z direction.
    # modeshapesRx: (mFE*nFE)*nmodes array that contains the modal rotations
    # around the x axis.
    # modeshapesRy: (mFE*nFE)*nmodes array that contains the modal rotations
    # around the x axis.
    # modeshapesRz: (mFE*nFE)*nmodes array that contains the modal rotations
    # around the z axis.
    # body: Struct array of containing the coordinates of the control points
    # of the nbody bodies in the problem. 
    # Phi_xall: (2*m*n)*nmodes matrix containing the modal displacements in the
    # x direction in its columns
    # Phi_yall: (2*m*n)*nmodes matrix containing the modal displacements in the
    # y direction in its columns
    # Phi_zall: (2*m*n)*nmodes matrix containing the modal displacements in the
    # z direction in its columns
    # Phi_phiall: (2*m*n)*nmodes matrix containing the modal rotations around 
    # the x axis in its columns
    # Phi_thetaall: (2*m*n)*nmodes matrix containing the modal rotations around 
    # the y axis in its columns
    # Phi_psiall: (2*m*n)*nmodes matrix containing the modal rotations around 
    # the z axis in its columns
    
    # Obtain number of modes
    _,nmodes=modeshapesz.shape   
    # Assemble the x and y coordinates of the FE grid into one matrix with two columns
    xyplot=np.concatenate((xxplot,yyplot),axis=1)    
    # Obtain number of SDPM bodies
    nbody=len(body)
    
    # Cycle over the bodies
    for ibody in range(0,nbody): 
        # Obtain chordwise and spanwise numbers of SDPM panels for this body
        m,n=body['Xc0'][ibody].shape
        m=m//2 # Number of chordwise panels on the upper surface only
        # We interpolate only with respect to x and y of the half-wing. This 
        # means that the dihedral angle cannot be 90 degrees.
        # If there is dihedral, the y coordinates of the upper and lower
        # surfaces will be different. We interpolate with respect to the mean 
        # of these coordinates.
        XX=body['Xc0'][ibody][m:2*m,n//2:n];
        YY=(body['Yc0'][ibody][m:2*m,n//2:n]+np.flipud(body['Yc0'][ibody][0:m,n//2:n]))/2.0;
                
        # Initialize arrays to hold the mode shapes
        Phi_xall=np.zeros((2*m*n,nmodes))
        Phi_yall=np.zeros((2*m*n,nmodes))
        Phi_zall=np.zeros((2*m*n,nmodes))
        Phi_phiall=np.zeros((2*m*n,nmodes))
        Phi_thetaall=np.zeros((2*m*n,nmodes))
        Phi_psiall=np.zeros((2*m*n,nmodes))
        
        # Cycle over the mode shape
        for i in range(0,nmodes): 
            # Interpolate translation mode shapes
            # Translation in x
            fitresult = griddata(xyplot,-modeshapesx[:,i],(XX,YY), method='cubic')    
            # Mirror the mode shape to the other half-wing
            fitresult=np.concatenate((np.fliplr(fitresult),fitresult),axis=1)
            # Apply the same mode shape to both upper and lower surfaces
            fitresult=np.concatenate((np.flipud(fitresult),fitresult),axis=0)
            # Assign mode shape
            Phi_xall[:,i]=np.reshape(fitresult,2*m*n,order='C')
            # Translation in z
            fitresult = griddata(xyplot,-modeshapesy[:,i],(XX,YY), method='cubic')    
            # Mirror the mode shape to the other half-wing
            fitresult=np.concatenate((-np.fliplr(fitresult),fitresult),axis=1)
            # Apply the same mode shape to both upper and lower surfaces
            fitresult=np.concatenate((np.flipud(fitresult),fitresult),axis=0)
            # Assign mode shape
            Phi_yall[:,i]=np.reshape(fitresult,2*m*n,order='C')
            # Translation in z
            fitresult = griddata(xyplot,-modeshapesz[:,i],(XX,YY), method='cubic')    
            # Mirror the mode shape to the other half-wing
            fitresult=np.concatenate((np.fliplr(fitresult),fitresult),axis=1)
            # Apply the same mode shape to both upper and lower surfaces
            fitresult=np.concatenate((np.flipud(fitresult),fitresult),axis=0)
            # Assign mode shape
            Phi_zall[:,i]=np.reshape(fitresult,2*m*n,order='C')
            
            # Interpolate rotation mode shapes
            # Rotation around x
            fitresult = griddata(xyplot,-modeshapesRx[:,i],(XX,YY), method='cubic')    
            # Mirror the mode shape to the other half-wing
            fitresult=np.concatenate((-np.fliplr(fitresult),fitresult),axis=1)
            # Apply the same mode shape to both upper and lower surfaces
            fitresult=np.concatenate((np.flipud(fitresult),fitresult),axis=0)
            # Assign mode shape
            Phi_phiall[:,i]=np.reshape(fitresult,2*m*n,order='C')
            # Rotation around y
            fitresult = griddata(xyplot,-modeshapesRy[:,i],(XX,YY), method='cubic')    
            # Mirror the mode shape to the other half-wing
            fitresult=np.concatenate((np.fliplr(fitresult),fitresult),axis=1)
            # Apply the same mode shape to both upper and lower surfaces
            fitresult=np.concatenate((np.flipud(fitresult),fitresult),axis=0)
            # Assign mode shape
            Phi_thetaall[:,i]=np.reshape(fitresult,2*m*n,order='C')
            # Rotation around z
            fitresult = griddata(xyplot,-modeshapesRz[:,i],(XX,YY), method='cubic')    
            # Mirror the mode shape to the other half-wing
            fitresult=np.concatenate((-np.fliplr(fitresult),fitresult),axis=1)
            # Apply the same mode shape to both upper and lower surfaces
            fitresult=np.concatenate((np.flipud(fitresult),fitresult),axis=0)
            # Assign mode shape
            Phi_psiall[:,i]=np.reshape(fitresult,2*m*n,order='C')
        # End for    
        
        # Assign interpolated mode shapes to body struct array
        body['Phi_xall'][ibody]=Phi_xall
        body['Phi_yall'][ibody]=Phi_yall
        body['Phi_zall'][ibody]=Phi_zall
        body['Phi_phiall'][ibody]=Phi_phiall
        body['Phi_thetaall'][ibody]=Phi_thetaall
        body['Phi_psiall'][ibody]=Phi_psiall    
    # End for    
    
    return body


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package forcedbending contains one function to create the mode shapes for the
NASA TN D-344 test case

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
from scipy import linalg

def modes_NASATND344(mFE,nFE):
    # Calculates the mode shapes for the rectangular wing described in NASA TN
    # D344. The bending mode shape is assumed to be constant in the chordwise
    # direction. Only the bending mode shape and its derivative (pitch mode
    # shape) are non-zero.
    # This function is part of the SDPMflut Matlab distribution.
    # mFE: number of chordwise coordinates
    # nFE: number of spanwise coordinates
    # xxplot: (mFE*nFE)*1 array that contains the x coordinates of the structural model 
    # yyplot: (mFE*nFE)*1 array that contains the y coordinates of the structural model 
    # modeshapesx: (mFE*nFE)*nmodes array that contains the modal displacements
    # in the x direction.
    # modeshapesy: (mFE*nFE)*nmodes array that contains the modal displacements
    # in the y direction.
    # modeshapesz: (mFE*nFE)*nmodes array that contains the modal displacements
    # in the z direction.
    # modeshapesRx: (mFE*nFE)*nmodes array that contains the modal rotations
    # around the x axis.
    # modeshapesRy: (mFE*nFE)*nmodes array that contains the modal rotations
    # around the y axis.
    # modeshapesRz: (mFE*nFE)*nmodes array that contains the modal rotations
    
    # Bending mode data from:
    # Experimental determination of the pressure distribution on a rectangular
    # wing oscillating in the first bending mode for Mach numbers from 0.24 to
    # 1.3. H. C. Lessing, J. L. Troutman and G. P. Menees, NASA TN D-344, 1960
    bending_mode=np.array([(0.0, 0.0),
    (0.02936188255246979, 0.008426966292134797),
    (0.06711343524996272, 0.0196629213483146),
    (0.09648316962287706, 0.03370786516853941),
    (0.1272505280349249, 0.047752808988763995),
    (0.16222253629504, 0.0702247191011236),
    (0.19300167243775468, 0.0926966292134831),
    (0.22238318454133596, 0.1151685393258427),
    (0.2545638706334064, 0.1404494382022472),
    (0.2881461066748326, 0.1685393258426966),
    (0.314734333655258, 0.1924157303370787),
    (0.34832245856201766, 0.2247191011235955),
    (0.380514922384755, 0.2584269662921349),
    (0.40571141419138035, 0.2865168539325843),
    (0.4477029499289411, 0.3314606741573034),
    (0.47710016567341146, 0.3651685393258427),
    (0.5022986204351478, 0.3946629213483146),
    (0.5302962491853737, 0.4269662921348315),
    (0.5485046207963317, 0.4490561797752809),
    (0.5792955346697132, 0.4859550561797753),
    (0.6030944024372051, 0.5140449438202247),
    (0.6282948201540527, 0.5449438202247191),
    (0.654894824865145, 0.577247191011236),
    (0.6996953493667507, 0.6320224719101124),
    (0.7220965930951091, 0.6601123595505618),
    (0.7360963889477775, 0.6769662921348314),
    (0.7724974285288045, 0.7219101123595506),
    (0.8018985701834971, 0.7584269662921348),
    (0.8270989879003448, 0.7893258426966292),
    (0.8592993035435267, 0.8286516853932584),
    (0.8872988952488635, 0.8623595505617978),
    (0.9209007608414012, 0.9044943820224719),
    (0.9475007655524933, 0.9367977528089888),
    (0.9741007702635855, 0.9691011235955056),
    (1.0, 1.0)])
    
    # Obtain size of data
    ndata,_=bending_mode.shape
    
    # Fit bending mode shape by nth order polynomial with zero constant
    nord=5;
    RHS=bending_mode[:,1]
    LHS=np.zeros((ndata,nord))
    for i in range (0,nord):
        LHS[:,i]=bending_mode[:,0]**(i+1)
    # End for

    # Calculate polynomial coefficients
    acoeffs=linalg.solve(LHS.T@LHS,LHS.T@RHS)

    # Recalculate bending mode shape
    yy=np.linspace(0,1,num=nFE) 
    zz=np.zeros(nFE)
    for i in range (0,nord):
        zz=zz+acoeffs[i]*yy**(i+1)
    # End for
    # Calculate derivative of bending mode shape with respect to y
    zzdot=np.zeros(nFE)
    for i in range (0,nord):
        zzdot=zzdot+(i+1)*acoeffs[i]*yy**i
    # End for

    # Create FE grid
    xFE=np.linspace(0,1,num=mFE) 
    yFE=yy
    xxplot=np.matlib.repmat(np.reshape(xFE,(-1, 1)),1,nFE)*18*0.0254
    yyplot=np.matlib.repmat(np.reshape(yFE,(1, -1)),mFE,1)*27.44*0.0254
    # Create mode shapes
    modeshapesz=np.matlib.repmat(np.reshape(zz,(1, -1)),mFE,1)
    modeshapesx=np.zeros((mFE,nFE))
    modeshapesy=np.zeros((mFE,nFE))
    # modeshapesRx=-dz/dy
    modeshapesRx=np.matlib.repmat(np.reshape(zzdot,(1, -1)),mFE,1)
    # modeshapesRy=-dz/dx=0
    modeshapesRy=np.zeros((mFE,nFE))
    modeshapesRz=np.zeros((mFE,nFE))

    xxplot=np.reshape(xxplot,(mFE*nFE,1),order='C')
    yyplot=np.reshape(yyplot,(mFE*nFE,1),order='C')
    modeshapesx=np.reshape(modeshapesx,(mFE*nFE,1),order='C')
    modeshapesy=np.reshape(modeshapesy,(mFE*nFE,1),order='C')
    modeshapesz=np.reshape(modeshapesz,(mFE*nFE,1),order='C')
    modeshapesRx=np.reshape(modeshapesRx,(mFE*nFE,1),order='C')
    modeshapesRy=np.reshape(modeshapesRy,(mFE*nFE,1),order='C')
    modeshapesRz=np.reshape(modeshapesRz,(mFE*nFE,1),order='C')
    
    return xxplot, yyplot, modeshapesx, modeshapesy, modeshapesz, modeshapesRx, modeshapesRy, modeshapesRz

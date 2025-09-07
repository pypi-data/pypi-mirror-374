#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package flutsol contains functions to calculate flutter solutions using 
determinant iteration.

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
from scipy import linalg
from . import SDPMcalcs

def ABmx(kvec,k):
    # Calculates spline interpolation matrices in order to
    # interpolate the aerodynamic load matrices calculated at 
    # reduced frequencies kvec to reduced frequency k.
    # kvec: 1*nk vector of reduced frequency values
    # k: The desired reduced frequency value
    # Aint, Cint: Interpolation matrix and vector such that Q(k)=sum(C(i)*Q(:,:,kvec(i))) 
    #             with C=inv(Aint)*Bint
    
    # Calculate Aint matrix
    Aint=np.ones((kvec.size+1,kvec.size+1))
    Aint[kvec.size,kvec.size]=0;
    for i in range (0,kvec.size):
        for j in range (0,kvec.size):
            Aint[i,j]=np.absolute(kvec[i]-kvec[j])**3+np.absolute(kvec[i]+kvec[j])**3
    # Calculate Bint vector
    Bint=np.ones((kvec.size+1,1))
    dummy=np.absolute(k-kvec)**3+np.absolute(k+kvec)**3
    Bint[0:kvec.size]=dummy[:,None]
                    
    return Aint,Bint
    
def detiterfun(A,C,E,Q_0,Q_1,Q_2,kvec,Uv,bchar,rho,wn):
    # Solves the flutter problem for the SDPM using determinant iteration.
    # A: nmodes*nmodes structural mass matrix
    # C: nmodes*nmodes structural damping matrix
    # E: nmodes*nmodes structural stiffness matrix
    # Q_0: nmodes*nmodes*nk generalized aerodynamic stiffness matrix
    # calculated at nk values of the reduced frequency
    # Q_1: nmodes*nmodes*nk generalized aerodynamic damping matrix
    # calculated at nk values of the reduced frequency
    # Q_2: nmodes*nmodes*nk generalized aerodynamic mass matrix
    # calculated at nk values of the reduced frequency
    # kvec: 1*nk vector of reduced frequency values
    # Uini: Initial guess for the flutter airspeed
    # Uv: 1*nU vector of airspeed values 
    # bchar: characteristic length 
    # rho: air density 
    # wn: 1*nmodes vector of wind off natural frequencies
    # eigvals: nmodes*nU matrix of eigenvalues calculated at nU airspeeds
   
    # Small tolerance for calculating Jacobian numerically
    dx=1e-8
    # Determine number of modes
    nmodes=len(wn)
    # Initialize eigenvalue array
    eigvals=np.zeros((nmodes,Uv.size),dtype=complex)
    for imode in range (0,nmodes):
        # Set initial value of modal frequency
        w=wn[imode]
        # Calculate initial value of reduced frequency
        k=bchar*w/Uv[0]
        # Set initial value of modal damping
        preal=0.0
        for ivel in range (0,Uv.size):
            # Assign current value of airspeed
            U=Uv[ivel]           
            # Calculate dynamic pressure
            dynpress=1/2*rho*U**2
            # Condition for continuing iterations
            cond=1  
            while cond == 1:
                # Initialize Jacobian matrix
                Jac=np.zeros((2,2))
                # Interpolate generalized aerodynamic force matrix
                Aint,Bint=ABmx(kvec,k)
                Cint=linalg.solve(Aint,Bint)
                Q_0h=np.zeros((nmodes,nmodes),dtype=complex)
                Q_1h=np.zeros((nmodes,nmodes),dtype=complex)
                Q_2h=np.zeros((nmodes,nmodes),dtype=complex)
                for ik in range (0,kvec.size):
                    Q_0h=Q_0h+Cint[ik]*Q_0[ik,:,:]
                    Q_1h=Q_1h+Cint[ik]*Q_1[ik,:,:]
                    Q_2h=Q_2h+Cint[ik]*Q_2[ik,:,:]
                # Calculate complete eigenvalue
                p=preal+1j*k    
                # Calculate determinant of eigenvalue problem
                bigdet=linalg.det((A*U**2/bchar**2-dynpress*Q_2h)*p**2+(C*U/bchar-dynpress*Q_1h)*p+(E-dynpress*Q_0h))
                # Calculate objective function
                F=np.array([[bigdet.real],[bigdet.imag]])
                
                # Calculate derivative of objective function w.r.t. preal
                preal=preal+dx; # Increment preal
                # Calculate complete eigenvalue
                p=preal+1j*k;
                # Calculate determinant of eigenvalue problem
                bigdet=linalg.det((A*U**2/bchar**2-dynpress*Q_2h)*p**2+(C*U/bchar-dynpress*Q_1h)*p+(E-dynpress*Q_0h))
                # Calculate new objective function
                Fplus=np.array([[bigdet.real],[bigdet.imag]])
                # Calculate first column of Jacobian matrix
                dummy=(Fplus-F)/dx
                Jac[:,0]=dummy[:,0]
                preal=preal-dx; # Decrement preal
                
                # Calculate derivative of objective function w.r.t. k
                k=k+dx          # Increment k
                # Interpolate generalized aerodynamic force matrix
                Aint,Bint=ABmx(kvec,k)
                Cint=linalg.solve(Aint,Bint)
                Q_0h=np.zeros((nmodes,nmodes),dtype=complex)
                Q_1h=np.zeros((nmodes,nmodes),dtype=complex)
                Q_2h=np.zeros((nmodes,nmodes),dtype=complex)
                for ik in range (0,kvec.size):
                    Q_0h=Q_0h+Cint[ik]*Q_0[ik,:,:]
                    Q_1h=Q_1h+Cint[ik]*Q_1[ik,:,:]
                    Q_2h=Q_2h+Cint[ik]*Q_2[ik,:,:]
                # Calculate complete eigenvalue
                p=preal+1j*k    
                # Calculate determinant of eigenvalue problem
                bigdet=linalg.det((A*U**2/bchar**2-dynpress*Q_2h)*p**2+(C*U/bchar-dynpress*Q_1h)*p+(E-dynpress*Q_0h))
                # Calculate new objective function
                Fplus=np.array([[bigdet.real],[bigdet.imag]])
                # Calculate second column of Jacobian matrix
                dummy=(Fplus-F)/dx
                Jac[:,1]=dummy[:,0]
                k=k-dx          # Decrement k
                
                # Solve Newton-Raphson problem
                solvec=-linalg.solve(Jac,F)
                # Calculate convergence criterion
                crit=np.dot(solvec.T,solvec)
                
                # Update preal
                preal=preal+np.take(solvec[0],0) # Converting elements of arrays to scalars is a pain!
                # Update k
                k=k+np.take(solvec[1],0)
                # Check for convergence
                if crit < 1e-6:
                    cond=0
            # Store converged eigenvalue for the current mode and airspeed
            eigvals[imode,ivel]=U/bchar*(preal+1j*k)
            
    return eigvals

def pkmethod(A,C,E,Q,kvec,Uv,bchar,rho,wn):
    # Solves the flutter problem for the SDPM using determinant iteration.
    # A: nmodes*nmodes structural mass matrix
    # C: nmodes*nmodes structural damping matrix
    # E: nmodes*nmodes structural stiffness matrix
    # Q: nmodes*nmodes*nk generalized aerodynamic load matrix
    # calculated at nk values of the reduced frequency
    # kvec: 1*nk vector of reduced frequency values
    # Uini: Initial guess for the flutter airspeed
    # Uv: 1*nU vector of airspeed values 
    # bchar: characteristic length 
    # rho: air density 
    # wn: 1*nmodes vector of wind off natural frequencies
    # eigvals: nmodes*nU matrix of eigenvalues calculated at nU airspeeds
   
    # Determine number of modes
    nmodes=len(wn)
    # Initialize eigenvalue array
    eigvals=np.zeros((nmodes,Uv.size),dtype=complex)
    for imode in range (0,nmodes):
        # Set initial value of modal frequency
        w=wn[imode]
        # Calculate initial value of reduced frequency
        k=bchar*w/Uv[0]
        for ivel in range (0,Uv.size):
            # Assign current value of airspeed
            U=Uv[ivel]           
            # Calculate dynamic pressure
            dynpress=1.0/2.0*rho*U**2
            # Condition for continuing iterations
            cond=1  
            while cond == 1:
                # Interpolate generalized aerodynamic force matrix
                Aint,Bint=ABmx(kvec,k)
                Cint=linalg.solve(Aint,Bint)
                Qh=np.zeros((nmodes,nmodes),dtype=complex)
                for ik in range (0,kvec.size):
                    Qh=Qh+Cint[ik]*Q[ik,:,:]
                # End if
                # Calculate aerodynamic stiffness
                Qr=dynpress*np.real(Qh)  
                # Calculate aerodynamic damping
                Qi=1.0/2.0*rho*bchar*U*np.imag(Qh)/k
                # Set up the eigenvalue problem
                line1=np.concatenate((np.zeros((nmodes,nmodes)),np.eye(nmodes)),axis=1)
                line2=np.concatenate((-linalg.solve(A,E-Qr),-linalg.solve(A,C-Qi)),axis=1)
                eigprob=np.concatenate((line1,line2),axis=0)
                # Solve the eigenvalue problem
                ptem,_=linalg.eig(eigprob)
                # Select only one of each pair of conjugate eigenvalues
                ptem=ptem[np.arange(0, 2*nmodes, 2, dtype=int)]
                # Sort the eigenvalues
                ptem=np.sign(np.imag(ptem))*ptem
                I=np.argsort(np.imag(ptem))
                ptem=ptem[I]
                # Calculate the new reduced frequency for this mode
                knew=bchar*np.imag(ptem[imode])/U
                # Compute difference between previous and current frequency
                kdiff=abs(knew-k)
                # Update reduced frequency
                k=knew
                # Check for convergence
                if kdiff < 1e-6:
                    cond=0
            # Store converged eigenvalue for the current mode and airspeed
            eigvals[imode,ivel]=ptem[imode]
            
    return eigvals

def flutfind(A,C,E,Q_0,Q_1,Q_2,kvec,Uini,bchar,rho,wini):
    # Calculates exactly the flutter speed of the flutter equation, given an
    # initial guess Uini, wini.
    # A: nmodes*nmodes structural mass matrix
    # C: nmodes*nmodes structural damping matrix
    # E: nmodes*nmodes structural stiffness matrix
    # Q_0: nmodes*nmodes*nk generalized aerodynamic stiffness matrix
    # calculated at nk values of the reduced frequency
    # Q_1: nmodes*nmodes*nk generalized aerodynamic damping matrix
    # calculated at nk values of the reduced frequency
    # Q_2: nmodes*nmodes*nk generalized aerodynamic mass matrix
    # calculated at nk values of the reduced frequency
    # kvec: 1*nk vector of reduced frequency values
    # Uini: Initial guess for the flutter airspeed
    # Uv: 1*nU vector of airspeed values 
    # bchar: characteristic length 
    # rho: air density 
    # wini: Initial guess for the flutter frequency 
    # U: flutter speed (m/s)
    # w: flutter frequency (rad/s)
   
    # Small tolerance for calculating Jacobian numerically
    dx=1e-8
    # Determine number of modes
    nmodes=A.shape[0]
    # Assign initial guess  for the flutter airspeed
    U=Uini
    # Assign initial guess  for the flutter frequency
    w=wini
    # Condition for continuing iterations
    cond=1  
    while cond == 1:
        # Calculate reduced frequency
        k=bchar*w/U
        # Calculate dynamic pressure
        dynpress=1/2*rho*U**2
        # Initialize Jacobian matrix
        Jac=np.zeros((2,2))
        # Interpolate generalized aerodynamic force matrix
        Aint,Bint=ABmx(kvec,k)
        Cint=linalg.solve(Aint,Bint)
        Q_0h=np.zeros((nmodes,nmodes),dtype=complex)
        Q_1h=np.zeros((nmodes,nmodes),dtype=complex)
        Q_2h=np.zeros((nmodes,nmodes),dtype=complex)
        for ik in range (0,kvec.size):
            Q_0h=Q_0h+Cint[ik]*Q_0[ik,:,:]
            Q_1h=Q_1h+Cint[ik]*Q_1[ik,:,:]
            Q_2h=Q_2h+Cint[ik]*Q_2[ik,:,:]
        # At flutter the eigenvalue has zero real part    
        p=1j*k
        # Calculate determinant of eigenvalue problem
        bigdet=linalg.det((A*U**2/bchar**2-dynpress*Q_2h)*p**2+(C*U/bchar-dynpress*Q_1h)*p+(E-dynpress*Q_0h))
        # Calculate objective function
        F=np.array([[bigdet.real],[bigdet.imag]])

        # Calculate derivative of objective function w.r.t. U
        U=U+dx      # Increment U
        k=bchar*w/U # Calculate new reduced frequency
        dynpress=1/2*rho*U**2 # Calculate new dynamic pressure
        # Interpolate generalized aerodynamic force matrix
        Aint,Bint=ABmx(kvec,k)
        Cint=linalg.solve(Aint,Bint)
        Q_0h=np.zeros((nmodes,nmodes),dtype=complex)
        Q_1h=np.zeros((nmodes,nmodes),dtype=complex)
        Q_2h=np.zeros((nmodes,nmodes),dtype=complex)
        for ik in range (0,kvec.size):
            Q_0h=Q_0h+Cint[ik]*Q_0[ik,:,:]
            Q_1h=Q_1h+Cint[ik]*Q_1[ik,:,:]
            Q_2h=Q_2h+Cint[ik]*Q_2[ik,:,:]
        # At flutter the eigenvalue has zero real part    
        p=1j*k
        # Calculate determinant of eigenvalue problem
        bigdet=linalg.det((A*U**2/bchar**2-dynpress*Q_2h)*p**2+(C*U/bchar-dynpress*Q_1h)*p+(E-dynpress*Q_0h))
        # Calculate new objective function
        Fplus=np.array([[bigdet.real],[bigdet.imag]])
        # Calculate second column of Jacobian matrix
        dummy=(Fplus-F)/dx
        Jac[:,0]=dummy[:,0]
        U=U-dx      # Decrement U
        dynpress=1/2*rho*U**2 # Recalculate original dynamic pressure
        
        # Calculate derivative of objective function w.r.t. w
        w=w+dx;     # Increment w
        k=bchar*w/U # Calculate new reduced frequency
        # Interpolate generalized aerodynamic force matrix
        Aint,Bint=ABmx(kvec,k)
        Cint=linalg.solve(Aint,Bint)
        Q_0h=np.zeros((nmodes,nmodes),dtype=complex)
        Q_1h=np.zeros((nmodes,nmodes),dtype=complex)
        Q_2h=np.zeros((nmodes,nmodes),dtype=complex)
        for ik in range (0,kvec.size):
            Q_0h=Q_0h+Cint[ik]*Q_0[ik,:,:]
            Q_1h=Q_1h+Cint[ik]*Q_1[ik,:,:]
            Q_2h=Q_2h+Cint[ik]*Q_2[ik,:,:]
        # At flutter the eigenvalue has zero real part    
        p=1j*k
        # Calculate determinant of eigenvalue problem
        bigdet=linalg.det((A*U**2/bchar**2-dynpress*Q_2h)*p**2+(C*U/bchar-dynpress*Q_1h)*p+(E-dynpress*Q_0h))
        Fplus=np.array([[bigdet.real],[bigdet.imag]])
        # Calculate second column of Jacobian matrix
        dummy=(Fplus-F)/dx
        Jac[:,1]=dummy[:,0]
        w=w-dx;     # Decrement w
 
        # Solve Newton-Raphson problem
        solvec=-linalg.solve(Jac,F)
        # Calculate convergence criterion
        crit=np.dot(solvec.T,solvec)

        # Update U
        U=U+np.take(solvec[0],0) # Converting elements of arrays to scalars is a pain!
        # Update w
        w=w+np.take(solvec[1],0)
        # Check for convergence
        if crit < 1e-6:
            cond=0
            
    return U,w

def flutsolve_flex(body,allbodies,kvec,Uv,nmodes,Aphi,Bphi,Cphi,barUinf,barVinf,barWinf,c0,Mach,beta,cp_order,A,C,E,rho,wn,halfwing,install_dir):
    # Calculates the flutter solution for the bodies described in struct array
    # body, given flexible structural modal matrices and mode shapes.
    # This function is part of the SDPMflut Matlab distribution.
    # body: struct array containing the geometry of all the bodies in the flow.
    #       Each element of body describes a different wing, fairing or 
    #       fuselage
    # allbodies: struct array containing concatenated information for all the
    #       bodies
    # kvec: Vector of reduced frequencies at which to calculate the unsteady
    #       pressure distribution
    # Uv: Vector of free stream airspeeds at which to calculate the natural
    #       frequencies and damping ratios of the aeroelastic system
    # nmodes: Number of modes in the structural model
    # Aphi: Steady body-on-body source influence coefficients
    # Bphi: Steady body-on-body doublet influence coefficients
    # Cphi: Steady wake-on-body doublet influence coefficients
    # barUinf: Component of non-dimensional free stream velocity in the x 
    #       direction
    # barVinf: Component of non-dimensional free stream velocity in the y 
    #       direction
    # barWinf: Component of non-dimensional free stream velocity in the z 
    #       direction 
    # c0: Characteristic chord length
    # Mach: Free stream Mach number
    # beta: Subsonic compressibility factor
    # cp_order: Order of pressure calculation. cp_order=1: first order
    #       calculation. cp_order=2: second order calculation
    # A: Structural mass matrix
    # C: Structural damping matrix
    # E: Structural stiffness matrix
    # rho: Free stream density
    # wn: wind-off natural frequencies
    # halfwing: Parameter to determine if the structural model concerns a half 
    #       wing or a full wing.  halfwing=1: half-wing. halfwing=0: full wing
    # install_dir: Path to ./Common directory
    # Uflut: Flutter airspeed
    # freqflut: Flutter frequency
    # kflut: Reduced flutter frequency
    # dynpressflut: Flutter dynamic pressure
    # omega: Natural frequencies at airspeeds Uv
    # zeta: Damping ratios at airspeeds Uv

    # Calculate steady generalized aerodynamic load vector
    Q0=allbodies['Phi_xall'][0].T@allbodies['Fx0'][0]+allbodies['Phi_yall'][0].T@allbodies['Fy0'][0] \
        +allbodies['Phi_zall'][0].T@allbodies['Fz0'][0] 
    if halfwing == 1:
        # Divide steady generalized aerodynamic load vector by 2 because the
        # structural model is a half-wing
        Q0=Q0/2.0
    # End if
    
    # Initialize arrays for unsteady generalized force matrices
    Q1=np.zeros((kvec.size,nmodes,nmodes),dtype=complex)
    Q_0=np.zeros((kvec.size,nmodes,nmodes),dtype=complex)
    Q_1=np.zeros((kvec.size,nmodes,nmodes),dtype=complex)
    Q_2=np.zeros((kvec.size,nmodes,nmodes),dtype=complex)
    
    print('Calculating generalized aerodynamic force matrix at '+str(len(kvec))+' requested frequencies')
    for ik in range (0,kvec.size):
        print('Frequency '+str(ik+1))
        k=kvec[ik]
        
        # Calculate the unsteady pressure coefficients
        cp1,cp_0,cp_1,cp_2=SDPMcalcs.unsteadysolve_flex(body,allbodies,Aphi,Bphi,Cphi,barUinf,barVinf,barWinf,k,c0,Mach,beta,cp_order,install_dir)
        
        # Calculate total unsteady aerodynamic loads on the panels
        Fx1,Fy1,Fz1,_,_,_=SDPMcalcs.aeroforces(cp1,allbodies['nx0all'][0],allbodies['ny0all'][0],allbodies['nz0all'][0], \
                                               allbodies['s0all'][0],allbodies['Xc0all'][0],allbodies['Yc0all'][0],allbodies['Zc0all'][0], \
                                               0.0,0.0,0.0)
        # Calculate total unsteady generalized aerodynamic load matrix    
        Q1[ik,:,:]=allbodies['Phi_xall'][0].T@Fx1+allbodies['Phi_yall'][0].T@Fy1+allbodies['Phi_zall'][0].T@Fz1 
            
        # Calculate unsteady aerodynamic stiffness loads on the panels
        Fx1,Fy1,Fz1,_,_,_=SDPMcalcs.aeroforces(cp_0,allbodies['nx0all'][0],allbodies['ny0all'][0],allbodies['nz0all'][0], \
                                               allbodies['s0all'][0],allbodies['Xc0all'][0],allbodies['Yc0all'][0],allbodies['Zc0all'][0], \
                                               0.0,0.0,0.0)
        # Calculate unsteady generalized aerodynamic stiffness matrix    
        Q_0[ik,:,:]=allbodies['Phi_xall'][0].T@Fx1+allbodies['Phi_yall'][0].T@Fy1+allbodies['Phi_zall'][0].T@Fz1 

        # Calculate unsteady aerodynamic damping loads on the panels
        Fx1,Fy1,Fz1,_,_,_=SDPMcalcs.aeroforces(cp_1,allbodies['nx0all'][0],allbodies['ny0all'][0],allbodies['nz0all'][0], \
                                               allbodies['s0all'][0],allbodies['Xc0all'][0],allbodies['Yc0all'][0],allbodies['Zc0all'][0], \
                                               0.0,0.0,0.0)
        # Calculate unsteady generalized aerodynamic damping matrix    
        Q_1[ik,:,:]=allbodies['Phi_xall'][0].T@Fx1+allbodies['Phi_yall'][0].T@Fy1+allbodies['Phi_zall'][0].T@Fz1 

        # Calculate unsteady aerodynamic mass loads on the panels
        Fx1,Fy1,Fz1,_,_,_=SDPMcalcs.aeroforces(cp_2,allbodies['nx0all'][0],allbodies['ny0all'][0],allbodies['nz0all'][0], \
                                               allbodies['s0all'][0],allbodies['Xc0all'][0],allbodies['Yc0all'][0],allbodies['Zc0all'][0], \
                                               0.0,0.0,0.0)
        # Calculate unsteady generalized aerodynamic mass matrix    
        Q_2[ik,:,:]=allbodies['Phi_xall'][0].T@Fx1+allbodies['Phi_yall'][0].T@Fy1+allbodies['Phi_zall'][0].T@Fz1 
    # End for
    
    if halfwing == 1:
        # Divide steady generalized aerodynamic load vector by 2 because the
        # structural model is a half-wing
        Q1=Q1/2.0
        Q_0=Q_0/2.0
        Q_1=Q_1/2.0
        Q_2=Q_2/2.0
    # End if
    
    # Calculate eigenvalues using determinant iteration
    eigvals=detiterfun(A,C,E,Q_0,Q_1,Q_2,kvec,Uv,c0/2,rho,wn)
    # Calculate natural frequencies and damping ratios
    omega=np.absolute(eigvals)
    zeta=-eigvals.real/np.absolute(eigvals)    

    # Calculate indices of first point after flutter 
    ijflut=np.argwhere(zeta < 0.0)
    
    # Calculate exact flutter point, if there is one
    if ijflut.size != 0:
        # Find velocity index of first point after flutter
        jmin=np.min(ijflut[:,1])
        # Find mode index of first point after flutter
        imin=np.argwhere(ijflut[:,1] == jmin)
        imin=ijflut[np.take(imin[0],0),0]
        # Retrieve velocity of first point after flutter
        Uini=Uv[jmin-1]
        # Retrieve frequency of first point after flutter
        wini=np.imag(eigvals[imin,jmin-1]) 
        # Calculate exact flutter velocity and frequency
        Uflut,freqflut=flutfind(A,C,E,Q_0,Q_1,Q_2,kvec,Uini,c0/2.0,rho,wini)
        # Calculate flutter reduced frequency
        kflut=freqflut*c0/2.0/Uflut
        # Calculate flutter dynamic pressure
        dynpressflut=1/2.0*rho*Uflut**2.0
    else:
        # Set all outputs to zero
        Uflut=0.0
        freqflut=0.0
        kflut=0.0
        dynpressflut=0.0
    # End if
    
    return Uflut,freqflut,kflut,dynpressflut,omega,zeta

def flutsolve_pitchplunge(body,allbodies,kvec,Uv,nmodes,Aphi,Bphi,Cphi,barUinf,barVinf,barWinf,c0,Mach,beta,cp_order,A,C,E,rho,wn,halfwing,xf0,yf0,zf0,install_dir):
    # Calculates the flutter solution for the bodies described in struct array
    # body, given rigid pitch plunge structural matrices.
    # body: struct array containing the geometry of all the bodies in the flow.
    #       Each element of body describes a different wing, fairing or 
    #       fuselage
    # allbodies: struct array containing concatenated information for all the
    #       bodies
    # kvec: Vector of reduced frequencies at which to calculate the unsteady
    #       pressure distribution
    # Uv: Vector of free stream airspeeds at which to calculate the natural
    #       frequencies and damping ratios of the aeroelastic system
    # nmodes: Number of modes in the structural model
    # Aphi: Steady body-on-body source influence coefficients
    # Bphi: Steady body-on-body doublet influence coefficients
    # Cphi: Steady wake-on-body doublet influence coefficients
    # barUinf: Component of non-dimensional free stream velocity in the x 
    #       direction
    # barVinf: Component of non-dimensional free stream velocity in the y 
    #       direction
    # barWinf: Component of non-dimensional free stream velocity in the z 
    #       direction 
    # c0: Characteristic chord length
    # Mach: Free stream Mach number
    # beta: Subsonic compressibility factor
    # cp_order: Order of pressure calculation. cp_order=1: first order
    #       calculation. cp_order=2: second order calculation
    # A: Structural mass matrix
    # C: Structural damping matrix
    # E: Structural stiffness matrix
    # rho: Free stream density
    # wn: wind-off natural frequencies
    # halfwing: Parameter to determine if the structural model concerns a half 
    #       wing or a full wing.  halfwing=1: half-wing. halfwing=0: full wing
    # xf0,yf0,zf0: Position of pitch axis in Cartesian coordinates
    # install_dir: Path to ./Common directory
    # Uflut: Flutter airspeed
    # freqflut: Flutter frequency
    # kflut: Reduced flutter frequency
    # dynpressflut: Flutter dynamic pressure
    # omega: Natural frequencies at airspeeds Uv
    # zeta: Damping ratios at airspeeds Uv
    
    # Apply Prandtl-Glauert transformation to pitch centre
    xf=xf0/beta
    yf=yf0
    zf=zf0
    
    # Calculate steady aerodynamic loads on the panels
    Fx0,Fy0,Fz0,Mx0,My0,Mz0=SDPMcalcs.aeroforces(allbodies['cp0'][0],allbodies['nx0all'][0],allbodies['ny0all'][0],allbodies['nz0all'][0], \
                                           allbodies['s0all'][0],allbodies['Xc0all'][0],allbodies['Yc0all'][0],allbodies['Zc0all'][0], \
                                           xf0,yf0,zf0)    
    # Calculate steady generalized aerodynamic load vector
    Q0=np.array([[-np.sum(Fz0)],[np.sum(My0)]])   
    if halfwing == 1:
        # Divide steady generalized aerodynamic load vector by 2 because the
        # structural model is a half-wing
        Q0=Q0/2.0
    # End if

    # Initialize arrays for unsteady generalized force matrices
    Q1=np.zeros((kvec.size,nmodes,nmodes),dtype=complex)
    Q_0=np.zeros((kvec.size,nmodes,nmodes),dtype=complex)
    Q_1=np.zeros((kvec.size,nmodes,nmodes),dtype=complex)
    Q_2=np.zeros((kvec.size,nmodes,nmodes),dtype=complex)

    print('Calculating generalized aerodynamic force matrix at '+str(len(kvec))+' requested frequencies')
    for ik in range (0,kvec.size):
        print('Frequency '+str(ik+1))
        k=kvec[ik]
        
        # Calculate the unsteady pressure coefficients
        cpalpha,cphdot,cpalphadot,cph2dot,cpalpha2dot=SDPMcalcs.unsteadysolve_pitchplunge(body,allbodies,Aphi,Bphi,Cphi,barUinf,barVinf,barWinf,k,c0,Mach,beta,cp_order,xf,yf,zf,install_dir)
        
        # Calculate unsteady aerodynamic loads on the panels
        Fxalpha,Fyalpha,Fzalpha,Mxalpha,Myalpha,Mzalpha=SDPMcalcs.aeroforces(cpalpha,allbodies['nx0all'][0],allbodies['ny0all'][0], \
                                               allbodies['nz0all'][0],allbodies['s0all'][0],allbodies['Xc0all'][0],allbodies['Yc0all'][0], \
                                               allbodies['Zc0all'][0],xf0,yf0,zf0)    
        Fxhdot,Fyhdot,Fzhdot,Mxhdot,Myhdot,Mzhdot=SDPMcalcs.aeroforces(cphdot,allbodies['nx0all'][0],allbodies['ny0all'][0], \
                                               allbodies['nz0all'][0],allbodies['s0all'][0],allbodies['Xc0all'][0],allbodies['Yc0all'][0], \
                                               allbodies['Zc0all'][0],xf0,yf0,zf0)         
        Fxalphadot,Fyalphadot,Fzalphadot,Mxalphadot,Myalphadot,Mzalphadot=SDPMcalcs.aeroforces(cpalphadot,allbodies['nx0all'][0],allbodies['ny0all'][0], \
                                               allbodies['nz0all'][0],allbodies['s0all'][0],allbodies['Xc0all'][0],allbodies['Yc0all'][0], \
                                               allbodies['Zc0all'][0],xf0,yf0,zf0)  
        Fxh2dot,Fyh2dot,Fzh2dot,Mxh2dot,Myh2dot,Mzh2dot=SDPMcalcs.aeroforces(cph2dot,allbodies['nx0all'][0],allbodies['ny0all'][0], \
                                               allbodies['nz0all'][0],allbodies['s0all'][0],allbodies['Xc0all'][0],allbodies['Yc0all'][0], \
                                               allbodies['Zc0all'][0],xf0,yf0,zf0)  
        Fxalpha2dot,Fyalpha2dot,Fzalpha2dot,Mxalpha2dot,Myalpha2dot,Mzalpha2dot=SDPMcalcs.aeroforces(cpalpha2dot,allbodies['nx0all'][0],allbodies['ny0all'][0], \
                                               allbodies['nz0all'][0],allbodies['s0all'][0],allbodies['Xc0all'][0],allbodies['Yc0all'][0], \
                                               allbodies['Zc0all'][0],xf0,yf0,zf0)             
        # Calculate unsteady generalized aerodynamic stiffness matrix    
        Q_0[ik,:,:]=np.array([[0, -np.sum(Fzalpha)],[0, np.sum(Myalpha)]])  
        # Calculate unsteady generalized aerodynamic damping matrix    
        Q_1[ik,:,:]=np.array([[-np.sum(Fzhdot), -np.sum(Fzalphadot)],[np.sum(Myhdot), np.sum(Myalphadot)]])  
        # Calculate unsteady generalized aerodynamic mass matrix    
        Q_2[ik,:,:]=np.array([[-np.sum(Fzh2dot), -np.sum(Fzalpha2dot)],[np.sum(Myh2dot), np.sum(Myalpha2dot)]])  
        # Calculate total unsteady generalized aerodynamic load matrix    
        Q1[ik,:,:]=Q_0[ik,:,:]+1j*k*Q_1[ik,:,:]+(1j*k)**2.0*Q_2[ik,:,:]      
    # End for

    if halfwing == 1:
        # Divide steady generalized aerodynamic load vector by 2 because the
        # structural model is a half-wing
        Q1=Q1/2.0
        Q_0=Q_0/2.0
        Q_1=Q_1/2.0
        Q_2=Q_2/2.0
    # End if

    # Calculate eigenvalues using determinant iteration
    eigvals=detiterfun(A,C,E,Q_0,Q_1,Q_2,kvec,Uv,c0/2,rho,wn)
    # Calculate natural frequencies and damping ratios
    omega=np.absolute(eigvals)
    zeta=-eigvals.real/np.absolute(eigvals)    

    # Calculate indices of first point after flutter 
    ijflut=np.argwhere(zeta < 0.0)
    
    # Calculate exact flutter point, if there is one
    if ijflut.size != 0:
        # Find velocity index of first point after flutter
        jmin=np.min(ijflut[:,1])
        # Find mode index of first point after flutter
        imin=np.argwhere(ijflut[:,1] == jmin)
        imin=ijflut[np.take(imin[0],0),0]
        # Retrieve velocity of first point after flutter
        Uini=Uv[jmin-1]
        # Retrieve frequency of first point after flutter
        wini=np.imag(eigvals[imin,jmin-1]) 
        # Calculate exact flutter velocity and frequency
        Uflut,freqflut=flutfind(A,C,E,Q_0,Q_1,Q_2,kvec,Uini,c0/2.0,rho,wini)
        # Calculate flutter reduced frequency
        kflut=freqflut*c0/2.0/Uflut
        # Calculate flutter dynamic pressure
        dynpressflut=1/2.0*rho*Uflut**2.0
    else:
        # Set all outputs to zero
        Uflut=0.0
        freqflut=0.0
        kflut=0.0
        dynpressflut=0.0
    # End if
    
    return Uflut,freqflut,kflut,dynpressflut,omega,zeta
        
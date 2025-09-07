/*
 * C function sdpminf_unsteady_subsonicso.c -
 *
 * Calculates the unsteady influence coefficient matrices for the 
 * compressible Source and Doublet Panel Method.
 *
 * Inputs:
 * xc: mc*nc matrix of x-coordinates of influenced panel control points
 * yc: mc*nc matrix of y-coordinates of influenced panel control points
 * zc: mc*nc matrix of z-coordinates of influenced panel control points
 * xv: mv*nv matrix of x-coordinates of influencing wing panel control points
 * yv: mv*nv matrix of y-coordinates of influencing wing panel control points
 * zv: mv*nv matrix of z-coordinates of influencing wing panel control points
 * nx: mv*nv matrix of x-components of unite vectors normal to the 
 *     influencing panels
 * xcw: mw*nw matrix of x-coordinates of influencing wake panel control points
 * ycw: mw*nw matrix of y-coordinates of influencing wake panel control points
 * zcw: mw*nw matrix of z-coordinates of influencing wake panel control points
 * Aphi: (mc*nc)*(mv*nv) matrix of steady source influence coefficients of
 *       wing panels on wing control points
 * Bphi: (mc*nc)*(mv*nv) matrix of steady doublet influence coefficients of
 *       wing panels on wing control points
 * Cphi: (mc*nc)*(mw*nw) matrix of steady doublet influence coefficients of
 *       wake panels on wing control points
 * params: 1*2 vector of parameters. The first element is the scaled 
 *         frequency Omega and the second the free stream Mach number.
 * Abarphi_real: (mc*nc)*(mv*nv) matrix of real parts of unsteady source 
 *               influence coefficients of wing panels on wing control points
 * Abarphi_imag: (mc*nc)*(mv*nv) matrix of iaginary parts of unsteady source 
 *               influence coefficients of wing panels on wing control points
 * Bbarphi_real: (mc*nc)*(mv*nv) matrix of real parts of unsteady doublet 
 *               influence coefficients of wing panels on wing control points
 * Bbarphi_imag: (mc*nc)*(mv*nv) matrix of imaginary parts of unsteady doublet 
 *               influence coefficients of wing panels on wing control points
 * Cbarphi_real: (mc*nc)*(mw*nw) matrix of real parts of unsteady doublet 
 *               influence coefficients of wing panels on wing control points
 * Cbarphi_imag: (mc*nc)*(mw*nw) matrix of imaginary parts of unsteady doublet 
 *               influence coefficients of wake panels on wing control points
 *
 * Outputs: This code does not return any outputs. The results of its 
 *          calculations are stored in input matrices Abarphi_real,
 *          Abarphi_imag, Bbarphi_real, Bbarphi_imag, Cbarphi_real and
 *          Cbarphi_imag.
 * NB: All matrices must have compatible dimensions
 *
 * Compile this by typing at the terminal 
 * gcc -fPIC -shared -o sdpminf_unsteady_subsonicso.so sdpminf_unsteady_subsonicso.c
 *
 * This is a C language file to be used with the SDPMflut 
 * distribution.
 * Copyright (C) 2024 Grigorios Dimitriadis 
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 * 
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#include "math.h"

void sdpminf_unsteady_subsonic(double *xc, double *yc, double *zc, 
			double *xcv, double *ycv, double *zcv,double *nx,
			double *xcw, double *ycw, double *zcw, 
			double *Aphi, double *Bphi, double *Cphi, double * params,
			int mc, int nc, int mv, int nv, int mw, int nw, 
			double * Abarphi_real, double * Abarphi_imag, double * Bbarphi_real, double * Bbarphi_imag, 
			double * Cbarphi_real, double * Cbarphi_imag)
{			
    double Omega,Mach,Dx,Dy,Dz,R,exparg,expreal,expimag;
    double exp1real,exp1imag,exp2real,exp2imag,OmegaMachnx;
    int    mvnv,mwnw,ic,jc,iv,jv,ik;

    /* Assign value of frequency */
    Omega=*params;
    /* Assign value of Mach number */
    Mach=*(params+1);
    /* Size of influencing body matrix */
    mvnv=mv*nv;
    /* Size of influencing wake matrix */
    mwnw=mw*nw;
    
    /* Create influence coefficient matrices */
    /* Cycle through influenced points */
    for (ic=0; ic < mc; ic++) {
        for (jc=0; jc < nc; jc++) {
            /* Cycle through influencing wing panels */
            for (iv=0; iv < mv; iv++) {
                for (jv=0; jv < nv; jv++) {
                    /* Caclulate distance between influenced and influencing
                     * control points */
                    Dx=*(xc+ic*nc+jc) - *(xcv+iv*nv+jv); /* x-direction */
                    Dy=*(yc+ic*nc+jc) - *(ycv+iv*nv+jv); /* y-direction */
                    Dz=*(zc+ic*nc+jc) - *(zcv+iv*nv+jv); /* z-direction */
                    R=sqrt(Dx*Dx+Dy*Dy+Dz*Dz);          /* Total distance */
                    /* Calculate exponential term in equation 6.81 */
                    exparg=-Mach*Dx+R;
                    expreal=cos(-Omega*exparg);
                    expimag=sin(-Omega*exparg);
                    /* Calculate unsteady source influence coefficient matrix from  equation 6.81 */
                    *(Abarphi_real+(ic*nc+jc)*mvnv+(iv*nv+jv))=*(Aphi+(ic*nc+jc)*mvnv+(iv*nv+jv))*expreal;
                    *(Abarphi_imag+(ic*nc+jc)*mvnv+(iv*nv+jv))=*(Aphi+(ic*nc+jc)*mvnv+(iv*nv+jv))*expimag;
                    /* Calculate the two coefficients of equation 6.82 */
                    exp1real=expreal-expimag*Omega*R;
                    exp1imag=expimag+expreal*Omega*R;
                    OmegaMachnx=Omega*Mach* *(nx+iv*nv+jv);
                    exp2real=expimag*OmegaMachnx;
                    exp2imag=-expreal*OmegaMachnx;
                    /* Calculate unsteady doublet influence coefficient matrix from  equation 6.82 */
                    *(Bbarphi_real+(ic*nc+jc)*mvnv+(iv*nv+jv))= *(Bphi+(ic*nc+jc)*mvnv+(iv*nv+jv))*exp1real+ *(Aphi+(ic*nc+jc)*mvnv+(iv*nv+jv))*exp2real;
                    *(Bbarphi_imag+(ic*nc+jc)*mvnv+(iv*nv+jv))= *(Bphi+(ic*nc+jc)*mvnv+(iv*nv+jv))*exp1imag+ *(Aphi+(ic*nc+jc)*mvnv+(iv*nv+jv))*exp2imag;
               }
            }
            /* Cycle through influencing wake panels */
            for (iv=0; iv < mw; iv++) {
                for (jv=0; jv < nw; jv++) {
                    /* Caclulate distance between influenced and influencing
                     * control points */
                    Dx=*(xc+ic*nc+jc) - *(xcw+iv*nw+jv); /* x-direction */
                    Dy=*(yc+ic*nc+jc) - *(ycw+iv*nw+jv); /* y-direction */
                    Dz=*(zc+ic*nc+jc) - *(zcw+iv*nw+jv); /* z-direction */
                    R=sqrt(Dx*Dx+Dy*Dy+Dz*Dz);          /* Total distance */
                    /* Calculate exponential term in equation 6.81 */
                    exparg=-Mach*Dx+R;
                    expreal=cos(-Omega*exparg);
                    expimag=sin(-Omega*exparg);
                    /* Calculate the coefficient of equation 6.83 */
                    exp1real=expreal-expimag*Omega*R;
                    exp1imag=expimag+expreal*Omega*R;
                    /* Calculate unsteady doublet influence coefficient matrix from  equation 6.83 */
                    *(Cbarphi_real+(ic*nc+jc)*mwnw+(iv*nw+jv))=*(Cphi+(ic*nc+jc)*mwnw+(iv*nw+jv))*exp1real;
                    *(Cbarphi_imag+(ic*nc+jc)*mwnw+(iv*nw+jv))=*(Cphi+(ic*nc+jc)*mwnw+(iv*nw+jv))*exp1imag;
                }
            }
        }
    }
}
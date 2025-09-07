/*
 * C function sdpminfso.c -
 *
 * Calculates influence coefficient matrices for the Source and Doublet
 * Panel Method.
 *
 * Inputs:
 * xc: mc*nc matrix of x-coordinates of points on which the influence
 *     is to be calculated
 * yc: mc*nc matrix of y-coordinates of points on which the influence
 *     is to be calculated
 * zc: mc*nc matrix of z-coordinates of points on which the influence
 *     is to be calculated
 * xp: mv*nv matrix of x-coordinates of vertices of influencing panels
 * yp: mv*nv matrix of y-coordinates of vertices of influencing panels
 * zp: mv*nv matrix of z-coordinates of vertices of influencing panels
 * xcw: (mv-1)*(nv-1) matrix of x-coordinates of control points of 
 *      influencing panels
 * ycw: (mv-1)*(nv-1) matrix of y-coordinates of control points of 
 *      influencing panels
 * zcw: (mv-1)*(nv-1) matrix of z-coordinates of control points of 
 *      influencing panels
 * nx: (mv-1)*(nv-1) matrix of x-components normal to the panels whose 
 *     control points are stored in matrices xcw, ycw, zcw.
 * ny: (mv-1)*(nv-1) matrix of y-components normal to the panels whose 
 *     control points are stored in matrices xcw, ycw, zcw.
 * nz: (mv-1)*(nv-1) matrix of z-components normal to the panels whose 
 *     control points are stored in matrices xcw, ycw, zcw.
 * tauxx: (mv-1)*(nv-1) matrix of x-components tangent to the panels whose 
 *     control points are stored in matrices xcw, ycw, zcw (tangent with 
 *     zero y component)
 * tauxy: (mv-1)*(nv-1) matrix of y-components tangent to the panels whose 
 *     control points are stored in matrices xcw, ycw, zcw (tangent with 
 *     zero y component)
 * tauxz: (mv-1)*(nv-1) matrix of z-components tangent to the panels whose 
 *     control points are stored in matrices xcw, ycw, zcw (tangent with 
 *     zero y component)
 * tauyx: (mv-1)*(nv-1) matrix of x-components tangent to the panels whose 
 *     control points are stored in matrices xcw, ycw, zcw (tangent normal 
 *     to both taux and n)
 * tauyy: (mv-1)*(nv-1) matrix of y-components tangent to the panels whose 
 *     control points are stored in matrices xcw, ycw, zcw (tangent normal 
 *     to both taux and n)
 * tauyz: (mv-1)*(nv-1) matrix of z-components tangent to the panels whose 
 *     control points are stored in matrices xcw, ycw, zcw (tangent normal 
 *     to both taux and n)
 * Aphi: (mc*nc)*(mv*nv) matrix source potential influence coefficients
 * Au: (mc*nc)*(mv*nv) matrix of source velocity influence coefficients in  
 *      x direction 
 * Av: (mc*nc)*(mv*nv) matrix of source velocity influence coefficients in  
 *      y direction 
 * Aw: (mc*nc)*(mv*nv) matrix of source velocity influence coefficients in  
 *      z direction 
 * Bphi: (mc*nc)*(mv*nv) matrix doublet potential influence coefficients
 * Bu: (mc*nc)*(mv*nv) matrix of doublet velocity influence coefficients in  
 *      x direction 
 * Bv: (mc*nc)*(mv*nv) matrix of doublet velocity influence coefficients in  
 *      y direction 
 * Bw: (mc*nc)*(mv*nv) matrix of doublet velocity influence coefficients in  
 *      z direction 
 *
 * Outputs: This code does not return any outputs. The results of its 
 *          calculations are stored in input matrices Aphi, Au, Av, Aw,
 *          Bphi, Bu, Bv, Bw
 * NB: All matrices must have compatible dimensions 
 *
 * Compile this by typing at the terminal 
 * gcc -fPIC -shared -o sdpminfso.so sdpminfso.c
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
#include <stddef.h>

void sdpanel(double Phisd[], double uvw[], double x0, double y0, double z0, double x[], double y[], double z[], double xcp, double ycp, double zcp,
        double normal[], double taux[], double tauy[])
/* Calculates the potential and velocity influences of constant source and 
 * doublet distributions on a panel with vertices are given in x, y, z on 
 * a point x0, y0, z0 */        
{
    double xl[5],yl[5],zl[5],r[5],e[5],h[5],m,d,b,f,g,ghat,x0l,y0l,z0l,rc;
    double pi,Phi1,Phi2,l,t,fraction,p,phat,q,k,khat,us,vs,ws,ud,vd,wd;
    double ydiff,xdiff;
    int iv;
    
    pi=3.14159265358979;    /* value of pi */
    
    /* Calculate distance between influenced point and control point of 
     * influencing panel */
    rc=sqrt((x0-xcp)*(x0-xcp)+(y0-ycp)*(y0-ycp)+(z0-zcp)*(z0-zcp));
    /* Cycle through the panel vertices. Fifth vertex is coincident
     * with first vertex */
    for (iv=0; iv < 5; iv++) {
        /* Calculate coordinates of vertex iv in panel's local frame of 
         * reference */
        xl[iv]=(x[iv]-xcp)*taux[0]+(y[iv]-ycp)*taux[1]+(z[iv]-zcp)*taux[2];
        yl[iv]=(x[iv]-xcp)*tauy[0]+(y[iv]-ycp)*tauy[1]+(z[iv]-zcp)*tauy[2];
        zl[iv]=(x[iv]-xcp)*normal[0]+(y[iv]-ycp)*normal[1]+(z[iv]-zcp)*normal[2];
    }
    /* Calculate coordinates of influenced point in panel's local frame of 
     * reference */
    x0l=(x0-xcp)*taux[0]+(y0-ycp)*taux[1]+(z0-zcp)*taux[2];
    y0l=(x0-xcp)*tauy[0]+(y0-ycp)*tauy[1]+(z0-zcp)*tauy[2];
    z0l=(x0-xcp)*normal[0]+(y0-ycp)*normal[1]+(z0-zcp)*normal[2];
    /* Cycle through the panel vertices */
    for (iv=0; iv < 4; iv++) {
        /* Calculate r, e and h from equations A.73 */
        r[iv]=sqrt((x0l-xl[iv])*(x0l-xl[iv])+(y0l-yl[iv])*(y0l-yl[iv])+z0l*z0l);
        e[iv]=(x0l-xl[iv])*(x0l-xl[iv])+z0l*z0l;
        h[iv]=(x0l-xl[iv])*(y0l-yl[iv]);
    }
    /* Assing vlues of r, e and h on the fifth vertex equal to thos on the
     * first */
    r[4]=r[0];
    e[4]=e[0];
    h[4]=h[0];
    
    /* Initialize source potential, source velocities and doublet 
     * velocities */
    Phi1=0.;    // Log contribution
    Phi2=0.;    // Atan contribution
    /* Source velocities */
    us=0.;
    vs=0.;
    /* Doublet velocities */
    ud=0.;
    vd=0.;
    wd=0.;
    /* Cycle through the panel edges */
    for (iv=0; iv < 4; iv++) {
        /* Initialize value of l in equations A.73 */
        l=0.0;
        /* Calculate m and d in equations A.73 */
        m=(yl[iv+1]-yl[iv])/(xl[iv+1]-xl[iv]);
        d=sqrt((xl[iv+1]-xl[iv])*(xl[iv+1]-xl[iv])+(yl[iv+1]-yl[iv])*(yl[iv+1]-yl[iv]));
        /* xdiff and ydiff are used in the velocity calculations later */
        ydiff=yl[iv+1]-yl[iv];
        xdiff=xl[iv]-xl[iv+1];
        /* d appears in the denominator of the expression for f in 
         * equations A.73. Only carry out the following calculations if d
         * is not zero. */
        if (fabs(d) > 1e-10){
            /* Calculate f, g and ghat in equations A.73 */
            f=((x0l-xl[iv])*(yl[iv+1]-yl[iv])-(y0l-yl[iv])*(xl[iv+1]-xl[iv]))/d;
            g=(r[iv]+r[iv+1]+d);
            ghat=(r[iv]+r[iv+1]-d);
            /* ghat appears in the denominator of l in equations A.73. Only
             * Only carry out the following calculation if ghat is not 
             * zero. */
            if (fabs(ghat) > 1e-10){
                l=log(g/ghat);
            }
            /* Calculate source velocity influence of the current edge from
             * equations A.76 */
            us-=ydiff/d*l;
            vs-=xdiff/d*l;
            /* Calculate log source potential influence of the current 
             * edge from equation A.75 */
            Phi1+=f*l;
        }
        /* Initialize t in equation A.75 */
        t=0.0;
        if (fabs(xdiff) > 1e-10){ // If m is not infinite
            /* Calculate k, khat in equations A.74 */
            k=(m*e[iv]-h[iv])/r[iv];
            khat=(m*e[iv+1]-h[iv+1])/r[iv+1];
            /* Calculate t in equation A.75 */
            t=atan2(z0l*(k-khat),z0l*z0l+k*khat);
        }
        /* Calculate atan source and doublet potential influence of the 
         * current edge (equations A.75 and A.85) */        
        Phi2+=t;
        /* Calculate b, p, q, phat in equation A.86 */
        b=(x0l-xl[iv+1])*(y0l-yl[iv])-(x0l-xl[iv])*(y0l-yl[iv+1]);
        p=r[iv]+r[iv+1];
        q=r[iv]*r[iv+1]+(x0l-xl[iv])*(x0l-xl[iv+1])+(y0l-yl[iv])*(y0l-yl[iv+1])+z0l*z0l;
        phat=r[iv]*r[iv+1]*q;
        /* Calculate ratio of p to phat */
        fraction=p/phat;
        /* Calculate doublet velocity influence of the current edge from
         * equations A.86 */
        ud-=z0l*ydiff*fraction;
        vd-=z0l*xdiff*fraction;
        wd+=b*fraction;
    }
    /* Calculate total source potential influence from equation A.75 */
    Phisd[0]=-1/4.0/pi*(Phi1-z0l*Phi2);
    /* Calculate total source velocity influences from equations A.76 */
    us=us/4.0/pi;
    vs=vs/4.0/pi;
    ws=Phi2/4.0/pi;
    /* Calculate total doublet potential influence from equation A.85 */
    Phisd[1]=ws;
    /* Calculate total doublet velocity influences from equations A.86 */
    ud=ud/4.0/pi;
    vd=vd/4.0/pi;
    wd=wd/4.0/pi;
    /* If rc=0, the influenced point is the control point of the 
     * influencing panel */
    if (rc < 1e-10) {
        /* Source velocity influence in direction normal to the panel is 
         * set to zero */
        ws=0;
        /* Doublet potential self-influence is set to zero */
        Phisd[1]=0;
        /* Doublet velocity influences in directions tangent to the panel  
         * are set to zero */
        ud=0.0;
        vd=0.0;
    }
    // Transform all velocities to global coordinates
    uvw[0]=taux[0]*us+tauy[0]*vs+normal[0]*ws;
    uvw[1]=taux[1]*us+tauy[1]*vs+normal[1]*ws;
    uvw[2]=taux[2]*us+tauy[2]*vs+normal[2]*ws;
    uvw[3]=taux[0]*ud+tauy[0]*vd+normal[0]*wd;
    uvw[4]=taux[1]*ud+tauy[1]*vd+normal[1]*wd;
    uvw[5]=taux[2]*ud+tauy[2]*vd+normal[2]*wd;
    return;
}

void sdpminf(double *xc, double *yc, double *zc, double *xp, double *yp, double *zp, 
			double *xcw, double *ycw, double *zcw, double *nx, double *ny, double *nz,
			double *tauxx, double *tauxy, double *tauxz,double *tauyx, double *tauyy, double *tauyz,
			int mc, int nc, int mv, int nv, double *Aphi, double *Au, double *Av, double *Aw,
			double *Bphi, double *Bu, double *Bv, double *Bw)
{
    double normal[3],taux[3],tauy[3],x0,y0,z0,xcp,ycp,zcp,x[5],y[5],z[5],Phisd[2],uvw[6],rc;
    int ic,jc,iv,jv,mvnv,nvp1;

	mvnv=mv*nv;
	nvp1=nv+1;
    /* Create influence coefficient matrices */
    /* Cycle through influenced points */
    for (ic=0; ic < mc; ic++) {
        for (jc=0; jc < nc; jc++) {
            /* Cycle through influencing panels */
            for (iv=0; iv < mv; iv++) {
                for (jv=0; jv < nv; jv++) {
                   /* Assign coordinates of current influence point */
                    x0=*(xc+ic*nc+jc);
                    y0=*(yc+ic*nc+jc);
                    z0=*(zc+ic*nc+jc);
                    /* Assign coordinates of control point of current 
                     * influencing panel */
                    xcp=*(xcw+iv*nv+jv);
                    ycp=*(ycw+iv*nv+jv);
                    zcp=*(zcw+iv*nv+jv);
                    /* Calculate distance between influenced point and 
                     * control point of current influening panel */
                    rc=sqrt((x0-xcp)*(x0-xcp)+(y0-ycp)*(y0-ycp)+(z0-zcp)*(z0-zcp));
                    /* Assign coordinates of four vertices of current 
                     * influencing panel */
                    x[0]=*(xp+iv*nvp1+jv);
                    x[1]=*(xp+iv*nvp1+(jv+1));
                    x[2]=*(xp+(iv+1)*nvp1+(jv+1));
                    x[3]=*(xp+(iv+1)*nvp1+jv);
                    x[4]=*(xp+iv*nvp1+jv);
                    y[0]=*(yp+iv*nvp1+jv);
                    y[1]=*(yp+iv*nvp1+(jv+1));
                    y[2]=*(yp+(iv+1)*nvp1+(jv+1));
                    y[3]=*(yp+(iv+1)*nvp1+jv);
                    y[4]=*(yp+iv*nvp1+jv);
                    z[0]=*(zp+iv*nvp1+jv);
                    z[1]=*(zp+iv*nvp1+(jv+1));
                    z[2]=*(zp+(iv+1)*nvp1+(jv+1));
                    z[3]=*(zp+(iv+1)*nvp1+jv);
                    z[4]=*(zp+iv*nvp1+jv);
                    /* Assign components of unit vector normal to current
                     * influencing panel */
                    normal[0]=*(nx+iv*nv+jv);
                    normal[1]=*(ny+iv*nv+jv);
                    normal[2]=*(nz+iv*nv+jv);
                    /* Assign components of unit vector tangent to current
                     * influencing panel (zero y-component) */
                    taux[0]=*(tauxx+iv*nv+jv);
                    taux[1]=*(tauxy+iv*nv+jv);
                    taux[2]=*(tauxz+iv*nv+jv);
                    /* Assign components of unit vector tangent to current
                     * influencing panel (normal to taux and n) */
                    tauy[0]=*(tauyx+iv*nv+jv);
                    tauy[1]=*(tauyy+iv*nv+jv);
                    tauy[2]=*(tauyz+iv*nv+jv);
                    /* Calculate influence coefficients of current 
                     * influencing panel on current influencing point */
                    sdpanel(Phisd,uvw,x0,y0,z0,x,y,z,xcp,ycp,zcp,normal,taux,tauy);
                    /* Assing source potential influence */
                    *(Aphi+(ic*nc+jc)*mvnv+(iv*nv+jv))=Phisd[0];
                    /* Assing source velocity influences */
                    *(Au+(ic*nc+jc)*mvnv+(iv*nv+jv))=uvw[0];
                    *(Av+(ic*nc+jc)*mvnv+(iv*nv+jv))=uvw[1];
                    *(Aw+(ic*nc+jc)*mvnv+(iv*nv+jv))=uvw[2];
                    /* Assing doublet potential influence */
                    *(Bphi+(ic*nc+jc)*mvnv+(iv*nv+jv))=Phisd[1];
                    /* Assing doublet velocity influences */
                    *(Bu+(ic*nc+jc)*mvnv+(iv*nv+jv))=-uvw[3];
                    *(Bv+(ic*nc+jc)*mvnv+(iv*nv+jv))=-uvw[4];
                    *(Bw+(ic*nc+jc)*mvnv+(iv*nv+jv))=-uvw[5];
                }
            }
        }
    }
	
}
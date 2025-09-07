SDPMflut version 0.6

This is a set of Python and C codes to perform aerodynamic and aeroelastic analysis on wings using the compressible unsteady Source and Doublet Panel Method. For more information on the method see references 1-5.

The distribution contains the following directories:
-Common: Contains common files used for all test cases.
-AGARD445_6: Flutter solution for the weakened AGARD 445.6 wing described in reference 6.
-NASATMX72799: Flutter solution for the flat plate swept wing with and without winglets described in reference 7. 
-NASATND344: Steady and unsteady pressure calculation for the rectangular wing forced to oscillate in reference 8.
-NASATM84367: Steady pressure calculation for the swept wing described in reference 9.
-PAPA: Flutter solution for the rectangular NACA 0012, NACA 64A010 and BSCW 
 wings tested by NASA on the Pitch and Plunge Apparatus (PAPA) described in references 10-12.  
-T-tail: Flutter solution for the rectangular Van Zyl T-tail described in reference 13.  
-NACARML5: Calculation of aerodynamic stability derivatives for a straight tapered wing, a swept tapered wing and a delta wing, described in references 14-16.
-Theodorsen: Flutter solution for a 2D infinitely thin flat plate airfoil with pitch and plunge degrees of freedom at incompressible conditions and comparison to Theodorsen theory result, reference 17.

Installation:
1. Unzip the SDPMflut_v1.2.zip file, place anywhere in your file space, then edit the line starting with install_dir= in AGARD445_6/flutter_SDPM_AGARD.py, NASATMX72799/flutter_SDPM_NASATMX72799.py, NASATND344/unsteady_SDPM_NASATND344.py, NASATM84367/steady_SDPM_NASATM84367.py, PAPA/flutter_SDPM_NACA0012.py, PAPA/flutter_SDPM_BSCW.py, PAPA/flutter_SDPM_NACA64A010.py, T_tail/flutter_SDPM_Ttail.py, NACARML5/unsteady_SDPM_straight.py, NACARML5/unsteady_SDPM_swept.py, NACARML5/unsteady_SDPM_delta.py, Theodorsen/flutter_SDPM_Theodorsen.py. You need to give the absolute path to the Common directory, as installed on your system. 
2. Compile the C codes sdpminfso.c and sdpminf_unsteady_subsonicso.c found in directory Common. At the terminal type:
cc -fPIC -shared -o sdpminfso.so sdpminfso.c
cc -fPIC -shared -o sdpminf_unsteadyso.so sdpminf_unsteadyso.c
If you do not have a C compiler, you need to install one that is compatible with your system architecture. 

3. Run the codes:
- For the AGARD wing:
  Run AGARD445_6/flutter_SDPM_AGARD.py
- For the NASA TM X-72799 wing:
  Run NASATMX72799/flutter_SDPM_NASATMX72799.py
- For the NASA TN D344 wing:
  Run NASATND344/unsteady_SDPM_NASATND344.py
- For the NASA TM 84367 wing:
  Run NASATM84367/steady_SDPM_NASATM84367.py
- For the PAPA wings:
  Run PAPA/flutter_SDPM_NACA0012, PAPA/flutter_SDPM_BSCW or PAPA/flutter_SDPM_NACA64A010
- For the T-tail:
  Run T_tail/flutter_SDPM_Ttail.py
- For the NACA RML5 wings:
  Run NACARML5/unsteady_SDPM_straight.py, NACARML5/unsteady_SDPM_swept.py or NACARML5/unsteady_SDPM_delta.py
- For the Theodorsen pitch-plunge wing:
  Run Theodorsen/flutter_SDPM_Theodorsen.py

Copyright (C) 2024 Grigorios Dimitriadis 
 
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

References:
1. Dimitriadis, G., Unsteady Aerodynamics - Potential and Vortex Methods, Wiley, 2023, https://doi.org/10.1002/9781119762560.
2. Martínez, M. S. and Dimitriadis, G., Subsonic source and doublet panel methods, Journal of Fluids and Structures, Vol. 113, 2022, pp. 103624, https://doi.org/10.1016/j.jfluidstructs.2022.103624.
3. Dimitriadis, G., Kilimtzidis, S., Kostopoulos, V., Laraspata and V. Soria, L., Flutter Calculations Using the Unsteady Source and Doublet Panel Method, Journal of Aircraft, Article in Advance, 13 November 2024, https://doi.org/10.2514/1.C037891.
4. Dimitriadis, G., Panagiotou, P., Dimopoulos, T., and Yakinthos, K., Prediction of aerodynamic loads and stability derivatives using the unsteady Source and Doublet Panel Method for BWB configurations, Proceedings of the AIAA Scitech 2024 Forum, Orlando, FL, Jan. 2024.
5. Dimitriadis, G., Kilimtzidis, S., Kostopoulos, V., Laraspata, V., and Soria, L., Application of the unsteady compressible source and doublet panel method to flutter calculations, Proceedings of the International Forum on Aeroelasticity and Structural Dynamics, IFASD 2024, The Hague, Netherlands, June 2024.
6. E.Carson Yates, Jr, AGARD Standard Aeroelastic Configurations for Dynamic Response I -Wing 445.6, AGARD REPORT No.765, 1985
7. R. V. Doggett, Jr and M. G. Farmer, A preliminary study of the effects of vortex diffusers (winglets) on wing flutter, NASA TMX 72799, 1975
8. H. C. Lessing, J. L. Troutman and G. P. Menees, Experimental determination of the pressure distribution on a rectangular wing oscillating in the first bending mode for Mach numbers from 0.24 to 1.3, NASA TN D-344, 1960
9. W. K. Lockman and H. Lee Seegmiller, An experimental investigation of the subcritical and supercritical flow about a swept semispan wing, NASA TM 84367, 1983.
10. Bryan E. Dansberry et al, Experimental unsteady pressures at flutter on the supercritical wing benchmark model. AIAA-93-1592-CP, pp. 2504-2514. 
11. Test Cases for Flutter of the Benchmark Models Rectangular Wings on the Pitch and Plunge Apparatus. Robert M. Bennett. Defense Technical Information Center Compilation Part Notice ADPO10713.
12. J. A. Rivera, Jr., et al., Pressure measurements on a rectangular wing with a NACA0012 airfoil during conventional flutter. NASA Technical Memorandum 104211. July 1992.
13. J. Murua et al, T-tail flutter: Potential-flow modelling, experimental validation and flight tests, Progress in Aerospace Sciences, Vol 71, 2014, pp. 54–84.
14. D. R. Riley et al., Experimental determination of the aerodynamic derivatives arising from acceleration in sideslip for a triangular, a swept, and an unswept wing, NACA RM L55A07, 1955.
15. M. J. Queijo et al., Preliminary measurements of the aerodynamic yawing derivatives of a triangular, a swept, and an unswept wing performing pure yawing oscillations, with a description of the instrumentation employed, NACA RM L55L14, 1957.
16. J. H. Lichtenstein et al., Low-speed investigation of the effects of frequency and amplitude of oscillation in sideslip on the lateral stability derivatives of a 60o Delta wing, 45o degree sweptback wing, and an unswept wing, NACA RM L58B26, 1958.
17. T. Theodorsen, General theory of aerodynamic instability and the mechanism of flutter, NACA Report 496, 1935.

# AGARD 445.6 Flutter Test - New Package Verification

This directory contains the AGARD 445.6 flutter test case adapted for the new SDPMflut package structure.

## Purpose

This test verifies that the new package structure produces identical results to the original v0.6 implementation for the classic AGARD 445.6 weakened wing flutter benchmark.

## Files

- `flutter_SDPM_AGARD_new.py` - Main flutter analysis script using new package imports
- `modes_AGARD_Q4EPM.mat` - Structural mode shapes and frequencies (copied from v0.6)
- `comparison_results.py` - Script to compare results between old and new implementations

## Key Changes from Original v0.6

1. **Import structure**: Changed from `sys.path.append()` to proper package imports:
   ```python
   # Old v0.6
   sys.path.append(install_dir)
   from SDPMgeometry import SDPMgeometry_trap_fun
   import flutsol
   
   # New package
   from sdpmflut.core.SDPMgeometry import SDPMgeometry_trap_fun
   from sdpmflut.core import flutsol
   ```

2. **Function signatures**: Removed `install_dir` parameter from function calls:
   ```python
   # Old v0.6
   SDPMcalcs.steadysolve(..., install_dir)
   flutsol.flutsolve_flex(..., install_dir)
   
   # New package  
   SDPMcalcs.steadysolve(...)  # No install_dir parameter
   flutsol.flutsolve_flex(...)  # No install_dir parameter
   ```

3. **Shared libraries**: Compiled .so files are now located in `src/sdpmflut/kernels/`

## Test Results

**✅ VERIFICATION PASSED**

The new package produces **exactly identical** results to the old v0.6 implementation:

| Run | Mach | Old v0.6 U_F (m/s) | New Package U_F (m/s) | Difference |
|-----|------|-------------------|----------------------|------------|
| 1   | 0.499| 179.26           | 179.26               | 0.00e+00   |
| 2   | 0.678| 242.90           | 242.90               | 0.00e+00   |
| 3   | 0.901| 301.21           | 301.21               | 0.00e+00   |
| 4   | 0.954| 332.59           | 332.59               | 0.00e+00   |
| 5   | 0.957| 329.44           | 329.44               | 0.00e+00   |
| 6   | 0.960| 326.22           | 326.22               | 0.00e+00   |

**Maximum difference**: 0.00e+00 m/s (machine precision identical)

## Usage

To run the test:

```bash
cd AGARD445_6_new
python flutter_SDPM_AGARD_new.py
```

To compare with original results:

```bash
python comparison_results.py
```

## Dependencies

- numpy
- matplotlib
- scipy (for .mat file reading)
- The compiled shared libraries (.so files) in the kernels directory

## Notes

- The test uses the same AGARD 445.6 weakened wing geometry and structural data
- Results are compared against experimental data from AGARD Report No. 765 (1985)
- The new package maintains full backward compatibility in terms of numerical results
- All function interfaces remain the same except for the removal of the `install_dir` parameter

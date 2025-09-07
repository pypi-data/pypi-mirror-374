from sdpmflut.__version__ import __version__

print(__version__)
print("✅ Import test passed!")


# before
# sys.path.append(install_dir); import SDPMcalcs
# after
# from sdpmflut.core import SDPMcalcs, SDPMgeometry, flutsol
# from sdpmflut.kernels import sdpminfso, sdpminf_unsteadyso

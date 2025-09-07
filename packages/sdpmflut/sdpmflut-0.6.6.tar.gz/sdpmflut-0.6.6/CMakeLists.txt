cmake_minimum_required(VERSION 3.20)
project(sdpmflut_kernels LANGUAGES C)

# We build two shared libraries from the original C sources for use with ctypes.
# The package uses a "src" layout:
#   src/sdpmflut/kernels/sources/sdpminfso.c
#   src/sdpmflut/kernels/sources/sdpminf_unsteadyso.c

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module NumPy)

# Steady kernel - build as shared library for ctypes
add_library(sdpminfso SHARED
    src/sdpmflut/kernels/sources/sdpminfso.c
)
target_include_directories(sdpminfso PRIVATE ${Python_NumPy_INCLUDE_DIRS})
set_target_properties(sdpminfso PROPERTIES
    PREFIX ""
    SUFFIX "${CMAKE_SHARED_LIBRARY_SUFFIX}"
)
install(TARGETS sdpminfso DESTINATION sdpmflut/kernels)

# Unsteady kernel - build as shared library for ctypes
add_library(sdpminf_unsteadyso SHARED
    src/sdpmflut/kernels/sources/sdpminf_unsteadyso.c
)
target_include_directories(sdpminf_unsteadyso PRIVATE ${Python_NumPy_INCLUDE_DIRS})
set_target_properties(sdpminf_unsteadyso PROPERTIES
    PREFIX ""
    SUFFIX "${CMAKE_SHARED_LIBRARY_SUFFIX}"
)
install(TARGETS sdpminf_unsteadyso DESTINATION sdpmflut/kernels)

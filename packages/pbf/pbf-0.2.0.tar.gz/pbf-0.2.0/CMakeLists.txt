# This file is part of the mlhpbf project. License: See LICENSE

cmake_minimum_required( VERSION 3.12 )

project( mlhpbf LANGUAGES CXX )

# Find out if this is the root CMake project or not
get_directory_property( hasParent PARENT_DIRECTORY )
string( COMPARE EQUAL "${hasParent}" "" PBF_IS_ROOT )

# Options
option( PBF_TESTS "Enable verification tests." ${PBF_IS_ROOT} )
option( PBF_PYTHON "Enable python bindings." ON )

# -------------------- External dependencies ----------------------

# Configure mlhp
set( MLHP_PYTHON ${PBF_PYTHON} CACHE BOOL "" FORCE )
set( MLHP_DIMENSIONS 3 CACHE STRING "" )
set( MLHP_DEBUG_CHECKS OFF CACHE BOOL "" )
set( MLHP_INDEX_SIZE_DOFS "64" CACHE STRING "" )

add_subdirectory( external/mlhp )

# ------------------------- PBF library ---------------------------

set( MLHPBF_HEADERS laser.hpp materials.hpp meltstate.hpp thermal.hpp mechanical.hpp )
list( TRANSFORM MLHPBF_HEADERS PREPEND ${CMAKE_CURRENT_SOURCE_DIR}/include/mlhp/pbf/ )

add_library( mlhpbf INTERFACE )

target_sources( mlhpbf INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include/mlhp/pbf.hpp ${MLHPBF_HEADERS} )
target_include_directories( mlhpbf INTERFACE include external )
target_link_libraries( mlhpbf INTERFACE mlhp::core )

add_library( mlhp::pbf ALIAS mlhpbf )

file( COPY materials DESTINATION ${CMAKE_BINARY_DIR} )

if ( CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT )
    set( CMAKE_INSTALL_PREFIX "${CMAKE_CURRENT_BINARY_DIR}/install" CACHE PATH "default install path" FORCE )
endif( )

# ----------------------- Python bindings -------------------------

if( ${PBF_PYTHON} )

    include( src/files.cmake )
 
    list( TRANSFORM PBF_PYTHON_BINDING_SOURCES PREPEND src/ )
 
    pybind11_add_module( pymlhpbf ${PBF_PYTHON_BINDING_SOURCES} )
 
    target_link_libraries( pymlhpbf PRIVATE mlhp::pbf mlhp_private_compile_flags )
    
    target_include_directories( pymlhpbf PRIVATE . )
      
    # Set output directories
    set_target_properties( pymlhpbf PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${MLHP_BUILD_BINARY_DIR} )

    # Whenever we build pymlhpbf we want to build pymlhpcore too
    add_dependencies( pymlhpbf pymlhpcore )

    # Copy python sources
    file( COPY src/pbf.py DESTINATION ${MLHP_BUILD_BINARY_DIR} )
	
    if(SKBUILD)
		install( FILES src/pbf.py DESTINATION . )
		install( TARGETS pymlhpbf LIBRARY DESTINATION . )
    else(SKBUILD)
	    install( FILES src/pbf.py DESTINATION ${CMAKE_INSTALL_BINDIR} )
	    install( TARGETS pymlhpbf LIBRARY DESTINATION ${CMAKE_INSTALL_BINDIR} )
    endif(SKBUILD)

endif( ${PBF_PYTHON} )

# ---------------------- Verification tests -----------------------

if( ${PBF_TESTS} )
	include( tests/files.cmake )
	list( TRANSFORM PBF_TEST_SOURCES PREPEND tests/ )

	add_executable( mlhpbf_tests ${PBF_TEST_SOURCES} )
	target_link_libraries( mlhpbf_tests PRIVATE mlhp::pbf )
	set_target_properties( mlhpbf_tests PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin )
	target_include_directories( mlhpbf_tests PRIVATE mlhp/external/catch2 )


    install( TARGETS mlhpbf_tests )

	if( ${PBF_PYTHON} )

		list( TRANSFORM PBF_PYTHON_TESTS PREPEND tests/ )
				
		file( COPY ${PBF_PYTHON_TESTS} DESTINATION ${MLHP_BUILD_BINARY_DIR}/pbftests )
		file( COPY tests/run_pbftests.py DESTINATION ${MLHP_BUILD_BINARY_DIR} )
				
		install( FILES ${PBF_PYTHON_TESTS} DESTINATION ${CMAKE_INSTALL_BINDIR}/pbftests )
		install( FILES tests/run_pbftests.py DESTINATION ${CMAKE_INSTALL_BINDIR} )

	endif( ${PBF_PYTHON} )
endif( ${PBF_TESTS} )

# ----------------------- Example drivers -------------------------

function( createPythonExample name description )
    if( ${PBF_PYTHON} )
        configure_file( examples/${name}.py ${MLHP_BUILD_BINARY_DIR}/${name}.py COPYONLY )
    endif( ${PBF_PYTHON} )
endfunction( )

createPythonExample( AMB2018-01 "Benchmark problem by NIST." )
createPythonExample( hatched_square "Hatched square with thermomechanics." )
createPythonExample( hollow_sphere "Ressidual heat buildup when printing a hollow sphere." )
createPythonExample( multilayer_thermal "Multi-layer simulation with powder bed." )
createPythonExample( singletrack_thermal "Single track thermal computation." )
createPythonExample( singletrack_thermomech "Single track thermomechanical computation." )
createPythonExample( stldomain "Single track thermal computation with stl domain initialization." )
createPythonExample( steadystate_thermal "Steady state thermal computation with surface heat source." )
createPythonExample( thermal_metrics "Hatched square with custom postprocessing." )

configure_file( examples/stldomain.stl ${CMAKE_BINARY_DIR}/stldomain.stl COPYONLY )

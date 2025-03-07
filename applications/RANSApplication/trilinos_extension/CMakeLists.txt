kratos_add_dependency(${KRATOS_SOURCE_DIR}/applications/TrilinosApplication)

include_directories(
  ${KRATOS_SOURCE_DIR}/kratos
  ${KRATOS_SOURCE_DIR}/applications/RANSApplication
  ${KRATOS_SOURCE_DIR}/applications/TrilinosApplication
)

if (NOT TRILINOS_FOUND)
  find_package(TRILINOS REQUIRED)
endif()

include_directories(SYSTEM ${TRILINOS_INCLUDE_DIR})

file(
  GLOB_RECURSE
  KRATOS_RANS_TRILINOS_EXTENSION_PYTHON_INTERFACE_SOURCES
  ${CMAKE_CURRENT_SOURCE_DIR}/custom_strategies/*.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/custom_python/*.cpp
)

## Python module
pybind11_add_module( KratosRANSTrilinosExtension MODULE THIN_LTO ${KRATOS_RANS_TRILINOS_EXTENSION_PYTHON_INTERFACE_SOURCES} )
target_link_libraries( KratosRANSTrilinosExtension PRIVATE KratosRANSCore KratosTrilinosCore KratosMPICore ${TRILINOS_LIBRARIES})
set_target_properties( KratosRANSTrilinosExtension PROPERTIES PREFIX "")

# Set batch size in the unity build
IF(CMAKE_UNITY_BUILD MATCHES ON)
    set_target_properties(KratosRANSTrilinosExtension PROPERTIES UNITY_BUILD_BATCH_SIZE ${KRATOS_UNITY_BUILD_BATCH_SIZE})
ENDIF(CMAKE_UNITY_BUILD MATCHES ON)

###############################################################################
# changing the .dll suffix to .pyd
if(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
  set_target_properties(KratosRANSTrilinosExtension PROPERTIES SUFFIX .pyd)
endif(${CMAKE_SYSTEM_NAME} MATCHES "Windows")

# changing the .dylib suffix to .so
if(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
	set_target_properties(KratosRANSTrilinosExtension PROPERTIES SUFFIX .so)
endif(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")

###############################################################################
## installing the resulting libraries
install(TARGETS KratosRANSTrilinosExtension DESTINATION libs )

###############################################################################
## install python module
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/TrilinosExtension.py" DESTINATION "KratosMultiphysics/RANSApplication")

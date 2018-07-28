cmake_minimum_required (VERSION 2.6)
project (test C)

# add the binary tree to the search path for include files
include_directories ("${PROJECT_BINARY_DIR}")

include_directories ("${PROJECT_SOURCE_DIR}/libs")
add_subdirectory (libs)
# set (EXTRA_LIBS ${EXTRA_LIBS} )
# set (EXTRA_LIBS ${EXTRA_LIBS} rw_lock.c)
set (EXTRA_LIBS ${EXTRA_LIBS} pthread)

# LIB
add_library(rw_lock libs/rw_lock.c)

  
# add the executable
add_executable (test main.c)
target_link_libraries (test ${EXTRA_LIBS} rw_lock) 
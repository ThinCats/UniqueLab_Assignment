cmake_minimum_required (VERSION 2.6)
project (updatedb)


# should we use our own math functions
option(USE_MYMATH "Use tutorial provided math implementation" ON)



# add the binary tree to the search path for include files
# so that we will find TutorialConfig.h
include_directories ("${PROJECT_BINARY_DIR}")

# add the MathFunctions library?
if (USE_MYMATH)
  include_directories ("${PROJECT_SOURCE_DIR}/libs")
  add_subdirectory (libs)
  # set (EXTRA_LIBS ${EXTRA_LIBS} )
  set (EXTRA_LIBS ${EXTRA_LIBS} updatedb_basic)
  set (EXTRA_LIBS ${EXTRA_LIBS} error_functions)
  set (EXTRA_LIBS ${EXTRA_LIBS} dirqueue)

  
endif (USE_MYMATH)
# add the executable
add_executable (updatedb main.cpp)
target_link_libraries (updatedb ${EXTRA_LIBS}) 

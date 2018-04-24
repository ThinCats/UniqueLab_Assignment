cmake_minimum_required (VERSION 2.6)
project (searcher)



# add the binary tree to the search path for include files
include_directories ("${PROJECT_BINARY_DIR}")

  include_directories ("${PROJECT_SOURCE_DIR}/libs")
  add_subdirectory (libs)
  # set (EXTRA_LIBS ${EXTRA_LIBS} )
  set (EXTRA_LIBS ${EXTRA_LIBS} searcher_basic)
  set (EXTRA_LIBS ${EXTRA_LIBS} error_functions)
  set (EXTRA_LIBS ${EXTRA_LIBS} cpp_redis tacopie pthread)

# add the executable
add_executable (searcher main.cpp)
target_link_libraries (searcher ${EXTRA_LIBS}) 

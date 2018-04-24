cmake_minimum_required (VERSION 2.6)
project (searcher)



# add the binary tree to the search path for include files
include_directories ("${PROJECT_BINARY_DIR}")


  include_directories ("${PROJECT_SOURCE_DIR}/libs")
  add_subdirectory (libs)
  # set (EXTRA_LIBS ${EXTRA_LIBS} )
  # set (EXTRA_LIBS ${EXTRA_LIBS} updatedb_basic)
  set (EXTRA_LIBS ${EXTRA_LIBS} error_functions)
  # set (EXTRA_LIBS ${EXTRA_LIBS} dirqueue)
  # set (EXTRA_LIBS ${EXTRA_LIBS} PlainText)
  set (EXTRA_LIBS ${EXTRA_LIBS} cpp_redis tacopie pthread)
  # set (EXTRA_LIBS ${EXTRA_LIBS} magic)
  set (EXTRA_LIBS ${EXTRA_LIBS} searcher)
  

  

  
# add the executable
add_executable (searcheeer main.cpp)
target_link_libraries (searcheeer ${EXTRA_LIBS}) 

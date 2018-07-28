cmake_minimum_required (VERSION 2.6)
project (Word_sort)

# add the binary tree to the search path for include files
include_directories ("${PROJECT_BINARY_DIR}")

include_directories ("${PROJECT_SOURCE_DIR}/libs")
add_subdirectory (libs)

set (EXTRA_LIBS ${EXTRA_LIBS} word_sort)
set (EXTRA_LIBS ${EXTRA_LIBS} error_functions)
set (EXTRA_LIBS ${EXTRA_LIBS} PlainText)
set (EXTRA_LIBS ${EXTRA_LIBS} pthread)
set (EXTRA_LIBS ${EXTRA_LIBS} magic)

  
# add the executable
add_executable (test main.cpp)
target_link_libraries (test ${EXTRA_LIBS}) 
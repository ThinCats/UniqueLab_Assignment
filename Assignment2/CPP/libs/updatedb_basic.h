#ifndef UPDATEDB_BASIC_H
#define UPDATEDB_BASIC_H

#include <iostream>
// For C BASIC
#include <cstdio>
#include <cerrno>
#include <cstdlib>
#include <cstring>
// For POSIX API
#include <dirent.h>
// error_print functios
#include "error_functions.h"

// For iterate the files in given dir and saved the subdirs in a queue
// dirpath will be the absolute path
int iterFile(char *dirpath);

// For iterate the subdirs
// read from a queue(or sort) and then call iterFile()
int iterDirs(char *rootdir);



//For priority calculation
int priority(char *filename);

#endif
#ifndef UPDATEDB_BASIC_H
#define UPDATEDB_BASIC_H

#include <iostream>
#include <string>
#include <queue>
// For C BASIC
#include <cstdio>
#include <cerrno>
#include <cstdlib>
#include <cstring>

extern "C" {
// For POSIX API
#include <dirent.h>
#include <sys/stat.h>
}
// error_print functios
#include "error_functions.h"

// User-edited class
#include "dirqueue.h"

// For iterate the files in given dir and saved the subdirs in a queue
// dirpath will be the absolute path
int iterFile(std::string &dirpath, DirQueue &a_dirqueue);

// For iterate the subdirs
// read from a queue(or sort) and then call iterFile()
int iterDirs(char *rootdir);



//For priority calculation
int priority(char *filename);

#endif
#ifndef UPDATEDB_BASIC_H
#define UPDATEDB_BASIC_H

#include "basic_libs.h"
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



#endif
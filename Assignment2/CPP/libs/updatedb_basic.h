#ifndef UPDATEDB_BASIC_H
#define UPDATEDB_BASIC_H

#include "basic_libs.h"
// error_print functios
#include "error_functions.h"

// User-edited class
#include "dirqueue.h"
#include "PlainText.h"

// Redis-client
#include "cpp_redis/cpp_redis"
// Extern data:

int makeIndex(std::string &dirpath);

// For iterate the files in given dir and saved the subdirs in a queue
// dirpath will be the absolute path
int iterFile(std::string &dirpath, DirQueue &a_dirqueue, DirQueue &a_filequeue);

// For iterate the subdirs
// read from a queue(or sort) and then call iterFile()
int iterDirs(std::string &parent_path, std::vector<std::string> &all_files);

// For iter the files content
int iterContent(std::vector<std::string> &all_files, cpp_redis::client &db_client);

int readFile(std::string &filename, cpp_redis::client &db_client);
//std::vector<string> &splitToWords(string &line);

#endif

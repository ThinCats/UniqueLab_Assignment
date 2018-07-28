#ifndef UPDATEDB_BASIC_H
#define UPDATEDB_BASIC_H

#include "basic_libs.h"
// error_print functios
#include "error_functions.h"

// User-edited class
#include "PlainText.h"

// Multi thread
#include <thread>

// Map
#include <map>
// Extern data:

// typedef std::queue<std::string*> FileQueue;
// typedef std::queue<std::string*> DirQueue;
typedef std::vector<std::string> FileQueue;
typedef std::vector<std::string> DirQueue;
typedef FileQueue files_vector;

int startSort(std::string &dirpath);

// For iterate the files in given dir and saved the subdirs in a queue
// dirpath will be the absolute path
int iterFile(std::string& filepath, DirQueue &a_dirqueue, FileQueue &a_filequeue, PlainText& judger);

// For iterate the subdirs
// read from a queue(or sort) and then call iterFile()
int iterDirs(std::string &parent_path, files_vector &all_files, PlainText& judger); 
// For iter the files content
int iterContent(FileQueue &all_files);

int readFile(std::string &filename, std::map<std::string, size_t> word_count);


#endif

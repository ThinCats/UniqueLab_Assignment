#ifndef UPDATEDB_BASIC_H
#define UPDATEDB_BASIC_H

#include "basic_libs.h"
// error_print functios
#include "error_functions.h"

// User-edited class
#include "dirqueue.h"
#include "fileQueue.h"
#include "PlainText.h"

// Redis-client
#include "cpp_redis/cpp_redis"

// Multi thread
#include <omp.h>
// Extern data:

int makeIndex(std::string &dirpath);

// For iterate the files in given dir and saved the subdirs in a queue
// dirpath will be the absolute path
int iterFile(std::string &dirpath, DirQueue &a_dirqueue, FileQueue &a_filequeue);

// For iterate the subdirs
// read from a queue(or sort) and then call iterFile()
int iterDirs(std::string &parent_path, std::vector<std::string> &all_files);

// For iter the files content
int iterContent(std::vector<std::string> &all_files, cpp_redis::client &db_client);

int readFile(std::string &filename, cpp_redis::client &db_client);
//std::vector<string> &splitToWords(string &line);


int readFile_multi2(std::string &filename, cpp_redis::client &db_client, int Fileid);
int iterContent_multi(std::vector<std::string> &all_files, cpp_redis::client &db_client, int continue_id);


int iterContent_multi2(std::vector<std::string> &all_files, cpp_redis::client &db_client);
int parel(void);

int readFile_multi(std::string &filepath, cpp_redis::client &db_client, int Fileid, std::map<std::string, std::vector<std::string> > &word_index, std::map<std::string, std::vector<std::string> >& word_lines); 
#endif

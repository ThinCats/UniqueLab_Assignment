#ifndef _SORT_WORDS_H
#define _SORT_WORDS_H

#include "FileRead.h"
#include "Threadsafe_queue.cpp"

#include <thread>
#include <iterator>
#include <memory> // For share_ptr


typedef std::vector<std::string> block_t;
typedef std::vector<std::string>::iterator file_it;

typedef std::pair<std::string, size_t> key_val_t;

bool compare_map(key_val_t &a, key_val_t &b);

// void words_worker_old(file_it start, file_it end, Threadsafe_queue<std::shared_ptr<block_t>>& words_queue);
void words_worker(file_it start, file_it end, std::map<std::string , size_t>&);
int threadManager(std::string &root_path);

#endif // !_SORT_WORDS_H

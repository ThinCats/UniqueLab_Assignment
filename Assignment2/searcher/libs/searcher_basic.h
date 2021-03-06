#ifndef SEARCHER_H
#define SEARCHER_H
#include "basic_libs.h"
#include "error_functions.h"

int printLines(std::string &pathname, const std::vector<std::pair<std::string, std::vector<std::string> > >&file_keywords );

int searchNow(std::vector<std::string> &keywords_list);

// The vector is for save the All fileid list
// Convenient for iter all id
// Info: map(fileid, {(keyword, {"1", "2", "3"...})...})
int singleWordFind(std::string &keyword, std::map <std::string, std::vector<std::pair<std::string, std::vector<std::string> > > >& file_result_container, cpp_redis::client &db_client, std::vector<std::string> &fileid_list);

int callIndexer(char *pathname);

int executeSh(const char* command);

int format(char *pathname);
#endif // !1SEARCHER_H

#ifndef SEARCHER_H
#define SEARCHER_H
#include "cpp_redis/cpp_redis"
#include "updatedb_basic.h"


//int printLines(std::string &pathname, std::multimap<std::string, std::vector<int> > &keywords_info );

//std::vector<int> &hanleLines(std::vector<std::string> lines_str);

//std::multimap<std::string, std::pair<std::string, std::vector<int> > > getResult(std::vector<std::string>& keywords_list);

int searchNow(std::vector<std::string> &keywords_list);

int foo(void);
//int printUsage(void);

//std::vector<std::string> &stringDownloader(cpp_redis::client &db_client, std::string &command, int database_index);

#endif // !1SEARCHER_H
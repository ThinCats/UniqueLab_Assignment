#include "searcher.h"

using std::string;
using std::vector;
using std::cout;
using std::endl;

int searchNow(std::vector<std::string> &keywords_list) {
    
    cout << "hw";
    // For connecting to redis
   cpp_redis::client db_client;
   db_client.connect();
    if(db_client.is_connected() == false) {
        errExit("Can't connect to Redis-server");
   }

    cout << "hellp";
  //  For iter the keyword
    for(auto keyword: keywords_list) {
       //  Select to words base 1
       db_client.select(1);
        
        db_client.zscan(keyword, 0, [](cpp_redis::reply &reply) {
            cout << reply;
            cout << "Now";
        });
        
    }
    
}

int foo(void) {
    cout << "foo" << "\n";
}

//std::vector<string> &stringDownloader(cpp_redis::client &db_client, string &command);
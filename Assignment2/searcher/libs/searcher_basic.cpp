#include "searcher_basic.h"

using std::string;
using std::vector;
using std::cout;
using std::endl;

int searchNow(std::vector<std::string> &keywords_list) {

    // For connecting to redis
   cpp_redis::client db_client;
   db_client.connect();
    if(db_client.is_connected() == false) 
        errExit("Can't connect to Redis-server");

    
    // This map container is for saving all fileid and search result
    // To iter it later into the print list
    // INFO: map(fileid, {(keywordA, {"1", "2", "3"...})...})
    std::map <string, vector<std::pair<string, vector<string> > > > file_result_container;

    // This fileid_list is for save all fileid that occurs in
    // the searching process.
    std::vector<string> fileid_list;
    //  For iter the keyword
    for(auto &keyword: keywords_list) {
        singleWordFind(keyword, file_result_container, db_client, fileid_list);
    }

    // Variables needed
    string pathname;

    // For print out the word and lines information
    for(auto &fileid: fileid_list) {
        
        // Find the fileid -> path
        if(db_client.is_connected() == false) {
            db_client.connect();
        }
        // Select to database 2(Path base)
        db_client.select(2);
        db_client.get(fileid, [&pathname](cpp_redis::reply& reply){
            if(reply.is_string()) {
                pathname = reply.as_string();
            }
            else {
                errMsg("reply is not string");
            }
        });
        db_client.sync_commit();
        // Get the pathname OK
        // This read the current file's keyword_info lists
        // Then will iter.
        vector<std::pair<string, vector<string> > > &file_keywords
        = file_result_container[fileid];
        printLines(pathname, file_keywords);

    }
}


int singleWordFind(std::string &keyword, std::map <std::string, std::vector<std::pair<std::string, std::vector<std::string> > > >& file_result_container, cpp_redis::client &db_client, std::vector<std::string> &fileid_list) {
       //  Select to words base 1
       //  Which contains the word index data
       db_client.select(1);

       // Get the number of file to iter
       // It's in an ordered set(keyword)
       int filenum;
       db_client.zcard(keyword, [&filenum](cpp_redis::reply& reply) {
          filenum = reply.as_integer();
       });

       // Save the fileids to locate the files
       // For each word
       std::vector<string> word_fileId_list;
       int  line_num;
     
      
       // To get the keyword -> fileid and save into fileid<vector>
       // [keyword]: (fileId1, fileId2, ...)
       // [main]: (2, 3, 4...)
       db_client.zrange(keyword, "0", "1000000", [&word_fileId_list, &fileid_list](cpp_redis::reply& reply){
             
           const std::vector<cpp_redis::reply> &group = reply.as_array();
          
           for(auto &ele: group) {
               word_fileId_list.push_back(ele.as_string());
               // PUT into a global filelist
               fileid_list.push_back(ele.as_string());
           }
       });
       db_client.sync_commit(); 

       // Iter the file to get lines
       for(int i=0; i < filenum;i++){

            // For save each word occures in one file's
            // positions (by lines)
            std::vector<string> lines_list;
           // To find the key in list
           // Type: main:5
            string list_index = keyword + ":" + word_fileId_list[i];

          /* 
           // To get lines number
           db_client.llen(list_index, [&line_num](cpp_redis::reply& reply){
               //cout << reply.is_integer() << "reply::" << reply << std::endl;
              line_num = reply.as_integer();
           });
            db_client.sync_commit();
          */ // For get the line number

             // To get the lines with lrange(List range)
            // Put into a vector
            // The data in database is like this:
           // [keyword:fileid]: (line1, line2, ...)
           // [main:2]: (12, 32, 44, ...)
           db_client.lrange(list_index, 0, 10000000, [&lines_list](cpp_redis::reply& reply){

               const std::vector<cpp_redis::reply>& group = reply.as_array();
               for(auto& ele: group) {
                   lines_list.push_back(ele.as_string());
               }
           });
           db_client.sync_commit();

           // Pack keyword, lines and fileId in a map
           // Let fileid be the key
           // Current file keywords
           // As element in map is referrence
           // Use new to new a vector TODO
           
            // Read the result container
            // If no fileid match
            if(file_result_container.find(word_fileId_list[i]) == file_result_container.end()) {
                file_result_container[word_fileId_list[i]] = {std::make_pair(keyword, lines_list)};
                // test:
                //cout << std::get<1>(file_result_container[word_fileId_list[i]][0])[0] << "\n";
            } else {
             vector<std::pair<string, vector<string> > > &file_keywords =
             file_result_container[word_fileId_list[i]];
             file_keywords.push_back(std::make_pair(keyword, lines_list));
            }

        



       }
}

// file_keywords is {(keyword, {"1", "2"...})...}
// To print files as this format:
// /x/y/z/fileA: KeywordA(4): line 234,347,326,331 KeywordB(2): line 12,1992
// $pathname: $keyword($times): line ${lines}
int printLines(std::string &pathname,const std::vector<std::pair<std::string, std::vector<std::string> > >&file_keywords ) {
    // print path name first
    cout << pathname << ": ";
    for(auto &keyword_info: file_keywords) {
        const string &keyword_name = std::get<0>(keyword_info);
        const vector<string> &line_list = std::get<1>(keyword_info);

        // output
        cout << keyword_name << "(" << line_list.size() << "):";
        cout << " ";
        cout << "line" << " ";

        // Not use iterator because I encounter some problems
        // And I want to control the output of ","
        int i;
        for(i=0;i < line_list.size()-1;i++) {
            cout << line_list[i];
            cout << ",";
        }
        cout << line_list[i] << " " ;
    }
    
    // End of one file
    cout << "\n" << std::endl;
}

int callIndexer(char *pathname) {
    // connect to redis to check wheher already
    // exists an index-cache
    cpp_redis::client check_client;
    check_client.connect();
    if(check_client.is_connected() == false) {
        errExit("Redis connect failed\n");
    }


    bool will_build_index;
    string old_pathname = pathname;

    // Get the path record from database
    // compare the old pathname
    // Select database 3 to get the path info
    check_client.select(3);
    
    check_client.get("index_db_path", [&old_pathname, &will_build_index](cpp_redis::reply& reply){
        if(reply.is_string()) {
            
            // Compare the pathname in database
            // /usr/ is same as /usr so I added more conditions
            // to judge this
            will_build_index = !(old_pathname == reply.as_string());
            cout << reply.as_string();
        } else {
            // means NIL
            // No database has been built
            will_build_index = true;
        }
   });
   check_client.sync_commit();
   // Close database
   check_client.disconnect();

   if(will_build_index == false) {
       cout << "\n" <<  "Database can be reused" << "\n";
       cout << "No needs to rebuild" << std::endl;
       return 1;
   } else {
       // call the indexer from external
       char cmd[1024];
       sprintf(cmd, "./indexer %s", pathname);
       if(executeSh(cmd) == -1) {
           errExit("Please check whether the indexer is in this dir\n");
           return -1;
       }

       cout << "\nIndexer exited..." << endl;
    
   }

}

int executeSh(const char* command) {
    FILE *fp = nullptr;
    int exit_status;

    // buf space to save output
    char buf[1024];
    if((fp=popen(command, "r"))!=nullptr) {
        while(fgets(buf, 1024, fp)!=nullptr) {
            puts(buf);
        }
        //cout << fp;
        exit_status = pclose(fp);
    } else {
        errMsg("Popen Error");
        return -1;
    }

    // Means command not found
    if(WEXITSTATUS(exit_status) == 127) {
        cout << "\nCommand not found\n";
        return -1;
    }
    // Means successfully
    else if(WEXITSTATUS(exit_status) == 0) {
        cout << "\nExcute successfully\n";
        return 1;
    }
   }

// To format the pathname
// As /usr not /usr/
int format(char *pathname) {
       char *it = pathname;

       // Iter until reach the end
       while(*it++ != '\0');

       // More 1 has been added
       it -= 2;
       if(*it == '/')
            *it = '\0';

       return 1;
}
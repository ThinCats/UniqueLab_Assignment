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

    //
  //  For iter the keyword
    for(auto keyword: keywords_list) {
       //  Select to words base 1
       db_client.select(1);

       // Get the number of file to iter
       // It's in an ordered set(keyword)
       int filenum;
       db_client.zcard(keyword, [&filenum](cpp_redis::reply& reply) {
           //cout << reply.is_integer();
         //cout << reply.as_integer();
          filenum = reply.as_integer();
          //filenum = reply.as_integer();
       });

       cout << filenum << std::endl;
       cout << "zcard endding" << "\n";
       
       
       // Save the fileids to locate the files
       std::vector<string> fileid;
       std::vector<string> lines;
       int  line_num;
     
      
       // To get the keyword -> fileid and save into fileid<vector>
       db_client.zrange(keyword, "0", "1000000", [&fileid](cpp_redis::reply& reply){
             
           const std::vector<cpp_redis::reply> &group = reply.as_array();
          
           for(auto &ele: group) {
               fileid.push_back(ele.as_string());
           }
           cout << "get " << reply << std::endl;
       });
       // Commit to exec zcard and zrange
       db_client.sync_commit(); 
         cout << "filenum:" << filenum<< std::endl;
       // Iter the file to get linesss
       //std::multimap;
       for(int i=0; i < filenum;i++){
           // To find the key in list
           // Type: main:5
            string list_index = keyword + ":" + fileid[i];
            cout << list_index << "\n";
           // To get lines
           db_client.llen(list_index, [&line_num](cpp_redis::reply& reply){
               cout << reply.is_integer() << "trply::" << reply << std::endl;
              line_num = reply.as_integer();
           });
            db_client.sync_commit();

            // To get the lines with lrange(List range)
            // Put into a vector
           db_client.lrange(list_index, 0, line_num, [&lines](cpp_redis::reply& reply){

               const std::vector<cpp_redis::reply>& group = reply.as_array();
               for(auto& ele: group) {
                   lines.push_back(ele.as_string());
               }
                cout << "Lrange get: " << reply << std::endl;
           });
           db_client.sync_commit();
           // Pack keyword, lines and fileId in a map
           // Let fileid be the key


       }
       //db_client.sync_commit();

       
    }
    

    
}

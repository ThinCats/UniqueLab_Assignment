#include "updatedb_basic.h"

// For using
using std::cout;
using std::string;
using std::priority_queue;
using std::ifstream;

int makeIndex(std::string &dirpath) {

    cpp_redis::client db_client;
    try {
        db_client.connect();
    }
    catch(const std::exception &ex) {
        errExit("Can't connect to Redis Server.\n Please check it\n");
    }

    // FLUSH DATABASE
    db_client.send({"flushall"});

    // Set a flag for database reusing
    db_client.select(3);
    db_client.set("index_db_path", dirpath);
    db_client.sync_commit();

    // This is for files_name saving
    // To avoid segment flow
    std::vector<std::string> all_files;
    iterDirs(dirpath, all_files);
    //iterContent(all_files, db_client);
    iterContent_multi2(all_files, db_client);
    // Sync
    db_client.sync_commit();
    // Close connections
    db_client.disconnect();

}

int iterFile(std::string &dirpath, DirQueue &a_dirqueue, FileQueue &a_filequeue) {
    // the DIR pointer
    DIR *dirp;
    struct dirent *ent_current;
    PlainText judger(1);
    judger.init();
    // for supporting c
    // max len 255
    char dirpath_c[255];
    strcpy(dirpath_c, dirpath.c_str());
    // for lstat()
    char full_file_path[255];
    struct stat statbuf;
    
    dirp = opendir(dirpath_c);
    if(dirp == nullptr) {
        errMsg("Can't read the dir: %s", dirpath_c);
        return 0;
    }

    while(true) {
        ent_current = readdir(dirp);
        if(ent_current == nullptr) {
            //std::cout << "end of dir\n";
            break;
        }
        //ignore . and ..
        if(strcmp(ent_current->d_name,".")==0 || strcmp(ent_current->d_name, "..") == 0)
            continue;

        // read the file type
        // Generate the full filepath
        strcpy(full_file_path, dirpath_c);
        // TODO: handle the more '/'
        strcat(full_file_path, "/");
        strcat(full_file_path, ent_current->d_name);
        
       

        if(lstat(full_file_path, &statbuf)==-1) {
            errMsg("Can't judge the file type");
        } else {
            if(S_ISDIR(statbuf.st_mode)) {
                // Put it in a queue in order to avoid recurisive
                // dirpath_c is a c string indicating the parent path
                a_dirqueue.push(ent_current->d_name, dirpath_c);
            }
            else if(S_ISREG(statbuf.st_mode)) {
                // TODO: DO SOMTHING

                // Plain text should be handled
                if(judger.isText(full_file_path)) {
                    // Put into a file_queue in orders
                    // Then the indexer will get from the queue
                    // use d_name for priority
                    a_filequeue.push(ent_current->d_name, dirpath_c, statbuf.st_mtime, statbuf.st_ino);
                    /*
                    std::cout << full_file_path << std::endl;
                    std::cout << "It's a text" << std::endl;
                    */
                }
                // Test:
            }
        }
    }
    // Error detactions:
    if(errno != 0) {
        //errMsg("read dir");
    }
    // Close dir
    if(closedir(dirp) == -1) {
        errMsg("Close dir falied");
    }

    // Close Judger
    judger.destruct();
}

// I still use recursive to track dirs
int iterDirs(std::string &parent_path, std::vector<std::string> &all_files) {
    DirQueue dir_queue;
    // File_queue will be only used once each dir
    static FileQueue file_queue;
    
    iterFile(parent_path, dir_queue, file_queue);
    // Put the files reading from filequeue into all_files
    while(!file_queue.empty()) {
        file_info a_info = file_queue.top();
        all_files.push_back(a_info.filename);
        cout << a_info.filename << "\n";
        cout << a_info.file_time << "\n";
        cout << a_info.file_id << "\n";
        file_queue.pop();
    }

    // Iter the dir_queue to access to subdir
    while(!dir_queue.empty()) {
        std::string path = dir_queue.top();
        dir_queue.pop();
        iterDirs(path, all_files);
    }
}

int iterContent(std::vector<std::string> &all_files, cpp_redis::client &db_client) {

    if(db_client.is_connected() == false) 
        errExit("Can't connect to Redis server.\n");
    // The file id identical for each file;
    // Iter each files:
    for(auto filepath: all_files) {
        readFile(filepath, db_client);
    // FileId determines the file display order
    }
    db_client.sync_commit();
    cout << "DataBase has been updated" << "\n";
    // test`
}
int iterContent_multi2(std::vector<std::string> &all_files, cpp_redis::client &db_client) {

    if(db_client.is_connected() == false) 
        errExit("Can't connect to Redis server.\n");
    // The file id identical for each file;
    // Iter each files:
    int file_length = all_files.size();
    #pragma omp parallel
    {
    #pragma omp for nowait
    for(int i=0;i < file_length;i++) {
        readFile_multi2(all_files[i], db_client, i);
            db_client.commit();
    }
    }

    db_client.sync_commit();
    cout << "DataBase has been updated" << "\n";
    // test`
}
int iterContent_multi(std::vector<std::string> &all_files, cpp_redis::client &db_client, int continue_id) {

    if(db_client.is_connected() == false) 
        errExit("Can't connect to Redis server.\n");
    // The file id identical for each file;
    // Iter each files:
    int file_length = all_files.size();
     std::map<std::string, std::vector<std::string> > word_index;
     std::map<std::string, std::vector<std::string> > word_lines;


    // For continue using continue_id
    {
    for(int i=continue_id; i < file_length;i++) {
        readFile_multi(all_files[i], db_client, i, word_index, word_lines);
    }
    }
    db_client.select(1);
    int i = 0;
    #pragma omp parallel sections
    {
    
    #pragma omp section
    {
    for(auto it=word_index.cbegin();it != word_index.cend();it++,i++) {
        db_client.sadd(it->first, it->second);
        if(i % 50 == 0)
            db_client.commit();
    }
    i=0;
    }
    #pragma omp section
    {
    cout << word_lines.size() << std::endl;
    for(auto it=word_lines.cbegin();it != word_lines.cend();it++,i++) {
        db_client.rpush(it->first, it->second);
        if(i%50 == 0)
            db_client.commit();
    }
    }
   }
   db_client.sync_commit();
    cout << "DataBase has been updated" << "\n";
    // test`
}
// paterns
int readFile(std::string &filepath, cpp_redis::client &db_client) {
        static int Fileid = 0;
        string Fileid_str = std::to_string(Fileid);
        cout << "content: " << filepath << std::endl << "\n";
        // Open the file;"[a-z0-9_-]{1,50}"
        ifstream in_file(filepath, ifstream::in);
        if(!in_file) {
            errMsg("Can not read File:%s\n", filepath.c_str());
            return -1;
        }
        // Open successfully
        
        // Change database to 2
        // Put the file ID
        // Into Redis string

        // Select to 2
        // The database is like this:
        // [FileId]: (filepath)
        db_client.select(2);
        db_client.set(Fileid_str, filepath);
       
        // Read the word
        std::string line;
        int line_num = 1;
        char *word = new char[5000];
        // For path pair to pack into redis
        std::pair<string, string> path_pair("path", filepath);
        

        // Select to 1(words)
         db_client.select(1);
        //db_client.select(1);
         while(getline(in_file, line)) {
            std::istringstream record(line);

            // For a single word
            char ch;
            int word_len = 0;
            
            while((ch = record.get())!= EOF) {
                if(isalnum(ch) || ch == '_') {
                    word[word_len] = ch;
                    word[++word_len] = '\0';
                } 
                // There is a break
                else if(word_len != 0) {
                    string word_str = word; // for word convertion 
                    // Add into database
                    // build the word <-> files using sorted set
                    
                    // Ordered Set
                    // [Word]: (fileid1, fileid2)
                    db_client.zadd(word_str,{"NX"},{std::make_pair(Fileid_str, Fileid_str)});
                    
                    // build the word:file <-> lines using list
                    // [word:fileid]: (line1, line2)
                    db_client.rpush(word_str+":"+Fileid_str, {std::to_string(line_num)});
                    
                    word_len = 0;
                }
            }
        line_num ++;
        }
    Fileid++;
   // cout << "Total File number: "<< Fileid << "\n";
    db_client.sync_commit();
    return Fileid;
}

int readFile_multi2(std::string &filepath, cpp_redis::client &db_client, int Fileid) {
        string Fileid_str = std::to_string(Fileid);
        cout << "content: " << filepath << std::endl << "\n";
        // Open the file;"[a-z0-9_-]{1,50}"
        ifstream in_file(filepath, ifstream::in);
        if(!in_file) {
            errMsg("Can not read File:%s\n", filepath.c_str());
            return -1;
        }
        // Open successfully
        
        // Change database to 2
        // Put the file ID
        // Into Redis string

        // Select to 2
        // The database is like this:
        // [FileId]: (filepath)
        db_client.select(2);
        db_client.set(Fileid_str, filepath);
       
        // Read the word
        std::string line;
        int line_num = 1;
        char *word = new char[5000];
        // For path pair to pack into redis
        std::pair<string, string> path_pair("path", filepath);
        

        // Select to 1(words)
         db_client.select(1);
         while(getline(in_file, line)) {
            std::istringstream record(line);

            // For a single word
            char ch;
            int word_len = 0;
            
            while((ch = record.get())!= EOF) {
                if(isalnum(ch) || ch == '_') {
                    word[word_len] = ch;
                    word[++word_len] = '\0';
                } 
                // There is a break
                else if(word_len != 0) {
                    string word_str = word; // for word convertion 
                    // Add into database
                    // build the word <-> files using sorted set
                    
                    // Ordered Set
                    // [Word]: (fileid1, fileid2)
                     db_client.zadd(word_str,{"NX"},{std::make_pair(Fileid_str, Fileid_str)});
                    
                    // build the word:file <-> lines using list
                    // [word:fileid]: (line1, line2)
                     db_client.rpush(word_str+":"+Fileid_str, {std::to_string(line_num)});
                    
                    word_len = 0;
                }
            }
        line_num ++;
        }
    cout << "Total File number: "<< Fileid << "\n";
    return Fileid;
}
int readFile_multi(std::string &filepath, cpp_redis::client &db_client, int Fileid, std::map<std::string, std::vector<std::string> > &word_index, std::map<std::string, std::vector<std::string> >& word_lines) {
        string Fileid_str = std::to_string(Fileid);
        cout << "content: " << filepath << std::endl << "\n";
        // Open the file;"[a-z0-9_-]{1,50}"
        ifstream in_file(filepath, ifstream::in);
        if(!in_file) {
            errMsg("Can not read File:%s\n", filepath.c_str());
            return -1;
        }
        // Open successfully
        
        // Change database to 2
        // Put the file ID
        // Into Redis string

        // Select to 2
        // The database is like this:
        // [FileId]: (filepath)
        
        db_client.select(2);
        db_client.set(Fileid_str, filepath);
       
        // Read the word
        std::string line;
        int line_num = 1;
        char *word = new char[5000];
        // For path pair to pack into redis
        std::pair<string, string> path_pair("path", filepath);
        

        // Select to 1(words)
        // db_client.select(1);
        // db_client.select(1);

         // Test for speed
        // std::map<std::string, std::vector<std::string> > word_index;
        // std::map<std::string, std::vector<int> > word_lines;
         while(getline(in_file, line)) {
            std::istringstream record(line);

            // For a single word
            char ch;
            int word_len = 0;
            
            while((ch = record.get())!= EOF) {
                if(isalnum(ch) || ch == '_') {
                    word[word_len] = ch;
                    word[++word_len] = '\0';
                } 
                // There is a break
                else if(word_len != 0) {
                    string word_str = word; // for word convertion 

                    // Test:
                    
                    {
                    {
                    try {
                        word_index.at(word_str).push_back(Fileid_str);
                    }
                    catch(std::exception& ex) {
                        word_index[word_str] = {Fileid_str};
                    }
                    }

                    {
                    std::string key = word_str + ":" + Fileid_str;
                    try {
                        word_lines.at(key).push_back(std::to_string(line_num));
                    }
                    catch(std::exception& ex) {
                        word_lines[key] = {std::to_string(line_num)};
                    }
                    }
                    }
                    
                    // Add into database
                    // build the word <-> files using sorted set
                    
                    // Ordered Set
                    // [Word]: (fileid1, fileid2)
                   // db_client.zadd(word_str,{"NX"},{std::make_pair(Fileid_str, Fileid_str)});
                    
                    // build the word:file <-> lines using list
                    // [word:fileid]: (line1, line2)
                   // db_client.rpush(word_str+":"+Fileid_str, {std::to_string(line_num)});
                    
                    word_len = 0;
                }
            }
            
        line_num ++;
        }
    cout << "Total File number: "<< Fileid << "\n";
    db_client.commit();
    return 1;
}
int parel(void) {
    #pragma omp parallel
    {
        cout << "hi" << "\n";
    }
}
#include "updatedb_basic.h"

// For using
using std::cout;
using std::string;
using std::priority_queue;
using std::ifstream;

int makeIndex(std::string &dirpath) {

    cpp_redis::client db_client;
    db_client.connect();
    if(db_client.is_connected() == false) {
        errExit("Can't connect to Redis Server. Exited\n");
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
    iterContent(all_files, db_client);

    // Close connections
    db_client.disconnect();
}

int iterFile(std::string &dirpath, DirQueue &a_dirqueue, DirQueue &a_filequeue) {
    // the DIR pointer
    DIR *dirp;
    struct dirent *ent_current;

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
                // TODO: DO SOMETHING
                // Put it in a queue in order to avoid recurisive
                a_dirqueue.push(ent_current->d_name);
                // Test:
            }
            else if(S_ISREG(statbuf.st_mode)) {
                // TODO: DO SOMTHING
                PlainText judger;
                // Plain text should be handled
                if(judger.isText(full_file_path)) {
                    // Put into a file_queue in orders
                    // Then the indexer will get from the queue
                    // use d_name for priority
                    a_filequeue.push(ent_current->d_name, dirpath_c);
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
}

// I still use recursive to track dirs
int iterDirs(std::string &parent_path, std::vector<std::string> &all_files) {
    DirQueue dir_queue;
    // File_queue will be only used once each dir
    static DirQueue file_queue;

    iterFile(parent_path, dir_queue, file_queue);
    // Connect to the datebase
    // Track the files
    while(!file_queue.empty()) {
        std::string file = file_queue.top();
        //file = parent_path + "/" + file;
        // Put it into all_files vector
        all_files.push_back(file);
        cout << file << "\n";
        file_queue.pop();
    }
    while(!dir_queue.empty()) {
        std::string path = dir_queue.top();
        dir_queue.pop();
        path = parent_path + "/" + path;

        // test:
        //std::cout << path << std::endl;
        //
        iterDirs(path, all_files);
    }
}

int iterContent(std::vector<std::string> &all_files, cpp_redis::client &db_client) {
    //
    if(db_client.is_connected() == false) 
        errExit("Can't connect to Redis server.\n");
    // The file id identical for each file;
    // Iter each files:
    for(auto filepath: all_files) {
        readFile(filepath, db_client);
        //db_client.sync_commit();
    // FileId determines the file display order
    }
   // db_client.sync_commit();
    cout << "DataBase has been updated" << "\n";
    // test
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
                    db_client.zadd(word_str,{"NX"},{std::make_pair(Fileid_str, Fileid_str)});
                    // build the word:file <-> lines using list

                    db_client.rpush(word_str+":"+Fileid_str, {std::to_string(line_num)});
                    
                    word_len = 0;
                }
            }
        line_num ++;
        }
    Fileid++;
    cout << "Total File number: "<< Fileid << "\n";
   db_client.sync_commit();
    return Fileid;
}


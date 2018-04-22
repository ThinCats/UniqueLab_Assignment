#include "updatedb_basic.h"

// For using
using std::cout;
using std::string;;
using std::priority_queue;

int iterFile(string &dirpath, DirQueue &a_dirqueue) {
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
        errMsg("can't read the dir: %s", dirpath_c);
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
                //test:
            }
            else if(S_ISREG(statbuf.st_mode)) {
                // TODO: DO SOMTHING
 cout << "\n" << full_file_path << "\n";
                cout << "It's a regular file" << "\n";
            }
        }
        
    }

    // Error detactions:
    if(errno != 0) {
        errMsg("read dir");
    }
    // Close dir
    if(closedir(dirp) == -1) {
        errMsg("Close dir falied");
    }

}

int iterDirs(std::string &parent_path) {
    DirQueue dir_queue;

    iterFile(parent_path, dir_queue);
    while(!dir_queue.empty()) {
        std::string path = dir_queue.top();
        dir_queue.pop();
        path = parent_path + "/" + path;
        std::cout << path << std::endl;
        iterDirs(path);
    }
}
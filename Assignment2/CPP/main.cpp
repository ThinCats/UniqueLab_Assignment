#include "libs/updatedb_basic.h"

using std::cout;
using std::string;
int main(void) {

    std::string root_path = "/";
    iterDirs(root_path);
/*
    DirQueue dir_queue;
    iterFile(root_path, dir_queue);
    
    while(true) {
        string parent_dir = root_path;
        if(dir_queue.empty() == true)
            break;
        else {
            DirQueue subdir_queue;
            std::string path = dir_queue.top();
            dir_queue.pop();
            path = parent_dir + "/" + path;
            iterFile(path, subdir_queue);
        }
    }
*/


 
 
}
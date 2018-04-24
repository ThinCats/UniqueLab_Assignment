#include "libs/updatedb_basic.h"
//#include "libs/searcher.h"

using std::cout;
using std::string;
int main(int argc, char *argv[]) {

    if(argc == 1 || strcmp(*(argv+1),"--help")==0) {
        std::cout << "Do you need help?" << "\n";
        std::cout << "This is the usage for indexer" << "\n";
        std::cout << "USAGE:" << "\n";
        std::cout << *argv << " " << "path " <<  std::endl;
        return 0;
    } else {
        std::string root_path = *(argv+1);
        makeIndex(root_path);
    }
    
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

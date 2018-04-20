#include "updatedb_basic.h"


int iterFile(char *dirpath) {
    // the DIR pointer
    DIR *dirp;
    struct dirent *ent_current;
    
    dirp = opendir(dirpath);
    if(dirp == nullptr) {
        errMsg("can't read the dir: %s", dirpath);
        return;
    }

}
#include "PlainText.h"

bool PlainText::isText(char *filepath) {
    std::string ext;
    // To get suffix
    std::string path = filepath;
    size_t found = path.find_last_of(".");
    ext = path.substr(found+1);
    
    // Not accurate
    if(ext[0] != '\0') {
        for(auto &a: this->ext_data) {
            if(a == ext)
                return true;
        }
    }
    else {
        return false;
    }
}

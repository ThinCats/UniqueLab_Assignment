#include "PlainText.h"

using std::string;
std::vector<std::string> PlainText::ext_data = {
    "txt", "c", "cpp", "h", "py", "json", "js", "conf"
};

bool PlainText::newIsText(char *filepath) {


    if(cookie == nullptr)
        std::cout << "end";
    // Refer to man libmagic
    // Connect to magic database
    bool isPlainText;
    // Load database from default(NULL options)
    // Get mime
    const char *mime = magic_file(cookie, filepath);
    // Compare the file MIME TYPE

    // Avoid core dump
    if(mime == nullptr || strlen(mime) < 5)
        return false;
    isPlainText = !strncmp(mime, "text/", 5);
    // test

    return isPlainText;
}

bool PlainText::isText(char *filepath) {
    string path = filepath;
    string ext;
    size_t found = path.find_last_of(".");
    if(found == path.npos) {
        // DO SOMETHING
        return newIsText(filepath);
        // Unwise action
        
    } else {
        // Unwise action:
        // ext is "xxx"
        ext = path.substr(found+1);
        // Check the ext
        for(auto &a: this->ext_data) {
            
            if(a == ext) 
                return true;
        }
    }

    // Finally:
    return newIsText(filepath);
}

int PlainText::init(void) {
    this->cookie = magic_open(MAGIC_MIME_TYPE);
    if(cookie == nullptr)
        errExit("Connect to Magic database Failed");
    magic_load(cookie, NULL);
}

int PlainText::destruct(void) {
    magic_close(cookie);
}
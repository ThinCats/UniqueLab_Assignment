#include "PlainText.h"

using std::string;
std::vector<std::string> PlainText::ext_data = {
    "txt", "c", "cpp", "h", "py", "json", "js", "conf"
};

bool PlainText::newIsText(char *filepath) {

    // Refer to man libmagic
    // Connect to magic database
    magic_t cookie = magic_open(MAGIC_MIME_TYPE);
    if(cookie == nullptr)
        errExit("Connect to Magic database Failed");
    bool isPlainText;
    // Load database from default(NULL options)
    magic_load(cookie, NULL);
    // Get mime
    const char *mime = magic_file(cookie, filepath);
    // Compare the file MIME TYPE
    isPlainText = !strncmp(mime, "text/", 5);
    // test
    magic_close(cookie);

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
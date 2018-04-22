#ifndef PLAIN_TEXT_H
#define PLAIN_TEXT_H

#include "basic_libs.h"

class PlainText {
    public:
    PlainText() = default;
    bool isText(char *filepath);

    private:
    static std::vector<std::string> ext_data = {
        ".txt", ".c", ".h", ".cpp"; 
    };

}

#endif //  PLAIN_TEXT_H

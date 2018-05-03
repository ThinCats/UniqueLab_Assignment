#ifndef PLAIN_TEXT_H
#define PLAIN_TEXT_H

// For MIME TYPE detaction
#include <magic.h>
#include "basic_libs.h"

// error functions
#include "error_functions.h"

class PlainText {
    public:
    PlainText(int init) {
    }
    bool isText(char *filepath);
    bool newIsText(char *filepath);
    int init(void);
    int destruct(void);
    private:
    magic_t cookie;
    static std::vector<std::string> ext_data;
  

};

#endif //  PLAIN_TEXT_H

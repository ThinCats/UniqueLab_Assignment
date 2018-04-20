#include "libs/updatedb_basic.h"

int main(void) {

    std::string path = "/home/brody";
    DirQueue dir_queue;
    iterFile(path, dir_queue);
}
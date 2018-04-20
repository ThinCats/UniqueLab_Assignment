#include "libs/updatedb_basic.h"

using std::cout;
int main(void) {

    std::string path = "/home/brody";
    DirQueue dir_queue;
    iterFile(path, dir_queue);


    std::string test;
 
    cout << test << '\n';
    dir_queue.push("a");
    dir_queue.push("bsdf");
    dir_queue.push("csdf");
    dir_queue.push("sdffsdf");
    dir_queue.push("zss");
    dir_queue.push("ads");
    cout << dir_queue.top() << "\n";
    dir_queue.pop();
    dir_queue.pop();
    cout << dir_queue.top();
}
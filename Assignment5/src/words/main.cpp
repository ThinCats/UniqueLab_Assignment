#include "libs/word_sort.h"

using std::cout;
using std::string;

int main(int argc, char *argv[]) {

    if(argc == 1 || strcmp(*(argv+1),"--help")==0) {
        std::cout << "Do you need help?" << "\n";
        std::cout << "This is the usage for sorting words" << "\n";
        std::cout << "USAGE:" << "\n";
        std::cout << *argv << " " << "path " <<  std::endl;
        return 0;
    } else {
        std::string root_path = *(argv+1);
        startSort(root_path);
    }

}

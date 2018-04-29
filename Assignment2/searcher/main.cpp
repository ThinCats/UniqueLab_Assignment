#include "libs/searcher_basic.h"

int main(int argc, char *argv[]) {

    // Usage print out
    if(argc == 1 || argc == 2 || strcmp(*(argv+1),"--help")==0) {
        std::cout << "Do you need help?" << "\n";
        std::cout << "This is the usage for searcher" << "\n";
        std::cout << "USAGE:" << "\n";
        std::cout << *argv << " " << "path " << "word1[word2[word3...]]]" << std::endl;
        return 0;
    } else {

        // Check the pathname's length
        if(strlen(*(argv+1)) > 255) {
            errExit("The Path name is too long.\n");
        }
        
        char *pathname = *(argv+1);
        // Check whether the dir can be open
        DIR *tmp_dir;
        if((tmp_dir = opendir(pathname)) == nullptr) {
            errExit("Can't open this dir. Is this really a dir name?\n");
        } else {
            
            // Building keyword_list
            std::vector<std::string> keyword_list;
            closedir(tmp_dir);
            for(int i=2; i < argc;i++) {
                // Word is too long
                if(strlen(*(argv+i)) > 1000) {
                    errExit("We are sorry, Maybe there are no words more than 1000 length\n");
                }
                if(checkValidWord(*(argv+i)) == false) {
                    std::cout << "Ignore the word: " << *(argv+i);
                    std::cout << "  We don't support" << std::endl;
                } else {
                    keyword_list.push_back(*(argv+i));
                }
            }
            
            // Format the pathname
            format(pathname);
            // call the index program to build index
            callIndexer(pathname);

            std::cout << "\n" << "Searching start..\n" << std::endl;
            searchNow(keyword_list);
        }
    }

}
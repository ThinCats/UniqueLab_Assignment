
#include "libs/basic_libs.h"
#include "libs/error_functions.h"
#include "libs/searcher.h"


using std::cout;
using std::string;
using std::vector;
using std::endl;
int main() {
    vector<string> keywords;
    string keyword = "main";
    keywords.push_back(keyword);
    searchNow(keywords);
}
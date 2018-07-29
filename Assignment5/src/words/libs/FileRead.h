#ifndef _FILE_READ_H
#define _FILE_READ_H

#include "basic_libs.h"
// error_print functios
#include "error_functions.h"

// User-edited class
#include "PlainText.h"

// Map
#include <map>

// Type
typedef std::vector<std::string> FileQueue_t;
typedef std::vector<std::string> DirQueue_t;

class FileRead {

  public:
    FileRead(const std::string &a_root_path): root_path(a_root_path) {
      judger.init();
    };
    FileRead() = default;

    const FileQueue_t& get_files() const { return this->all_files;}
    FileQueue_t& build_files_data() {this->iterDirs(this->root_path); return this->all_files;}

    ~FileRead() {
      judger.destruct();
    }
  private:

    std::string root_path;
    PlainText judger;
    FileQueue_t all_files;
    int iterFile(const std::string &dirpath, DirQueue_t &a_dirqueue);
    int iterDirs(const std::string &parent_path);
    
};

int readFile(const std::string &filepath, std::map<std::string, size_t>& word_dict);
// int readFile(const std::string &filepath, std::vector<std::string>& words_save, std::map<std::string, size_t>& word_dict);

#endif // !_FILE_READ_H

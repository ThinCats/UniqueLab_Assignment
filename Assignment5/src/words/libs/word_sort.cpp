#include "word_sort.h"

// For using
using std::cout;
using std::ifstream;
using std::string;

int startSort(std::string &root_path) {

  PlainText judger(1);
  judger.init();

  FileQueue all_files;
  iterDirs(root_path, all_files, judger);
  iterContent(all_files);
  judger.destruct();
  return 0;
}
int iterFile(std::string &dirpath, DirQueue &a_dirqueue, FileQueue &a_filequeue,
             PlainText &judger) {
  // the DIR pointer
  DIR *dirp;
  struct dirent *ent_current;
  // for supporting c
  // max len 255
  char dirpath_c[255];
  strcpy(dirpath_c, dirpath.c_str());
  // for lstat()
  char full_file_path[255];
  struct stat statbuf;

  dirp = opendir(dirpath_c);
  if (dirp == nullptr) {
    errMsg("Can't read the dir: %s", dirpath_c);
    return 0;
  }

  while (true) {
    ent_current = readdir(dirp);
    if (ent_current == nullptr) {
      // std::cout << "end of dir\n";
      break;
    }
    // ignore . and ..
    if (strcmp(ent_current->d_name, ".") == 0 ||
        strcmp(ent_current->d_name, "..") == 0)
      continue;

    // read the file type
    // Generate the full filepath
    strcpy(full_file_path, dirpath_c);
    // TODO: handle the more '/'
    strcat(full_file_path, "/");
    strcat(full_file_path, ent_current->d_name);
    // cout << "full_file_path: " << full_file_path  << std::endl;

    if (lstat(full_file_path, &statbuf) == -1) {
      errMsg("Can't judge the file type");
    } else {
      if (S_ISDIR(statbuf.st_mode)) {
        // Put it in a queue in order to avoid recurisive
        // dirpath_c is a c string indicating the parent path
        // a_dirqueue.push(ent_current->d_name, dirpath_c);
        a_dirqueue.push_back(full_file_path);
      } else if (S_ISREG(statbuf.st_mode)) {
        // TODO: DO SOMTHING

        // Plain text should be handled
        if (judger.isText(ent_current->d_name, full_file_path)) {
          // if(1) {
          // Put into a file_queue in orders
          // Then the indexer will get from the queue
          // use d_name for priority
          // a_filequeue.push(ent_current->d_name, dirpath_c, statbuf.st_mtime,
          // statbuf.st_ino); cout << "text " << full_file_path << std::endl;
          a_filequeue.push_back(full_file_path);
          // std::string path(full_file_path);
          // readFile(path);
        } else {
          cout << "Non text" << full_file_path << std::endl;
        }
        // Test:
      }
    }
  }
  // Error detactions:
  if (errno != 0) {
    // errMsg("read dir");
  }
  // Close dir
  if (closedir(dirp) == -1) {
    errMsg("Close dir falied");
  }

  // Close Judger
}

// I still use recursive to track dirs
int iterDirs(std::string &parent_path, FileQueue &all_files,
             PlainText &judger) {
  DirQueue dir_queue;

  iterFile(parent_path, dir_queue, all_files, judger);

  // Iter the dir_queue to access to subdir
  for (auto &a : dir_queue) {
    iterDirs(a, all_files, judger);
  }
}

int iterContent(FileQueue &all_files) {

  // The file id identical for each file;
  // Iter each files:
  // for(auto fileinfo: all_files) {
  // readFile(fileinfo.filename);
  // FileId determines the file display order
  // }
  std::map<std::string, size_t> word_count;

  for (auto &a : all_files)
    readFile(a, word_count);

  // Assignment
}

// paterns
int readFile(std::string &filepath, std::map<std::string, size_t> word_count) {

  ifstream in_file(filepath, ifstream::in);
  if (!in_file) {
    errMsg("Can not read File:%s\n", filepath.c_str());
    return -1;
  }
  // Open successfully
  // Read the word
  char word[500];

  // For a single word
  char ch;
  int word_len = 0;

  while ((ch = record.get()) != EOF) {
    if (isalnum(ch) || ch == '_') {
      word[word_len++] = ch;
    }
    // There is a break
    else if (word_len != 0) {
      word[word_len] = '\0';
      // std::cout << word_str << std::endl;
      word_count[word]++;

      word_len = 0;
    }
  }
}

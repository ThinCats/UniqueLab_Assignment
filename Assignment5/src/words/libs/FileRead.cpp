#include "FileRead.h"

int FileRead::iterFile(const std::string &dirpath, DirQueue_t &a_dirqueue) {

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
        if (this->judger.isText(ent_current->d_name, full_file_path)) {
          // if(1) {
          // Put into a file_queue in orders
          // Then the indexer will get from the queue
          // use d_name for priority
          // a_filequeue.push(ent_current->d_name, dirpath_c, statbuf.st_mtime,
          // statbuf.st_ino); cout << "text " << full_file_path << std::endl;
          this->all_files.push_back(full_file_path);
          // std::string path(full_file_path);
          // readFile(path);
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

  return 0;

}

int FileRead::iterDirs(const std::string &parent_path) {

  DirQueue_t dir_queue;
  this->iterFile(parent_path, dir_queue);

  // Iter the dir_queue to access to subdir
  for (auto &a : dir_queue) {
    iterDirs(a);
  }
}

int readFile(const std::string &filepath, std::map<std::string, size_t>& word_dict) {

  std::ifstream in_file(filepath, std::ifstream::in);
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
  int word_count = 0;

  while ((ch = in_file.get()) != EOF) {
    if (isalpha(ch)) {
      word[word_len++] = tolower(ch);
    }
    // There is a break
    else if (word_len != 0) {
      word[word_len] = '\0';
      // word_count++;
      // words_save.push_back(word);
      word_dict[word]++;

      word_len = 0;
    }
  }
  in_file.close();
  return word_count;

}
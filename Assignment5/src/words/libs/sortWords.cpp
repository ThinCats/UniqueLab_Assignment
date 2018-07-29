#include "sortWords.h"

bool compare_map(key_val_t& a, key_val_t& b) {
  return a.second > b.second;
}

int threadManager(std::string &root_path) {

  FileRead reader(root_path);
    
  FileQueue_t &all_files = reader.build_files_data();

  std::map<std::string, size_t> word_count;
  
  int num_threads = std::thread::hardware_concurrency() == 0?std::thread::hardware_concurrency():4;

  num_threads++;

  // Gen num-1 threads group
  std::vector<std::thread> threads(num_threads-1);
  const size_t block_size = all_files.size() / num_threads-1;

  file_it block_start = all_files.begin();
  std::cout << "Size: " << block_size << std::endl;

  // std::shared_ptr<block_t> a = std::make_shared<block_t>();
  // Gen word_queue to save words block
  // Threadsafe_queue<std::shared_ptr<block_t> > words_queue);

  std::vector<std::map<std::string, size_t>> word_count_groups(num_threads-1);
  // Gen 3 threads to get words
  for(int i=0; i < num_threads-1; i++) {
    file_it block_end = block_start;
    std::advance(block_end, block_size);

    if(i == num_threads-1)
      block_end = all_files.end();
    
    std::cout << "Start: " << *block_start << std::endl << "End: " << *block_end<< std::endl;
    threads[i] = std::thread(words_worker, block_start, block_end, std::ref(word_count_groups[i]));

    block_start = block_end;
    // threads[i] = std::thread(words_worker, block_start, block_end, std::ref(words_queue));
  }
  // Main thread will do sort
/*
  while(true) {
    auto words_save = words_queue.wait_and_pop();
    for(auto &a: *words_save) {
      std::cout << a << std::endl;
      word_count[a]++;
    }
  }
*/
  for(int i=0;i < num_threads-1;i++) {
    threads[i].join();
    for(auto &a: word_count_groups[i])
      word_count[a.first] += a.second;
  }

  std::vector<key_val_t> counts(word_count.begin(), word_count.end());
  std::sort(counts.begin(), counts.end(), compare_map);

  std::cout << std::endl;
  for(auto &a: counts)
    std::cout << a.first << " occurs " << a.second << " times"<< std::endl;

}

/*
void words_worker_old(file_it start, file_it end, Threadsafe_queue<std::shared_ptr<block_t>> &words_queue) {
  // auto words_save = std::make_shared<block_t>();
  // auto words_save = new std::vector<std::string>;

  int words_len = 0;

  for(auto it=start;it != end;it++) {
    // std::cout << *it << std::endl;
    words_len += readFile(*it, *words_save);

    if(words_len > 10000) {
      std::cout << "Start push " << std::endl;
      words_queue.push(words_save);
      std::cout << "End push" << std::endl;
      words_save = std::make_shared<block_t>();
    }
  }

  std::cout << "Thread END" << std::endl;
  // Do something to sync
}
*/

void words_worker(file_it start, file_it end, std::map<std::string, size_t>& word_count) {

  std::cout << "THREAD: " << std::this_thread::get_id() << " Starts" << std::endl;
  for(auto it=start;it != end;it++) {
    readFile(*it, word_count);
  }

  std::cout << "THREAD: " << std::this_thread::get_id() << " END" << std::endl;
  // Do something to sync
}
#ifndef _THREADSAFE_QUEUE_H
#define _THREADSAFE_QUEUE_H
#include "basic_libs.h"

#include <mutex>
#include <condition_variable>
#include <queue>

template<typename T>
class Threadsafe_queue {
  public:
    Threadsafe_queue(const Threadsafe_queue&);
    Threadsafe_queue() = default;

    void push(T a_val);

    bool try_pop(T &val);

    T wait_and_pop();

    bool empty() const;

  private:
    mutable std::mutex mtx; // For lock
    std::queue<T> data_queue;
    std::condition_variable cond; // For notify

};

#endif // !
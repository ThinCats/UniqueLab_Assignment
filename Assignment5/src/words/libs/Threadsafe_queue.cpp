#include "Threadsafe_queue.h"

template <typename T>
void Threadsafe_queue<T>::push(T a_val) {
  std::lock_guard<std::mutex> guard(this->mtx);
  this->data_queue.push(a_val);
  // Notify
  this->cond.notify_one();

}

template <typename T>
bool Threadsafe_queue<T>::try_pop(T &val) {
  std::lock_guard<std::mutex> guard(this->mtx);
  if(this->data_queue.empty())
    return false;

  val = this->data_queue.front();
  this->data_queue.pop();
  return true;
}

template <typename T>
T Threadsafe_queue<T>::wait_and_pop() {
  std::unique_lock<std::mutex> lock(this->mtx);
  this->cond.wait(lock, [this](){
    return !this->data_queue.empty();
  });

  T val = this->data_queue.front();
  this->data_queue.pop();
  return val;
}

template <typename T>
bool Threadsafe_queue<T>::empty() const {
  std::lock_guard<std::mutex> guard(this->mtx);
  return this->data_queue.empty();
}


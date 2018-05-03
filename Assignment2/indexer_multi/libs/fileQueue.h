#ifndef FILE_QUEUE_H
#define FILE_QUEUE_H
#include "basic_libs.h"
struct file_info {
    std::string filename;
    int file_time;
    int file_id;
};
class FileQueue {
    public:

    void push(char *path);
    // overload
    void push(char *path, char *parent_path, int a_time, int a_id);
    bool empty();
    file_info &top();
    void pop();

    private:
    // The node contains the dirpath and its priority
    class Node {
        friend bool operator < (const  Node &node1, const Node &node2) {
            // TO let smaller first.
            return node1.priority_ > node2.priority_;
        }
        public:
        Node() = default;
        // sorry for that, because for cooperating with C
        Node(char *a_path): fullpath_(a_path) {
           priority_ = calPriority(a_path);
        };
        Node(char *a_path, char *parent_path, int a_time, int a_id):file_nodeid_(a_id), file_time_(a_time) {
            fullpath_ = parent_path;
            fullpath_ += "/";
            fullpath_ += a_path;
            priority_ = calPriority(a_path);
        };
        
        // Get and setter
        int getPriority() const {return this->priority_;}
        std::string &getPath() {return this->fullpath_;}
        void setPath(char *path) {this->fullpath_ = path;}
        int getTime(void) const {return this->file_time_;}
        int getId(void) const {return this->file_nodeid_;}
        
        private:
        int priority_;
        std::string fullpath_;
        int file_time_;
        int file_nodeid_;
        // calculate the priority by 1, 2, 3 letters of the word by ASCII
        // to combine as a 9-bit int nums
        // For example aaa means 097097097
        int calPriority(char *a_path);
    };
    std::priority_queue <FileQueue::Node> queue_;
};

#endif
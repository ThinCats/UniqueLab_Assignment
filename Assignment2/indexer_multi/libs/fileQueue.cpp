#include "fileQueue.h"

void FileQueue::push(char *path) {
   queue_.push(Node(path)); 
}

void FileQueue::push(char *path, char *parent_path, int a_time, int a_id) {
    queue_.push(Node(path, parent_path, a_time, a_id));
}

bool FileQueue::empty() {
    return queue_.empty();
}

file_info &FileQueue::top() {
    Node a_node = queue_.top();
    static file_info a_info;
    a_info.filename = a_node.getPath();
    a_info.file_time = a_node.getTime();
    a_info.file_id = a_node.getId();
    return a_info;
}

void FileQueue::pop() {
    this->queue_.pop();
}


// For sub-node
int FileQueue::Node::calPriority(char *a_path) {
    int len = strlen(a_path);
    int sum = 0;
    if(len <= 0)
        return 0;
    else {
        sum += tolower(a_path[0]) * 10000;
        // At least 1;
        //sum += a_path[0]=='.'?0:a_path[0]*10000;
        if(len >= 2)
            sum += tolower(a_path[1])*100;
        else 
            sum += tolower(a_path[2]);
    }
    return sum;
}
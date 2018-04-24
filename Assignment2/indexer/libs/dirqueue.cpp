#include "dirqueue.h"

void DirQueue::push(char *path) {
   queue_.push(Node(path)); 
}

void DirQueue::push(char *path, char *parent_path) {
    queue_.push(Node(path, parent_path));
}

bool DirQueue::empty() {
    return queue_.empty();
}

std::string &DirQueue::top() {
    Node a_node = queue_.top();
    static std::string a_path;
    a_path = a_node.getPath();
    return a_path;
}

void DirQueue::pop() {
    this->queue_.pop();
}


// For sub-node
int DirQueue::Node::calPriority(char *a_path) {
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
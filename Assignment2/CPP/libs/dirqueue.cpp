#include "dirqueue.h"

void DirQueue::push(char *path) {
   Node a_node = Node(path);
   queue_.push(a_node); 
}

bool DirQueue::empty() {
    return queue_.empty();
}

std::string &DirQueue::top() {
    Node a_node = queue_.top();
    static std::string a_path = a_node.getPath();
    return a_path;
}

void DirQueue::pop() {
    queue_.pop();
    Node a_node = queue_.top();
    std::cout << a_node.getPath();
}


// For sub-node
int DirQueue::Node::calPriority(char *a_path) {
    int len = strlen(a_path);
    if(len <= 0)
        return 0;
    // only 1 word
    else if(len <= 1)
        return a_path[0]*10000;
    else if(len <= 2)
        return a_path[0]*10000 + a_path[1]*100;
    else
        return a_path[0]*10000 + a_path[1]*100 + a_path[2];
}
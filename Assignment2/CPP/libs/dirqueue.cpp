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
    return a_node.getPath();
}

void DirQueue::pop() {
    queue_.pop();
}


// For sub-node
int DirQueue::Node::calPriority(char *a_path) {
    int len = strlen(a_path);
    if(len <= 1)
        return 0;
    // only 1 word
    else if(len <= 2)
        return a_path[0]*10000;
    else if(len <= 3)
        return a_path[0]*10000 + a_path[1]*100;
    else
        return a_path[0]*10000 + a_path[1]*100 + a_path[2];
}
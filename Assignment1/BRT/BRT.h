#ifndef BRT_H
#define BRT_H

#include <algorithm>

using T = double;

class BRT {

public:
    

    BRT(T& element) {};
    BRT() = default;
    
    void insert(const T& element);
    int count(const T& element) const; //V
    bool empty() const;  //V
    void erase(const T& element);  

    // An override will be at private
    void clear() { clear(this->root); }; //V
     
    size_t size();

private:
    size_t tree_size = 0;
    class Node {
    public:
        Node(const T& a_key): key(a_key) {};

        void set_red(bool a_is_red);
        // 为compare函数提供返回值
        const int kBigger = 1;
        const int kSmaller = -1;
        const int kEqual = 0;

        //compare
        int Compare(const T& a_key) const {
            return (this->key==a_key)?kEqual:(this->key>a_key?kBigger:kSmaller);
        }
        //is_red
        bool is_red() const;

        //rotateLeft
        Node *rotateLeft(Node *a_node);
        Node *rotateRight(Node *a_node);
        
        Node *left;
        Node *right;
        T key;
        size_t sub_size;
    private:
        bool red;
    };

    Node* root;
    //override
    void clear(Node* root);

    //Refresh size
    void RefreshSize();


};

#endif
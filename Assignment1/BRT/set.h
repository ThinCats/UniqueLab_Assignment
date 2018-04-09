#ifndef BRT_H
#define BRT_H

#include <algorithm>

using T = double;

class Set {

public:


    Set(T& element) {};
    Set() = default;

    void deleteMax();
    void deleteMin();

    void insert(const T& element);
    int count(const T& element) const; //V
    bool empty() const;  //V
    void erase(const T& element);

    // An override will be at private
    void clear() { clear(this->root); this->root = nullptr; }; //V

    size_t size();
private:
    //size_t tree_size = 0;
    class Node {
    public:
        Node(const T& a_key, bool a_red): key(a_key), red(a_red) {};
        Node(const T& a_key): key(a_key) {};

        void set_red(bool a_is_red);
        // 为compare函数提供返回值
        const int kBigger = 1;
        const int kSmaller = 2;
        const int kEqual = 3;

        //compare
        int Compare(const T& a_key) const; 
        //is_red
        bool is_red() const;

        //rotateLeft
        Node *rotateLeft(Node *a_node);
        Node *rotateRight(Node *a_node);
        Node *rotateMiddle(Node *a_node);
        
        //erase
        Node* moveRedLeft(Node* a_node);
        Node* moveRedRight(Node* a_node);
        Node* fatherGiveColor(Node* a_node);
        
        Node *left_ = nullptr;
        Node *right_ = nullptr;
        T key;
        size_t sub_size = 0;
    private:
        bool red = false;
    };

    Node* root = nullptr;
    size_t tree_size = 0;
    //Rotates to formalize tree
    Node *rotates(Node *a_node);
    //override
    void clear(Node* root);
    Node* insert(const T& ele, Node* a_node);
    Node* erase(const T& ele, Node* a_node);
    //Update size
    void UpdateSize();
    //Size override
    size_t size(Node *a_node);

    //erase
    Node* deleteMin(Node* a_node);
    Node* deleteMax(Node* a_node);

    //Max
    Node* getMax(Node* a_node);
    Node* getMin(Node* a_node);
};

#endif

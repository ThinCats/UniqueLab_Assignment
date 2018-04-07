#include "BRT.h"

// ─── FOR CLASS BRT ──────────────────────────────────────────────────────────────

// ─── FOR PUBLIC ─────────────────────────────────────────────────────────────────



/**
 * Return whether the set contains the element.
 * Return 1 if contains, 0 otherwise.
 */

// ─── PESUCODE ───────────────────────────────────────────────────────────────────
/*  
    set current = root
    if(current == NULL)
        return 0
    if(current.key == ele)
        return 1
    if(current.key > ele)
        find in right tree
    if(current.key < ele)
        find in left tree
*/
// ────────────────────────────────────────────────────────────────────────────────

    
int BRT::count(const T &ele) const {
    Node *current = this->root;
    //Change current to go into trees
    while(1) {
        if(current == nullptr)
            return 0;
        if(current->Compare(ele) == current->kEqual)
            return 1;
        if(current->Compare(ele) == current->kBigger)
            current = current->right;
        else
            current = current->left;
    }    
}

/**
 * Return true if the set is empty, false otherwise.
 */
bool BRT::empty() const {
    if(this->root == nullptr)
        return true;
    else
        return false;
}

/**
 * Clear all elements in set. Reset size to 0
 */

// ─── PESUCODE ───────────────────────────────────────────────────────────────────
/*
    For each node:
        if(node == bottom_node)
            delete node
        delete left sub_tree
        delete right sub_tree
*/
// ────────────────────────────────────────────────────────────────────────────────

void BRT::clear(BRT::Node *a_root) {
    
    if(a_root == nullptr)
        return;
    if(a_root->left == nullptr && a_root->right == nullptr)
    {
        delete a_root;
        return;
    }
        
    clear(a_root->left);
    clear(a_root->right);
}

/**
 * To insert an element
 * Also can be the initial function.
 */
// ─── PESUCODE ───────────────────────────────────────────────────────────────────
/*
    def insert(ele):
        if(tree is empty)
            init
        def (insert as BFT):
            if(ele == node.key)
                do nothing
            if(ele < node.key)
                insert in left tree
            if(ele > node.key)
                insert in right tree
            Update node to prevNode->subNode

        Change the node's color
        def (Format the node):
            if()


*/

// ────────────────────────────────────────────────────────────────────────────────
void BRT::insert(const T &ele) {
    //initial
    if(this->empty()) {
        this->root = new Node(ele);
        this->root->set_red(false);
    }
}

// ────────────────────────────────────────────────────────────────────────────────


// ────────────────────────────────────────────────────────────────────────────────
// ─── FOR SUB CLASS NODE ─────────────────────────────────────────────────────────

void BRT::Node::set_red(bool a_is_red) {
    this->red = a_is_red;
}

bool BRT::Node::is_red() const {
    return this->red;
}

BRT::Node *BRT::Node::rotateLeft(Node *a_node) {
    Node *tmp_right = a_node->right;
    //把右边结点的锅甩到a_node
    a_node->right = tmp_right->left;
    //重新链接
    tmp_right->left = a_node;
    //接源结点的颜色
    tmp_right->set_red(a_node->is_red());
    //源结点变为红色
    a_node->set_red(true);
    
    return tmp_right; 
}

BRT::Node *BRT::Node::rotateRight(Node *a_node) {
    Node *tmp_left = a_node->left;
    a_node->left = tmp_left->right;
    tmp_left->right = a_node;
    tmp_left->set_red(a_node->is_red());

    a_node->set_red(true);
    return tmp_left;
}


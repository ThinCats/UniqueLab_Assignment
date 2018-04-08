#include "Set.h"

// ─── FOR CLASS Set ──────────────────────────────────────────────────────────────

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


int Set::count(const T &ele) const {
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
bool Set::empty() const {
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

void Set::clear(Set::Node *a_root) {

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
            if(Node->left is red)
                rotateLeft(node);
            if(Node->left, leftNode->left is red):
              node = rotateRight(node);
            if(node->right , node->left is red):
                rotateMiddle(node);



*/

// ────────────────────────────────────────────────────────────────────────────────

Set::Node* Set::rotates(Node* a_node) {
    // Tranvers:
    if(a_node->right == nullptr)
        ;
    else if(a_node->right->is_red())
        a_node = a_node->rotateLeft(a_node);

    // is the node at the bottom?
    if(a_node->left->left == nullptr)
        ;
    else if(a_node->left->is_red() && a_node->left->left->is_red())
        a_node = a_node->rotateRight(a_node);

    if(a_node->left == nullptr || a_node->right == nullptr)
        ;
    else if(a_node->left->is_red() && a_node->right->is_red())
        a_node = a_node->rotateMiddle(a_node);
    return a_node;
}

void Set::insert(const T& ele) {
    this->root = insert(ele, this->root);
    //Update size
    UpdateSize();
}

Set::Node* Set::insert(const T& ele, Set::Node* a_node) {
    if(a_node == nullptr)
        return new Node(ele);
    if(a_node->Compare(ele) == a_node->kEqual)
        return a_node;
    else if(a_node->Compare(ele) == a_node->kBigger) {
        a_node->right = insert(ele, a_node->right);
        a_node->right->set_red(true);
    }
    else if(a_node->Compare(ele) == a_node->kSmaller) {
        a_node->left = insert(ele, a_node->left);
        a_node->left->set_red(true);
    }

    a_node = rotates(a_node);

    return a_node;


}

/**
 * Get set size
*/
size_t Set::size() {
    if(root == nullptr)
        return 0;
    else
        return root->sub_size;
}

/**
 * Reset size for each node
 * Size: Node's number of subNodes
 * Exp> node.size = node->left.size + node->right.size + 1;
*/
size_t Set::size(Node *a_node) {
    if(a_node == nullptr)
        return 0;
    a_node->sub_size =  size(a_node->left) + size(a_node->right) + 1;
    return a_node->sub_size;
}

/**
 * Update the each node's size by calling size(root)
*/
void Set::UpdateSize() {
    size(this->root);
}

// ────────────────────────────────────────────────────────────────────────────────


// ────────────────────────────────────────────────────────────────────────────────
// ─── FOR SUB CLASS NODE ─────────────────────────────────────────────────────────

void Set::Node::set_red(bool a_is_red) {
    this->red = a_is_red;
}

bool Set::Node::is_red() const {
    return this->red;
}

Set::Node *Set::Node::rotateLeft(Node *a_node) {
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


Set::Node *Set::Node::rotateRight(Node *a_node) {
    Node *tmp_left = a_node->left;
    a_node->left = tmp_left->right;
    tmp_left->right = a_node;
    tmp_left->set_red(a_node->is_red());

    a_node->set_red(true);
    return tmp_left;
}

/*
* To make a 4-Node to be a 3-Node
*/
Set::Node *Set::Node::rotateMiddle(Node *a_node) {
    // Just convert the color
    a_node->left->set_red(false);
    a_node->right->set_red(false);
    a_node->set_red(true);
    return a_node;
}

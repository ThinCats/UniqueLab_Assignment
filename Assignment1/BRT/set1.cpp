#include "set.h"

//#define DEBUG
#ifdef DEBUG
#include <iostream>
#endif //DEBUG
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
            current = current->right_;
        else
            current = current->left_;
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
    if(a_root->left_ == nullptr && a_root->right_ == nullptr)
    {
        delete a_root;
        return;
    }

    clear(a_root->left_);
    clear(a_root->right_);
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

    
    if(a_node->right_==nullptr && a_node->left_==nullptr)
        return a_node;
    // Tranvers:
    if(a_node->right_ == nullptr)
        ;
    else if(a_node->right_->is_red())
        a_node = a_node->rotateLeft(a_node);

    if(a_node->left_ == nullptr)
        ;
    // is the node at the bottom?
    else if(a_node->left_->left_ == nullptr)
        ;
    else if(a_node->left_->is_red() && a_node->left_->left_->is_red())
        a_node = a_node->rotateRight(a_node);

    if(a_node->left_ == nullptr || a_node->right_ == nullptr)
        ;
    else if(a_node->left_->is_red() && a_node->right_->is_red())
        a_node = a_node->rotateMiddle(a_node);
    return a_node;
}

void Set::insert(const T& ele) {
    if(this->count(ele) == 1)
        return;
    this->root = insert(ele, this->root);
    //Update size
    // If it is efficient insert
    root->set_red(false);
    tree_size++;
}

Set::Node* Set::insert(const T& ele, Set::Node* a_node) {
    if(a_node == nullptr) {
        return new Node(ele, true);
    }
    if(a_node->Compare(ele) == a_node->kEqual)
        ;
    else if(a_node->Compare(ele) == a_node->kBigger) {
        a_node->right_ = insert(ele, a_node->right_);
    }
    else if(a_node->Compare(ele) == a_node->kSmaller) {
        a_node->left_ = insert(ele, a_node->left_);
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
        return this->tree_size;
}

/**
 * Reset size for each node
 * Size: Node's number of subNodes
 * Exp> node.size = node->left.size + node->right.size + 1;
*/
size_t Set::size(Node *a_node) {
    if(a_node == nullptr)
        return 0;
    a_node->sub_size =  size(a_node->left_) + size(a_node->right_) + 1;
    return a_node->sub_size;
}
/**
 * Update the each node's size by calling size(root)
*/
void Set::UpdateSize() {
    size(this->root);
}

// ─── ERASE ──────────────────────────────────────────────────────────────────────

/**
 * 删除最小值
 * 1. 依据：
 *  删除3 or 4结点不会影响平衡性， 所以将删除结点转换为3/4 结点
 * 2. 实现:
 *  1.向下变换（转换结点至3/4）
 *  2. 向上修正 （配平所有4结点， 转化为左倾红黑树）
 * 3. 向下变换:
 *  1. 准则:
 *      1. 左结点为3结点， 继续。(这说明删除结点在3结点)
 *      1. 结点的左右子结点均为2结点， 直接将这两个结点与父结点的一个元素组合成4结点
 *      2. 结点的左（右）子结点为2结点， 而它的兄弟结点>2结点， 向他的兄弟结点借一个元素转换成3结点
 *  2. 对于红黑树:
 *      1. 判断: 判断左右子结点类型
 *          判断子结点及其子子结点的颜色
 *          目标删除结点: 判断其颜色， 兄弟结点， 判断其left子结点颜色(认为向下的红黑树都左倾)
 *      2. 借子结点: 根据情况进行左旋右旋转等变换
 *      3. 搜索: 若右边（对删除最小而言）结点为红， 左旋
 *          目的是方便父结点给子结点元素。
*/

/**
 * Erase实现:
 * 关键： 不是直接删除目标结点， 而是巧妙地将目标结点转换为已有的bottom结点，然后删除bottom结点， 规避了许多情况
 * 实现： RedBlack.pdf 取得是min， 这里我就取max， 但本质是一样的。
 *  1. 找到目标结点
 *  2. 从目标结点开始， 找到最大的小于目标结点的树， 并替换(左树最大值)
 *  3. 从目标结点开始， 找到被替换的结点， 删除(类似于删除最大最小)
 *  4. 从下到上修正
 * 注意: 由于目标结点并不是真正的根结点， 所以从上到下的变换依然要从根结点开始。左结点左变换， 右结点右变换， 直到找到目标结点。
*/

Set::Node* Set::deleteMin(Node* a_node) {
    
    //说明到底了
    if(a_node->left_ == nullptr) {
        delete a_node;
        return nullptr;
    }

    //左子结点是父结点的一部分()
    if(a_node->left_->is_red() == true)
        ;
    //左子结点是3/4结点
    //子结点倒数 
    if(a_node->left_->left_==nullptr)
        ;
    else if(a_node->left_->left_->is_red() == true)
        ;
    else {
        a_node = a_node->moveRedLeft(a_node);
    }

    //继续向下搜索
    a_node->left_ = deleteMin(a_node->left_);

    //向上修正
    return rotates(a_node);
}

Set::Node* Set::deleteMax(Node* a_node) {

    //a_node is the last one
    if(a_node->right_ == nullptr && a_node->left_ == nullptr) {
        delete a_node;
        return nullptr;
    }
    //向右转， 为了能方便给子结点元素
    // 同时， 删除时也不会影响其他树
    if(a_node->left_->is_red() == true)
        a_node = a_node->rotateRight(a_node);
        
    //if(a_node->right_ == nullptr)
      //  return nullptr;
    
    if(a_node->right_->is_red() == true)
        ;
    //默认为左倾树
    else if(a_node->right_->left_ == nullptr)
        ;
    else if(a_node->right_->left_->is_red() == true)
        ;
    else {
        a_node = a_node->moveRedRight(a_node);

    }
    a_node->right_ = deleteMax(a_node->right_);

    return rotates(a_node); 
}

void Set::erase(const T& element) {
    if(this->count(element) != 1)
        return;
    root = erase(element, root);
    root->set_red(false);
    tree_size --;
    
    
}
//override
Set::Node* Set::erase(const T& ele, Node* a_node) {
    

    int cmp = a_node->Compare(ele);

    if(cmp == a_node->kSmaller) {
        if(a_node->left_->is_red() == true)
            ;
        else if(a_node->left_->left_==nullptr) {
            a_node = a_node->moveRedLeft(a_node);
        }
            
        else if(a_node->left_->left_->is_red() == true)
            ;
        else 
            a_node = a_node->moveRedLeft(a_node);
        a_node->left_ = erase(ele, a_node->left_);
    }

    else if(cmp == a_node->kBigger) {
        if(a_node->left_==nullptr)
            ;
        else if(a_node->left_->is_red())
            a_node = a_node->rotateRight(a_node);
        
        if(a_node->right_->is_red())
            ;
        else if(a_node->right_->left_ == nullptr)
            ;
        else if(a_node->right_->left_->is_red())
            ;
        else
            a_node = a_node->moveRedRight(a_node);
        a_node->right_ = erase(ele, a_node->right_);
    }

    //Up all are serching the tartget node
    else if(cmp == a_node->kEqual) {
        //左树没东西了。。。
        if(a_node->left_ == nullptr && a_node->right_ == nullptr) {
            delete a_node;
            return nullptr;
        }
        else if(a_node->left_ == nullptr) {
            ;
        }
        else {
            a_node->key = getMax(a_node->left_)->key;
            a_node->left_ = deleteMax(a_node->left_);
        }
    }

    //Fix from bottom to up
    a_node = rotates(a_node);
    return a_node;
}

#ifdef DEBUG
 

void Set::deleteMax() {
    deleteMax(root);
    this->tree_size--;
}

void Set::deleteMin() {
    deleteMin(root);
    this->tree_size--;
}
#endif //DEBUG
Set::Node* Set::getMax(Node *a_node) {
    while(a_node->right_ != nullptr)
    {
        a_node = a_node->right_;
    }
    return a_node;
}

Set::Node* Set::getMin(Node *a_node) {
    while(a_node->left_ != nullptr) {
        a_node = a_node->left_;
    }
    return a_node;
}
// ────────────────────────────────────────────────────────────────────────────────
// ─── FOR SUB CLASS NODE ─────────────────────────────────────────────────────────

void Set::Node::set_red(bool a_is_red) {
    this->red = a_is_red;
}

bool Set::Node::is_red() const {
    return this->red;
}

Set::Node *Set::Node::rotateLeft(Node *a_node) {
    Node *tmp_right = a_node->right_;
    //把右边结点的锅甩到a_node
    a_node->right_ = tmp_right->left_;
    //重新链接
    tmp_right->left_ = a_node;
    //接源结点的颜色
    tmp_right->set_red(a_node->is_red());
    //源结点变为红色
    a_node->set_red(true);

    return tmp_right;
}


Set::Node *Set::Node::rotateRight(Node *a_node) {
    Node *tmp_left = a_node->left_;
    a_node->left_ = tmp_left->right_;
    tmp_left->right_ = a_node;
    tmp_left->set_red(a_node->is_red());

    a_node->set_red(true);
    return tmp_left;
}

/*
* To make a 4-Node to be a 3-Node
*/
Set::Node *Set::Node::rotateMiddle(Node *a_node) {
    // Just convert the color
    a_node->left_->set_red(false);
    a_node->right_->set_red(false);
    a_node->set_red(true);
    return a_node;
}

// To make a normal node to be 4-node
// A liitle famirlar with rotateMiddle UPUP|
Set::Node* Set::Node::fatherGiveColor(Node* a_node) {
    if(a_node->left_!=nullptr)
        a_node->left_->set_red(true);
    if(a_node->right_!=nullptr)
        a_node->right_->set_red(true);
    a_node->set_red(false);
    return a_node;
}

Set::Node* Set::Node::moveRedLeft(Node* a_node) {
    // Trans
    a_node = fatherGiveColor(a_node);
    

    // if subNodes are all 2-node
    //End node
    if(a_node->right_->left_==nullptr)
        ;
    
    else if(a_node->right_->left_->is_red() == false)
        ;
    //if brother node is 3-node
    else {
        // to make brother node easier to give element
        a_node->right_ = rotateRight(a_node->right_);
        // to make smallest ele from broter to be father node
        a_node = rotateLeft(a_node);
        // Finish giving, reduce ele in brother node (tmp 4-node reduce)
        a_node = rotateMiddle(a_node);
    }

    return a_node;
}

//For max
Set::Node* Set::Node::moveRedRight(Node* a_node) {
    a_node = fatherGiveColor(a_node);

    if(a_node->left_==nullptr)
        ;
    else if(a_node->left_->left_==nullptr)
        ;
    else if(a_node->left_->left_->is_red() == false)
        ;
    else {
        a_node = rotateRight(a_node);
        a_node = rotateMiddle(a_node);
    }

    return a_node;
}


//test
#ifdef DEBUG

int main(void) {
    Set a;
    //a.insert(1);
    //a.insert(2);
    int j = 1000000;
    int k; 
    for(int i=0 ;i < j;i++)
        a.insert(i + 3.4);
    for(int i=100;i > 0;i--) {
        a.erase(i*i);
    }
    std::cout << a.count(1) << '\n';
    std::cout << a.size();
}
#endif //DEBUG
int Set::Node::Compare(const T& a_key) const {

    int a = (this->key==a_key)?this->kEqual:(this->key<a_key?this->kBigger:this->kSmaller);
    return a;
       
}
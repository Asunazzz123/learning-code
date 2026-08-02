#include<iostream>
#include<optional>
struct BNode{
    std::optional<int> weight;
    BNode* left;
    BNode* right;

    bool is_leaf() const{
        return !left && !right;
    }
};

int WPL_impl(BNode* node, int depth) {
    if (node == nullptr) {
        return 0;
    }

    if (node->is_leaf()) {
        return node->weight.value() * depth;
    }

    return WPL_impl(node->left, depth + 1)
         + WPL_impl(node->right, depth + 1);
}

int WPL(BNode* rt) {
    return WPL_impl(rt, 0);
}
    
int main(){
    //          root
    //         /    \
    //      (2)     node
    //              /  \
    //            (3)  (5)
    //
    // WPL = 2 * 1 + 3 * 2 + 5 * 2 = 18
    BNode leaf1{2, nullptr, nullptr};
    BNode leaf2{3, nullptr, nullptr};
    BNode leaf3{5, nullptr, nullptr};
    BNode inner{std::nullopt, &leaf2, &leaf3};
    BNode root{std::nullopt, &leaf1, &inner};

    int result = WPL(&root);
    std::cout << "WPL = " << result << " (expected 18)\n";

    return result == 18 ? 0 : 1;
}


    



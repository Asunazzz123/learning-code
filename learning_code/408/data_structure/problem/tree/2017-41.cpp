#include<iostream>
#include<string>

struct node{
    char data;
    node* left;
    node* right;
    bool is_leaf() const{
        return !left && !right;
    }
};


std::string inorder(node* rt,int height) {
    bool is_root = (height == 1);
    if (rt == nullptr) {
        return "";
    }
    std::string current_data = std::string(1, rt->data);
    std::string res = inorder(rt->left,height +1) + current_data + inorder(rt->right,height+1);
    if (!is_root && !rt->is_leaf()){
        res = "(" + res + ")";
    }
    return res;
}

int main(){
    node leaf1{'a',nullptr,nullptr};
    node leaf2{'b',nullptr,nullptr};
    node leaf3{'c',nullptr,nullptr};
    node leaf4{'d',nullptr,nullptr};
    node r1{'+',&leaf1,&leaf2};
    node r2{'/',&leaf3,&leaf4};
    node r3{'*',&r1,&r2};
    std::string res = inorder(&r3,1);
    std::cout << "Result:\n" << res << std::endl;
    return 0;
}
#include<iostream>
#include<string>

struct node{
    char data;
    node* left;
    node* right;
};


void Tranverse(node* root,int height){
    if (root == nullptr){
        std::cout << "\n";
    }
    bool is_leaf = !(root->left) && !(root->right);
    bool need_param = (!is_leaf && height > 1);
    if (need_param) std::cout << "(";
    Tranverse(root->left,height+1);
    std::cout << root->data << '\n';
    Tranverse(root->right,height+1);
    if (need_param) std::cout << ")";
}

void MOTree(node* root){
    Tranverse(root,1);
    std::cout << '\n';
}
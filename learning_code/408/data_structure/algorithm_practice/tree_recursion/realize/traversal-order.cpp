#include<iostream>
#include<vector>



// 先序序列 1 2 4 3 5 6
// 中序序列 2 4 1 5 3 6
// 后序序列 4 2 5 6 3 1

struct node
{
    int data;
    node* left;
    node* right;
};


void preorder(node* root, int h, std::vector<int> &res){
    res.push_back(root->data);
    if (root->left != nullptr) preorder(root->left,h+1,res);
    if (root->right != nullptr) preorder(root->right,h+1,res);
}


void inorder(node* root, int h, std::vector<int> &res){
    if (root->left != nullptr) inorder(root->left,h+1,res);
    res.push_back(root->data);
    if (root->right != nullptr) inorder(root->right,h+1,res);
}


void postorder(node* root, int h, std::vector<int> &res){
    if (root->left != nullptr) postorder(root->left,h+1,res);
    if (root->right != nullptr) postorder(root->right,h+1,res);
    res.push_back(root->data);
}




int main(){
    node p4 = node{4,nullptr,nullptr};
    node p5 = node{5,nullptr,nullptr};
    node p6 = node{6,nullptr,nullptr};
    node p2 = node{2,nullptr,&p4};
    node p3 = node{3,&p5,&p6};
    node p1 = node{1,&p2,&p3};

    std::vector<int> preres;
    std::vector<int> inres;
    std::vector<int> postres;
    preorder(&p1,1,preres);
    inorder(&p1,1,inres);
    postorder(&p1,1,postres);

    std::cout << "Preorder" << '\n';
    for (int x:preres){
        std::cout << x;
    }

    std::cout << '\n' << "Inorder" << '\n';
    for (int x:inres){
        std::cout << x;
    }

    std::cout << '\n' << "Postorder" << '\n';
    for (int x:postres){
        std::cout << x;
    }
    std::cout << '\n';
}
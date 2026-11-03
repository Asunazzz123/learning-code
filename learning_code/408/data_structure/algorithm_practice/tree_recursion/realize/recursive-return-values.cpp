#include<iostream>
#include<vector>


struct node
{
    int data;
    node* left;
    node* right;
};


void countNodes(node* root, int h, int &num){
    num += 1;
    if (root -> left != nullptr) countNodes(root->left,h+1,num);
    if (root -> right != nullptr) countNodes(root->left,h+1,num);
}

void countLeaves(node* root, int h, int &num){
    if(root->left==nullptr && root->right==nullptr) num++;
    if (root->left != nullptr) countLeaves(root->left,h+1,num);
    if (root->right != nullptr) countLeaves(root->right,h+1,num);
}

void treeHeight(node* root, int h, int &num){
    if (root == nullptr) return;
    num = h;
    if (root->left != nullptr) treeHeight(root->left,h+1,num);
    if (root->right != nullptr) treeHeight(root->right,h+1,num);
}



int main(){
    node p2 = node{2,nullptr,nullptr};
    node p3 = node{3,nullptr,nullptr};
    node p1 = node{1,&p2,&p3};

    int node_num = 0;
    countNodes(&p1,1,node_num);
    std::cout << node_num << '\n';

    int leaves = 0;
    countLeaves(&p1,1,leaves);
    std::cout << leaves << '\n';

    int height = 0;
    treeHeight(&p1,1,height);
    std::cout << height << '\n';
}



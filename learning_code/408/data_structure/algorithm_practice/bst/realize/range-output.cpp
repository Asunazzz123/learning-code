#include<iostream>


struct TreeNone{
    int data;
    TreeNone* left;
    TreeNone* right;
};


void printrange(TreeNone* root, int low, int high){
    // 中序遍历
    if (root->left!=nullptr){
        printrange(root->left,low,high);
    }
    if (root->data <= high && root->data >= low){
       std::cout << root->data;
    }
    if (root->right!=nullptr){
        printrange(root->right,low,high);
    }
}


int main(){
    TreeNone* n3 = new TreeNone{1,nullptr,nullptr};
    TreeNone* n4 = new TreeNone{3,nullptr,nullptr};
    TreeNone* n5 = new TreeNone{5,nullptr,nullptr};
    TreeNone* n6 = new TreeNone{7,nullptr,nullptr};
    TreeNone* n1 = new TreeNone{2,n3,n4};
    TreeNone* n2 = new TreeNone{6,n5,n6};
    TreeNone* n0 = new TreeNone{4,n1,n2};
    TreeNone* ptrs[] = {n0,n1,n2,n3,n4,n5,n6};
    // printrange(n0,3,6);
    printrange(n0,4,6);
    std::cout << '\n';

    for (TreeNone* ptr : ptrs){
        delete ptr;
    }
}

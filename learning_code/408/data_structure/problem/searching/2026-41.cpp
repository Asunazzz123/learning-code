#include<iostream>
#include<vector>


int abs(int x,int y){
    return x>=y ? x-y : y-x;
}


struct node{
    int data;
    node* left;
    node* right;
};


int solve(node* root, int k, std::vector<int> keys){
    keys.clear();
    int min_diff = std::numeric_limits<int>::max();
    while (root != nullptr){
        int diff = abs(root->data, k);
        if (diff < min_diff) {
            min_diff = diff;
            keys.clear();
            keys.push_back(root->data);
        }
        else if (diff == min_diff){
            keys.push_back(root->data);
        }
        if (root->data == k) break;
        // 根据 BST 的有序性移动指针, 时间复杂度为O(n)
        else if (root->data > k) root = root->left;
        else root = root->right;
    }
    return min_diff;
}



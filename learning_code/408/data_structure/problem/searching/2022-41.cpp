#include<iostream>
#include<vector>
#include<cmath>
#define MAX_SIZE 100
struct SqBTree{
    std::vector<int> SqBNode;
    int ElemNum;
};


bool isBST_impl(SqBTree* t, int i, int lower, int upper){
    if (i >= t->ElemNum) {
        return true;
    }
    if (t->SqBNode[i] == -1){
        return true;
    }
    int value = t->SqBNode[i];
    
    if (value <= lower || value >= upper){
        return false;
    }
    int left  = 2 * i + 1;
    int right = 2 * i + 2;

    return isBST_impl(t, left, lower, value) && isBST_impl(t, right, value, upper);
}



bool isBST(SqBTree* t){
    if (t == nullptr){
        return false;
    }
    return isBST_impl(t,0,-100,100);
}





int main(){
    std::vector<int> list1 = {40,25,60,-1,30,-1,80,-1,-1,27};
    std::vector<int> list2 = {40,50,60,-1,30,-1,-1,-1,-1,-1,35};
    SqBTree tree1{list1,10};
    SqBTree tree2{list2,11};
    std::cout << std::boolalpha
          << "tree1: " << isBST(&tree1) << '\n'
          << "tree2: " << isBST(&tree2) << '\n';
    
    return 0;
}
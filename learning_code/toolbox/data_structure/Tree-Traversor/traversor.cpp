#include<iostream>

#define PREORDER 0
#define INORDER 1
#define POSTORDER 2

struct node{
    int data;
    node* lchild;
    node* rchild;
};

void visit(node* t){
    std::cout << "data" << std::endl;
}

void traversor(node* t,int mode){
    if (t != nullptr){
        if (mode == PREORDER){
            visit(t);
            traversor(t->lchild,mode);
            traversor(t->rchild,mode);
        }
        else if (mode == INORDER){
            traversor(t->lchild,mode);
            visit(t);
            traversor(t->rchild,mode);
        }
        else if (mode == POSTORDER){
            traversor(t->lchild,mode);
            traversor(t->rchild,mode);
            visit(t);
        }
    }
}

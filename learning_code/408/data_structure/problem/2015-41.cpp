#include<iostream>
#include<vector>

struct node
{
    int data;
    node* next;
};

int _abs(int n){
    if (n <= 0){
        return -n ;
    }
    return n;
}

void DeleteSameNode(node* head, int n){
    std::vector<bool> samenode(n+1 , false);
    node* tmp = head;
    while (tmp -> next != nullptr)
    {
        node* target = tmp -> next;
        int val = _abs(tmp -> data);
        if (!samenode[val]){
            samenode[val] = true;
            tmp = tmp -> next;
        }
        else{
            tmp -> next = target -> next;
            delete target;
        }
    }
}




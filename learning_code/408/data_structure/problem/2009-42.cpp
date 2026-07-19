#include <iostream>


struct node{
    int data;
    node* next;  
};



int searching(node* link,int* data, int k){
    if (link == nullptr || data == nullptr || k <= 0) {
        return 0;
    }
    node* fast = link->next;
    node* slow = link->next;
    
    for (int i = 0; i < k ; i++){
        if (fast == nullptr){
            return 0;
        }
        fast = fast -> next;
    }

    while(fast != nullptr){
        fast = fast -> next;
        slow = slow -> next;
    }

    *data = slow -> data;
    return 1;
    
}
#include <iostream>
#include <vector>
struct node{
    int data;
    node* next;
};


node* reverse_linklist(node* cur){
    // 单链表倒转的三指针方法
    // cur 中间指针 prev 前指针 next 尾指针
    node* prev = nullptr;
    while(cur != nullptr){
        node* next = cur -> next; // 尾指针承载中间后继，用于下一步后移中间指针
        cur -> next = prev; // 将中间指针的下一指针指向前序
        // 前中指针后移
        prev = cur;
        cur = next;
    }
    return prev;
}

void solve(node* L){
    if (L == nullptr || L->next == nullptr ||L->next->next == nullptr) {
        return;
    }

    node* head = L;
    node* prev = L -> next;
    node* fast = L -> next;
    node* slow = L -> next;
    // 移动快慢指针
    while (fast -> next != nullptr && fast->next->next != nullptr){
        fast = fast -> next -> next;
        slow = slow -> next;
    }
    // 倒转后半链表
    node* second = slow -> next;
    slow->next = nullptr;
    second = reverse_linklist(second);

    // 交叉合并两个链表
    node* first = L->next;
    while (second != nullptr) {
        node* first_next = first->next;
        node* second_next = second->next;

        first->next = second;
        second->next = first_next;

        first = first_next;
        second = second_next;
    }
}


int main(){
    std::vector<int> L = {1,2,3,4};
    node* head = new node{0,nullptr};
    node* tail = head;

    for (int value : L) {
        node* new_node = new node{value, nullptr};
        if (head == nullptr) {
            head = new_node;
            tail = new_node;
        }
        else {
            tail->next = new_node;
            tail = new_node;
        }
    }

    // node* rnode = reverse_linklist(head);
    // for (int i = 0; i < L.size(); i++){
    //     std::cout << rnode -> data << std::endl;
    //     rnode = rnode -> next;
    // }
    solve(head);
    for (node* p = head->next; p != nullptr; p = p->next) {
        std::cout << p->data << std::endl;
    }
    return 0;
}



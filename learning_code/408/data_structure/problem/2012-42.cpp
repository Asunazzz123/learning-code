#include <iostream>
#include <stdexcept>
#include <vector>

struct node {
    char data;
    node* next;
};

node* CreateList(const std::vector<char>& str) {
    node* head = new node{'\0', nullptr};
    node* tail = head;

    for (char c : str) {
        tail->next = new node{c, nullptr};
        tail = tail->next;
    }

    return head;
}


node* sharingstr(node* str1, node* str2){
    node* pt1 = str1->next;
    node* pt2 = str2->next;

    while (pt1 != pt2){
        pt1 = pt1 ? pt1 -> next : str2 -> next;
        pt2 = pt2 ? pt2 -> next : str1 -> next;
    }

    return pt1;
}


// char SharingChar(node* str1, node* str2) {
//     std::vector<bool> exist(26, false);

//     for (node* p = str2->next; p != nullptr; p = p->next) {
//         exist[p->data - 'a'] = true;
//     }

//     for (node* p = str1->next; p != nullptr; p = p->next) {
//         if (exist[p->data - 'a']) {
//             return p->data;
//         }
//     }

//     throw std::runtime_error("No sharing char");
// }

void DestroyList(node* head) {
    while (head != nullptr) {
        node* next = head->next;
        delete head;
        head = next;
    }
}

int main() {
    std::vector<char> str1 = {'l', 'o', 'a', 'd', 'i','n','g'};
    std::vector<char> str2 = {'b', 'e'};

    node* linklist1 = CreateList(str1);
    node* linklist2 = CreateList(str2);

    
    node* suffix = linklist1->next;
    for (int j = 0; j < 4; j++) suffix = suffix->next;
    node* tail2 = linklist2;
    while (tail2->next != nullptr) tail2 = tail2->next;
    tail2->next = suffix;


    try{
        node* elem = sharingstr(linklist1,linklist2);
        if (elem == nullptr) throw std::runtime_error("No sharing node");
        std::cout << elem->data << '\n' << std::endl;
    } catch (const std::runtime_error& error){
        std::cout << error.what() << '\n' << std::endl;
    }

    // try {
    //     char elem = SharingChar(linklist1, linklist2);
    //     std::cout << elem << '\n';
    // } catch (const std::runtime_error& error) {
    //     std::cout << error.what() << '\n';
    // }

    tail2->next = nullptr;
    DestroyList(linklist1);
    DestroyList(linklist2);

    return 0;
}

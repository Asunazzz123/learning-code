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

char SharingChar(node* str1, node* str2) {
    std::vector<bool> exist(26, false);

    for (node* p = str2->next; p != nullptr; p = p->next) {
        exist[p->data - 'a'] = true;
    }

    for (node* p = str1->next; p != nullptr; p = p->next) {
        if (exist[p->data - 'a']) {
            return p->data;
        }
    }

    throw std::runtime_error("No sharing char");
}

void DestroyList(node* head) {
    while (head != nullptr) {
        node* next = head->next;
        delete head;
        head = next;
    }
}

int main() {
    std::vector<char> str1 = {'h', 'e', 'l', 'l', 'o'};
    std::vector<char> str2 = {'w', 'o', 'r', 'l', 'd'};

    node* linklist1 = CreateList(str1);
    node* linklist2 = CreateList(str2);

    try {
        char elem = SharingChar(linklist1, linklist2);
        std::cout << elem << '\n';
    } catch (const std::runtime_error& error) {
        std::cout << error.what() << '\n';
    }

    DestroyList(linklist1);
    DestroyList(linklist2);
    
    return 0;
}

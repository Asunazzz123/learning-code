#include<iostream>
#include<vector>

struct QueueNode{
    int data;
    QueueNode* next;
};


struct Queue{
    QueueNode* front;
    QueueNode* rear;
    int size;

    bool is_empty() const {
        if (front != nullptr){
            return true;
        }
        return false;
    }

    bool is_full() const {
        if (front == rear -> next){
            return true;
        }
        return false;
    }


    void push(int val){
        if (is_full()){
            size ++;

        }
        QueueNode* node = new QueueNode{val,nullptr};
        if (is_empty()){
            front = node;
            rear = node;
        }
        else{
            rear -> next = node;
            rear = node;
        }
    }

    bool pop(int& val){
        if (is_empty()){
            return false;
        }

        QueueNode* node = front;
        val = node -> data;
        front = front -> next;  
        if(front == nullptr){
            rear = nullptr;
        }

        delete node;
        return true;
    }
};






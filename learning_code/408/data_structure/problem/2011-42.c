#include<stdio.h>
#include <stdbool.h>

#define STACK_CAPACITY 100

typedef struct {
    int data[STACK_CAPACITY];
    int top;
} Stack;

bool push(Stack *stack, int val){
    // Stack Full
    if (stack-> top >= STACK_CAPACITY){
        return false;   
    }
    for (int i = stack->top; i>0; i--){
        stack->data[i] = stack-> data[i-1];
    }
    stack->data[0] = val;
    stack->top ++;
    return true;
}

bool pop(Stack *stack,int *val){
    // Stack empty
    if (stack->top == 0){
        return false;
    }
    *val = stack->data[0];
    for (int i = 1; i< stack->top; i++){
        stack->data[i-1] = stack->data[i];
    }
    stack->top -- ;
    return true;
}

bool init(Stack stack){
    //
}

int ascending_median(Stack *a,Stack *b,int n){
    int val = 0;
    for (int idx = 0; idx < n; idx++){
        if (a->top == 0){
            pop(b, &val);
        }
        else if (b->top == 0){
            pop(a, &val);
        }
        else if (a->data[0] <= b->data[0]){
            pop(a, &val);
        }
        else{
            pop(b, &val);
        }
    }
    return val;
    
}

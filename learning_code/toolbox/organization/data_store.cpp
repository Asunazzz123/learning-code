#include<iostream>

struct A{
    int a;
    char b;
    short c;
};

struct B{
    char b;
    int a;
    short c;
};

int main(){
    std::cout << "Size of A" << ' '<< sizeof(A) << std::endl;
    std::cout << "Size of B" << ' '<< sizeof(B) << std::endl;
    std::cout << "Size of A,b" << ' '<< sizeof(A::b) << std::endl;
    std::cout << "Size of B,b" << ' ' << sizeof(B::b) << std::endl;
    return 0;
}
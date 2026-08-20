#include<iostream>


int main(){
    bool key = true;
    bool* lock = new bool{false};
    std::cout << key << std::endl;
    std::cout << &key << std::endl;
    std::cout << lock << std::endl;
    std::cout << &lock << std::endl;
    std::cout << *lock << std::endl;
    delete lock;
    return 0;
}
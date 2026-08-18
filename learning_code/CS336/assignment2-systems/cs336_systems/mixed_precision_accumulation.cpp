#include<iostream>
#include<iomanip>
#include<vector>
template <typename T>

T gen(int num){
    T s = 0;
    for (int i = 0; i < num; i++){
        s += T(0.01);
    }
    return s;
}


int main(){
    int num = 1000;
    float g1 = gen<float>(num);
    double g2 = gen<double>(num);
    std::cout << "float result:" << std::fixed << std::setprecision(17) << g1 << std::endl;
    std::cout << "double result:" << std::fixed << std::setprecision(17) <<  g2 << std::endl;
}
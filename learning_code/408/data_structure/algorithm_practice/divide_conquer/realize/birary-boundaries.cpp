#include<iostream>
#include<vector>


int lowerbound(const std::vector<int> &A, int n,int x){
    int lower = 0;
    int upper = n;
    while (lower < upper){
        const int index = lower + (upper - lower) / 2;
        if (A[index] < x){
            lower = index + 1;
        } else {
            upper = index;
        }
    }
    return lower;
}


int main(){
    std::vector<int> v = {1,2,2,2,5};
    int x = 2;
    int res = lowerbound(v,v.size(),x);
    std::cout << res << '\n';
}



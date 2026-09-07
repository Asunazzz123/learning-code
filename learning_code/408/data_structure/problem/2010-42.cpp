#include<iostream>
#include<vector>

void vectorswap(std::vector<int> &L, int p){
    int n = L.size();
    for (int i = 0; i < n; i++){
        int tmp = L[(i+n)%p];
        L[(i+n)%p] = L[i];
        L[i] = tmp;
    }
}

int main(){
    std::vector<int> L = {1,2,3,4,5,6};
    int p = 3;
    vectorswap(L,p);
    for (int i = 0; i < L.size(); i++){
        std::cout << L[i] << std::endl;
    }
    return 0;
}




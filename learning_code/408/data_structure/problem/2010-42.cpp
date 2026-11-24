#include<iostream>
#include<vector>

/*


*/

void vectorinverse(std::vector<int> &L,std::size_t head,std::size_t prev){
    const std::size_t n = prev - head;
    for (std::size_t i = 0; i < n / 2; i++){
        std::size_t left = head + i;
        std::size_t right = prev - 1 - i;
        int tmp = L[left];
        L[left] = L[right];
        L[right] = tmp;
    }
}

void vectorswap_clockwise(std::vector<int> &L, int p){
    const std::size_t n = L.size();
    if (n == 0) return;

    const std::size_t k = static_cast<std::size_t>(p) % n;
    if (k == 0) return;

    vectorinverse(L, 0, n);
    vectorinverse(L, 0, k);
    vectorinverse(L, k, n);
}


int main(){
    std::vector<int> L = {1,2,3,4,5,6};
    int p = 3;
    vectorswap_clockwise(L,p);
    for (int i = 0; i < L.size(); i++){
        std::cout << L[i];
    }
    std::cout << '\n';
}




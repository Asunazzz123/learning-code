#include<cstdint>
#include<vector>
#include<iostream>

int partition(std::vector<int>&a, int left, int right){
    int pivot = a[right];
    int boundary = left;
    for (int i = left; i < right; ++i){
        if (a[i] < pivot){
            std::swap(a[i],a[boundary]);
            ++boundary;
        }
    }
    std::swap(a[boundary], a[right]);
    return boundary;
}

void quickSort(std::vector<int>& a, int left, int right) {
    if (left >= right) {
        return;
    }

    int pivotIndex = partition(a, left, right);
    quickSort(a, left, pivotIndex - 1);
    quickSort(a, pivotIndex + 1, right);
}

void split(std::vector<int>& a, std::vector<int>& S1, std::vector<int>& S2){
    int n = a.size();
    for (int i = 0; i < n /2; i++){
        S1.push_back(a[i]);
    }
    for (int i = n/2 ; i < n ; i++){
        S2.push_back(a[i]);
    }
}


int main(){
    std::vector<int> q = {1,4,2,7,5,8};
    std::vector<int> S1;
    std::vector<int> S2;
    quickSort(q,0,q.size()-1);
    split(q,S1,S2);
    std::cout << "S1" << std::endl;
    for (int x: S1){
        std::cout << x << std::endl;
    }
    std::cout << "S2" << std::endl;
    for (int y: S2){
        std::cout << y << std::endl;
    }
    return 0;
}





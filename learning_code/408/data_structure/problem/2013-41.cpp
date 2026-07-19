#include<iostream>
#include<vector>

int MajorElem(std::vector<int> a,int n){
    int l = a.size();
    std::vector<int> exists(n + 1, 0);
    for (int i = 0; i < l; i++){
        exists[a[i]] ++;
    }
    int max_elem = exists[0];
    int idx = 0;
    for (int j = 0; j < n ; j++){
        if (exists[j] >= max_elem){
            max_elem = exists[j];
            idx = j;
        }
    }
    if (max_elem > l/2){
        return idx;
    }
    return -1;
}

int main(){
    std::vector<int> test_list = {1, 2, 3, 4, 4, 4, 4};
    int majorelem = MajorElem(test_list, test_list.size());
    std::cout << majorelem << std::endl;
}

#include<iostream>
#include<vector>


void swap(std::vector<int>& a, int idx, int idy){
    int tmp = a[idx];
    a[idx] = a[idy];
    a[idy] = tmp;
}

void BubbleSort(std::vector<int>& a){
    int n = a.size();
    for (int i = 0; i < n ; i++){
        bool flag = false;
        for (int j = n-1; j > i; j -- ){
            if (a[j-1] > a[j]){
                swap(a,j-1,j);
                flag = true;
            }
        }
        if (flag == false){
            return ;
        }
    }
}


int main(){
    std::vector<int> a = {4,5,12,2,10,1,7,6};
    BubbleSort(a);
    for (int x: a){
        std::cout << x << std::endl;
    }
    return 0;

}

#include<iostream>
#include<vector>


int middle(std::vector<int> a , std::vector<int>b){
    
    int length = a.size();
    int ida = 0; int idb = 0;
    for (int i = 0; i < length -1 ; i++ ){
        if (a[ida] <= b[idb] ){
            ++ida;
        }
        else if (a[ida] > b[idb]){
            ++idb;          

        }
    }
    return (a[ida] <= b[idb])? a[ida] : b[idb];
}


int main(){
    std::vector<int> a = {1,2,3};
    std::vector<int> b = {4,5,6};
    int res = middle(a,b);
    std::cout << "Result:" << res << std::endl;
    return 0;
}

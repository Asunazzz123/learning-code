#include<iostream>
#include<vector>



int middle(const std::vector<int>& a ,const std::vector<int>& b){
    
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


int middle2(
    const std::vector<int>& a, 
    const std::vector<int>& b
){
    int pa = 0;
    int pb = 0;
    int n = a.size();
    while (n > 1){
        int ma = pa + (n+1)/2 - 1;
        int mb = pb + (n+1)/2 - 1;
        if (a[ma] == b[mb]){
            return a[ma];
        }  
        else if (a[ma] < b[ma]){
            pa += n/2;
        }
        else{
            pb += n/2;
        }
        n = (n+1)/2;
    }
    return std::min(a[pa],b[pb]);
}

int main(){
    std::vector<int> a = {1,2,3};
    std::vector<int> b = {4,5,6};
    int res = middle2(a,b);
    std::cout << "Result:" << res << std::endl;
    return 0;
}

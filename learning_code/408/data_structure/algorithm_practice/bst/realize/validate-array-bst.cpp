#include <iostream>
#include <vector>


bool isBST(const std::vector<int>& T, int n){
    int l = T.size();
    if (2*n < l){
        if(T[n] <= T[2*n+1] || T[n] >= T[2*n+2]){
            return false;
        }
        else{
            return isBST(T,2*n+1)&&isBST(T,2*n+2);
        }
    }
    return true;
}


bool isBST_2(const std::vector<int>& T, int n,
             int low, int high) {
    if (n >= T.size() || T[n] == -1)
        return true; 

    if (T[n] <= low || T[n] >= high)
        return false;

    return isBST_2(T, 2*n+1, low, T[n])
        && isBST_2(T, 2*n+2, T[n], high);
}



bool solve(const std::vector<int>& T){
    return isBST_2(T,0,0,std::numeric_limits<int>::max());
}


int main(){
    std::vector<int> T1 = {4,2,6,1,3,5,7};
    bool res = solve(T1);
    if (res)  std::cout << "True" << '\n';

}






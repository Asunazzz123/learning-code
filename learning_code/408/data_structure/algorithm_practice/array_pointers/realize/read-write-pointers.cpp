#include<iostream>
#include<vector>

int uniqueSorted(std::vector<int>& A, int n){

    int dist= 0;
    int len = 0;
    for (int prev = 0; prev < n; prev ++){
        int rear = prev + dist;
        while (A[prev] == A[rear]&& rear < n){
            ++rear;
        }
        A[prev+1] = A[rear];
        dist = rear - prev;
        if (rear == n){
            len = prev;
            break;
        }
    }
    return len + 1;
}

int main(){
    std::vector<int> A = {1,1,2,2,3};
    int res = uniqueSorted(A,A.size());
    std::cout << res << '\n';
}





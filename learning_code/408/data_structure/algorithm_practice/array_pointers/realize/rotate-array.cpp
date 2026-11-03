#include<iostream>
#include<vector>

// 辅助空间O(n)
void rotate(std::vector<int> &A, int n, int p){
    std::vector<int> res;
    for (int i = 0; i < n; i++){
        res[i] = A[(i-p)%n];
    }
    A = res;
}


// 辅助空间O(1)


void reverse(std::vector<int> &A,int left,int right){
    while(left < right){
        int tmp = A[left];
        A[left] = A[right];
        A[right] = tmp;
        ++left;
        --right;
    }
}



void rotate_left(std::vector<int> &A, int n, int p){
    if (p >= n) p = p%n;

    reverse(A,0,n-1);
    reverse(A,0,p-1);
    reverse(A,p,n-1);
}


void rotate_right(std::vector<int> &A, int n, int p){
    if (p >= n) p = p%n;
    rotate_left(A,n,n-p);
}


int main(){
    std::vector<int> a = {1,2,3,4,5};
    rotate_left(a,a.size(),2);
    for (int x:a){
        std::cout << x;
    }
    std::cout << '\n';
}











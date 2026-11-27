#include<iostream>
#include<vector>

// 时间复杂度O(n) 空间复杂度O(1)
int lowerMedian(
    const std::vector<int> &A,
    const std::vector<int> &B,
    int n
){
    std::size_t ptr1 = 0;
    std::size_t ptr2 = 0;
    std::size_t all = 0;
    int min = -1;
    while (all < n){
        if (A[ptr1]<B[ptr2]){
            min = A[ptr1];
            ptr1++;
            all++;
        }
        if (B[ptr2]<A[ptr1]){
            min = B[ptr2];
            ptr2++;
            all++;
        }
        if (A[ptr1] == B[ptr2] && n-all >= 2){
            min = A[ptr1];
            ptr1++;
            ptr2++;
            all += 2;
        }
        if (A[ptr1] == B[ptr2] && n-all <=1){
            return A[ptr1];
        }

    }
    return min;
}

// 时间复杂度O(log n) 空间复杂度O(1)
int lowerMedian_v2(
    const std::vector<int> &A,
    const std::vector<int> &B,
    int n
){
    int left = 0;
    int right = n;
    while (left < right) {
        int ptr1 = left + (right - left) / 2;
        int ptr2 = n - ptr1;
        if (B[ptr2 - 1] > A[ptr1]) {
            left = ptr1 + 1;
        } else {
            right = ptr1;
        }
    }

    int ptr1 = left;
    int ptr2 = n - ptr1;
    if (ptr1 == 0) {
        return B[ptr2 - 1];
    }
    if (ptr2 == 0) {
        return A[ptr1 - 1];
    }
    return A[ptr1 - 1] >= B[ptr2 - 1] ? A[ptr1 - 1] : B[ptr2 - 1];
}



int main(){
    std::vector<int> A = {1,2,3,4};
    std::vector<int> B = {2,3,4,5};
    // int res = lowerMedian(A,B,3);
    int res = lowerMedian_v2(A,B,3);
    std::cout << res << '\n';
}

#include<iostream>
#include<vector>



int min_3(int a,int b,int c){
    int min_2 = a <= b ? a : b;
    return min_2 <= c ? min_2 : c;
}

int max_3(int a,int b,int c){
    int max_2 = a>=b ? a : b;
    return max_2 >= c ? max_2 : c;
}


int minTripleDistance(
    const std::vector<int> &A, int na,
    const std::vector<int> &B, int nb,
    const std::vector<int> &C, int nc
){
    int i = 0;
    int j = 0;
    int k = 0;
    int best = max_3(A[i],B[j],C[k]) - min_3(A[i],B[j],C[k]);
    while (i < na && j < nb && k < nc){
        int low = min_3(A[i],B[j],C[k]);
        int high = max_3(A[i],B[j],C[k]);
        int dist = high - low;
        if (dist < best) best = dist;
        if (best == 0) return 0;
        if (A[i] == low){
            ++i;
        }
        else if (B[j] == low){
            ++j;
        }
        else{
            ++k;
        }
    }
    return best;
}


int main(){
    std::vector<int> A = {1,2,3};
    std::vector<int> B = {3,4,5};
    std::vector<int> C = {6,7,8};
    int res = minTripleDistance(A,3,B,3,C,3);
    std::cout << res << '\n';
}
#include<iostream>
#include<vector>

void InsertSort(std::vector<int>& L, int n) {
    for (int i = 1; i < n; ++i) {
        int key = L[i];
        int j = i - 1;

        while (j >= 0 && L[j] > key) {
            L[j + 1] = L[j];
            --j;
        }
        L[j + 1] = key;
    }
}



#include<iostream>
#include<vector>

void InsertSort_vector(std::vector<int>* a, int n) {
    for (int i = 2; i <= n; ++i) {
        if ((*a)[i] < (*a)[i - 1]) {
            (*a)[0] = (*a)[i];
            int j;
            for (j = i - 1; (*a)[0] < (*a)[j]; --j) {
                (*a)[j + 1] = (*a)[j];
            }
            (*a)[j + 1] = (*a)[0];
        }
    }
}




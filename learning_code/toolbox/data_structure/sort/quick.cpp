#include<iostream>
#include<vector>



int partition(std::vector<int>& a, int left, int right) {
    int pivotIndex = left + std::rand() % (right - left + 1);
    std::swap(a[pivotIndex], a[right]);

    int pivot = a[right];
    int boundary = left;

    for (int i = left; i < right; ++i) {
        if (a[i] < pivot) {
            std::swap(a[i], a[boundary]);
            ++boundary;
        }
    }

    std::swap(a[boundary], a[right]);
    return boundary;
}

void quickSort(std::vector<int>& a, int left, int right) {
    if (left >= right) {
        return;
    }

    int pivotIndex = partition(a, left, right);
    quickSort(a, left, pivotIndex - 1);
    quickSort(a, pivotIndex + 1, right);
}
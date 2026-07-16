#include <stdio.h>



void move_left(int a[], int n, int p)
{
    if (p <= 0 || p >= n) {
        return;
    }
    int b[p];
    for (int i = 0; i < p; i++) {
        b[i] = a[i];
    }
    for (int i = p; i < n; i++) {
        a[i - p] = a[i];
    }
    for (int i = 0; i < p; i++) {
        a[n - p + i] = b[i];
    }
}

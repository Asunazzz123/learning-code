#include <metal_stdlib>
#include <metal_array>

using namespace metal;
constant uint n = 2;

struct Shape{
    uint M, N, K;
};



void vecMultiplication(
    thread const array<int, n>& A,
    thread const array<int, n>& B,
    thread int& C
) {
    for (uint i = 0; i < n; ++i) {
        C += A[i] * B[i];
    }
}

void matrixMultiplication(
    thread const array<array<int, n>, n>& A,
    thread const array<array<int, n>, n>& B,
    thread array<array<int, n>, n>& C
) {
    for (uint j = 0; j < n; ++j) {
        array<int, n> column;
        for (uint k = 0; k < n; ++k) {
            column[k] = B[k][j];
        }
        for (uint i = 0; i < n; ++i) {
            C[i][j] = 0;
            vecMultiplication(A[i], column, C[i][j]);
        }
    }
}



kernel void dot2(device int* out [[buffer(0)]]) {
    metal::array<int, n> A = {1, 2};
    metal::array<int, n> B = {1, 2};
    int C = 0;
    vecMultiplication(A, B, C);
    out[0] = C;
}





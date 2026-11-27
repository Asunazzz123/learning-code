#include <metal_stdlib>
#include <metal_array>

constant uint n = 2;

void multiplication(thread const metal::array<int, n>& A,
                    thread const metal::array<int, n>& B,
                    thread int& C) {
    for (uint i = 0; i < A.size(); ++i) {
        C += A[i] * B[i];
    }
}

kernel void dot2(device int* out [[buffer(0)]]) {
    metal::array<int, n> A = {1, 2};
    metal::array<int, n> B = {1, 2};
    int C = 0;
    multiplication(A, B, C);
    out[0] = C;
}

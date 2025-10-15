#include <stdio.h>
#include <immintrin.h>  // For AVX intrinsics

#define SIZE 8  // number of elements

int main() {
    float a[SIZE] __attribute__((aligned(32))) = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0};
    float b[SIZE] __attribute__((aligned(32))) = {8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0};
    float result[SIZE] __attribute__((aligned(32)));

    // Load vectors from memory into AVX registers
    __m256 vecA = _mm256_load_ps(a);
    __m256 vecB = _mm256_load_ps(b);

    // Perform vector addition using AVX
    __m256 vecResult = _mm256_add_ps(vecA, vecB);

    // Store result back to memory
    _mm256_store_ps(result, vecResult);

    // Print results
    for (int i = 0; i < SIZE; i++) {
        printf("%.1f ", result[i]);
    }
    printf("\n");

    return 0;
}
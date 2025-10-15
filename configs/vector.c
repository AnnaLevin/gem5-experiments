#include <stdio.h>
#include <stdlib.h>

int main() {
    int N = 1000000;
    float *A = malloc(N * sizeof(float));
    float *B = malloc(N * sizeof(float));
    float *C = malloc(N * sizeof(float));

    for (int i = 0; i < N; i++) {
        A[i] = i * 0.1;
        B[i] = i * 0.2;
    }

    for (int i = 0; i < N; i++) {
        C[i] = A[i] + B[i];
    }

    printf("C[0]=%f, C[N-1]=%f\n", C[0], C[N-1]);
    free(A); free(B); free(C);
    return 0;
}
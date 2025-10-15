#include <stdio.h>
#define SIZE 1000000

int main() {
    float a[SIZE], b[SIZE], c[SIZE];
    for (int i = 0; i < SIZE; i++) {
        a[i] = i * 0.5f;
        b[i] = i * 0.25f;
    }

    for (int i = 0; i < SIZE; i++) {
        c[i] = a[i] + b[i];
    }

    printf("Done scalar\n");
    return 0;
}
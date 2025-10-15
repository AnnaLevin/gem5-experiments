#include <iostream>
#include <vector>
#include <omp.h>

int main() {
    const int N = 1000000;
    std::vector<double> a(N, 1.0), b(N, 2.0), c(N, 0.0);

    // Parallelize the loop using OpenMP
    #pragma omp parallel for
    for (int i = 0; i < N; i++) {
        c[i] = a[i] + b[i];
    }

    std::cout << "c[0] = " << c[0] << ", c[N-1] = " << c[N-1] << std::endl;
    return 0;
}

#include <stdio.h>
#include "gen_out.h"

int main() {
    int a = 11, b = 22;
    f gen1(a, b);
    f gen2(b, a);
    int m, n;
    while (gen1.next(m) && gen2.next(n)) {
        printf("gen1 next number is: %d\n", m);
        printf("gen2 next number is: %d\n", n);
    }
    return 0;
}

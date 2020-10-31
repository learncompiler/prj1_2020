#include <stdio.h>
#include "gen_out.h"

int main() {
    int a = 11, b = 22;
    f gen(a, b);
    int n;
    while (gen.next(n)) {
        printf("next number is: %d\n", n);
    }
    return 0;
}

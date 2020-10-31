#include <stdio.h>
#include "gen_out.h"

int main(int argc, char* argv[]) {
    f gen;
    int n;
    while (gen.next(n)) {
        printf("next number is: %d\n", n);
    }
    return 0;
}

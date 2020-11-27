#include <stdio.h>
#include "gen_out.h"

int main() {
    Future<f1, int> fu((f1()));
    int a;
    while (fu.poll(a)) {
        printf("fu poll number is: %d\n", a);
    }
    return 0;
}

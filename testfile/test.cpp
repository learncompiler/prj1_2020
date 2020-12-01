#include <stdio.h>
#include "gen_out.h"

int main() {
    f1 tmp;
    Future<int> fu(&tmp);
    int a;
    while (fu.poll(a)) {
        printf("fu poll number is: %d\n", a);
    }
    return 0;
}

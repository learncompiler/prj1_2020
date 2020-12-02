#include <stdio.h>
#include "gen_out.h"

int main() {
    learn_and_sing tmp1;
    Future<int> fu1(&tmp1);
    dance tmp2;
    Future<int> fu2(&tmp2);

    Executor<int> exec;
    exec.spawn(fu1);
    exec.spawn(fu2);
    exec.run();
    return 0;
}

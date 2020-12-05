#include <stdio.h>
#include <ctime>
#include <iostream>
#include "add_out.h"

int a = 0;
const int num = 234;
add tmp1[num];
Future<int> fu1[num];
Executor<int> exec;

int main() {
    for (int i = 0; i < num; ++i) {
        tmp1[i].init(&a, i);
    }

    for (int i = 0; i < num; ++i) {
        fu1[i].init(tmp1 + i);
    }

    for (int i = 0; i < num; ++i) {
        exec.spawn(fu1[i]);
    }
    clock_t startTime, endTime;
    startTime = clock();  //计时开始
    exec.run(false);
    endTime = clock();  //计时结束
    printf("ret: %d\n", a);
    cout << "async: run time is "
         << (double)(endTime - startTime) / CLOCKS_PER_SEC << "s" << endl;
    return 0;
}

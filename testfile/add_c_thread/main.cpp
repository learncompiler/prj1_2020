#include <stdio.h>
#include <ctime>
#include <iostream>
#include <mutex>
#include <thread>
using namespace std;

int a = 0;
const int num = 234;
thread threads[num];
mutex m;

int add_1(int* a) {
    m.lock();
    *a = *a + 1;
    m.unlock();
    return 0;
}

int add(int* a, int num) {
    for (int i = 0; i < num; i = i + 1) {
        thread tmp(add_1, a);
        tmp.join();
    }
    return 0;
}

int main() {
    clock_t startTime, endTime;
    startTime = clock();  //计时开始
    for (int i = 0; i < num; ++i) {
        threads[i] = thread(add, &a, i);
    }
    for (int i = 0; i < num; ++i)
        threads[i].join();
    endTime = clock();  //计时结束
    printf("ret: %d\n", a);
    cout << "run time is "
         << (double)(endTime - startTime) / CLOCKS_PER_SEC * 1000 << "ms"
         << endl;
    return 0;
}

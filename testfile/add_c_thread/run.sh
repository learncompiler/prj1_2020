g++ main.cpp -o main.out -std=c++11 -lpthread
taskset -c 0 ./main.out

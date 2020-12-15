# prj1_2020

在 c++ 中实现 async/await 语法。

## 运行方式 && 语法格式

`cd example && ./run.sh [dir_name]`

## 已完成

1. cpp 中的 generator。
2. 支持 generator 内部定义变量、传递参数。
3. 实现简单的 future ，支持 async 语法。
4. 实现 executor ，进一步完善 future（poll 中的参数增加 waker）。
5. 增加的 example 和 testfile ，可以对比 async 和 thread、cpp 和 rust 的性能。

## TODO

1. cpp generator 内存优化。
2. 补 log 。

## Log

### 2020-11-07

https://github.com/xy-plus/StudyDiary/blob/master/diary/2020-11-02.md

## Else

线程通信、协程通信，编译可知

内核作为一个进程

线程里单独放一个协程

高延时低延时

生产者消费者

同一个线程里的多个协程放到不同 cpu

spawn 线程

统一线程、协程

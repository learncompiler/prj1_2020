#ifndef __executor_h__
#define __executor_h__

#include "future.h"

template <class T>
class Task {
   private:
    Future<T> fu;
    bool sleep;

   public:
    Task(Future<T> fu_) : fu(fu_), sleep(false) {}
};

template <class T>
class Executor {
   private:
    Task<T> tasks[10];

    //    public:
    //     Task(Future<T1, T2> fu_) : fu(fu_), sleep(false) {}
};

#endif

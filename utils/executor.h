#ifndef __executor_h__
#define __executor_h__

#include <iostream>
#include <list>
#include "future.h"

using namespace std;

template <class T>
class Task {
   private:
    Future<T> fu;
    bool sleep;
    Task* other;

   public:
    Task(Future<T> fu_, Task* other_) : fu(fu_), sleep(false), other(other_) {}

    void wake_up() { sleep = false; }

    void set_sleep() { sleep = true; }

    bool is_sleep() { return sleep; }

    void wake_other() {
        if (other != nullptr) {
            other->wake_up();
        }
    }

    Poll poll(T& V) { return fu.poll(V); }
};

template <class T>
class Executor {
   private:
    list<Task<T>*> tasks;
    Task<T>* current_task;

   public:
    Executor() : current_task(nullptr) {}

    void spawn(Future<T> fu_) {
        fu_.reset();
        fu_.set_executor(this);
        if (current_task == nullptr) {
            // executor is initing, not runing
            // task don't need to wake other
            tasks.push_back(new Task<T>(fu_, nullptr));
        } else {
            // executor is runing
            // task need to wake other
            current_task->set_sleep();
            tasks.push_back(new Task<T>(fu_, current_task));
        }
    }

    void run(bool log) {
        while (tasks.size() > 0) {
            current_task = tasks.front();
            tasks.pop_front();
            if (current_task->is_sleep()) {
                tasks.push_back(current_task);
                continue;
            }
            T a;
            Poll ret = current_task->poll(a);
            if (ret != Poll::Ready) {
                if (ret == Poll::PendingAndSleep) {
                    current_task->set_sleep();
                }
                tasks.push_back(current_task);
            } else {
                if (log) {
                    cout << "future run to the end" << endl;
                    cout << "ret val is: " << a << endl;
                }
                current_task->wake_other();
                delete current_task;
            }
        }
    }
};

template <class T>
void block_on(Future<T> fu) {
    T ret;
    Poll state = Poll::PendingAndDontSleep;
    while (state != Poll::Ready) {
        state = fu.poll(ret);
    }
}

#endif

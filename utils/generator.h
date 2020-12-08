#ifndef __generator_h__
#define __generator_h__

#include <cstdio>

template <class T>
class Executor;

enum Poll { Ready, PendingAndSleep, PendingAndDontSleep };

template <class T>
class _generator {
   private:
    Executor<T>* executor;

   protected:
    int _line;

   public:
    _generator() : _line(0), executor(nullptr) {}

    virtual Poll next(T& V) = 0;

    Executor<T>* get_executor() { return executor; }

    void set_executor(Executor<T>* executor_) { executor = executor_; }

    void reset() { _line = 0; }
};

#define $generator(NAME, T) struct NAME : public _generator<T>

#define $emit(T)         \
   public:               \
    Poll next(T& _rv) {  \
        switch (_line) { \
            case 0:;

#define $stop           \
    }                   \
    _line = 0;          \
    return Poll::Ready; \
    }

#define $return(V)              \
    {                           \
        case __LINE__:          \
            _line = __LINE__;   \
            _rv = (V);          \
            return Poll::Ready; \
    }

#define $yield(V, sleep)                      \
    {                                         \
        _line = __LINE__;                     \
        _rv = (V);                            \
        if (sleep)                            \
            return Poll::PendingAndSleep;     \
        else                                  \
            return Poll::PendingAndDontSleep; \
        case __LINE__:;                       \
    }
#endif
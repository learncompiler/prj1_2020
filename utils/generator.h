#ifndef __generator_h__
#define __generator_h__

#include <cstdio>

template <class T>
class Executor;

template <class T>
class _generator {
   private:
    Executor<T>* executor;

   protected:
    int _line;

   public:
    _generator() : _line(0), executor(nullptr) {}

    virtual bool next(T& V) = 0;

    Executor<T>* get_executor() { return executor; }

    void set_executor(Executor<T>* executor_) { executor = executor_; }
};

#define $generator(NAME, T) struct NAME : public _generator<T>

#define $emit(T)         \
   public:               \
    bool next(T& _rv) {  \
        switch (_line) { \
            case 0:;

#define $stop     \
    }             \
    _line = 0;    \
    return false; \
    }

#define $return(V)            \
    {                         \
        case __LINE__:        \
            _line = __LINE__; \
            _rv = (V);        \
            return false;     \
    }

#define $yield(V)         \
    {                     \
        _line = __LINE__; \
        _rv = (V);        \
        return true;      \
        case __LINE__:;   \
    }
#endif
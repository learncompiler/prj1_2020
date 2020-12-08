#ifndef __future_h__
#define __future_h__

#include "generator.h"

template <class T>
class Future {
   private:
    _generator<T>* gen;

   public:
    Poll poll(T& a) { return gen->next(a); }

    Future() {}

    Future(_generator<T>* gen_) : gen(gen_) {}

    void init(_generator<T>* gen_) { gen = gen_; }

    Executor<T>* get_executor() { return gen->get_executor(); }

    void set_executor(Executor<T>* executor) { gen->set_executor(executor); }

    void reset() { gen->reset(); }

    ~Future() {
        // don't delete gen
        // delete gen;
    }
};

#endif

#ifndef __future_h__
#define __future_h__

#include "generator.h"

template <class T>
class Future {
   private:
    _generator<T>* gen;

   public:
    bool poll(T& a) { return gen->next(a); }

    Future(_generator<T>* gen_) : gen(gen_) {}
    // ~Future() { delete gen; }
};

#endif

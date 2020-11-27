#ifndef __future_h__
#define __future_h__

#include "generator.h"

template <class T1, class T2>
class Future {
   private:
    T1 gen;

   public:
    bool poll(T2& a) { return gen.next(a); }

    T2 await() {
        int a;
        while (poll(a)) {
        }
        return a;
    }

    Future(T1 gen_) : gen(gen_) {}
};

#endif

#ifndef __generator_h__
#define __generator_h__

class _generator {
   protected:
    int _line;

   public:
    _generator() : _line(0) {}
};

#define $generator(NAME) struct NAME : public _generator

#define $emit(T)         \
    bool next(T& _rv) {  \
        switch (_line) { \
            case 0:;

#define $stop     \
    }             \
    _line = 0;    \
    return false; \
    }

#define $return \
    _line = 0;  \
    return false

#define $yield(V)         \
    {                     \
        _line = __LINE__; \
        _rv = (V);        \
        return true;      \
        case __LINE__:;   \
    }
#endif
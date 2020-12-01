#ifndef __generator_h__
#define __generator_h__

template <class T>
class _generator {
   protected:
    int _line;

   public:
    _generator() : _line(0) {}
    virtual bool next(T& V) = 0;
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

#define $return(V) \
    _line = 0;     \
    _rv = (V);     \
    return false

#define $yield(V)         \
    {                     \
        _line = __LINE__; \
        _rv = (V);        \
        return true;      \
        case __LINE__:;   \
    }
#endif
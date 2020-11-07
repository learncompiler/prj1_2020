generator int f(int m, int n) {
    int a = m;
    yield a;
    a = n;
    yield a;
    int b = a = m - a;
    yield b;
    for (int i = 0; i < 2; i = i + 1) {
        yield i;
        yield i;
    }
    return;
}

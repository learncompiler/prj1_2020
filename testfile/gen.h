generator int f(int m, int n) {
    int a = m;
    yield a;
    a = n;
    yield a;
    int b = m + a;
    yield b;
    return;
}

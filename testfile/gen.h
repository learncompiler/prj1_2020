generator int f() {
    int a = 1;
    yield a;
    a = 22;
    yield a;
    int b = 333;
    yield b;
    return;
}

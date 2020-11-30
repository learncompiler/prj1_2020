async int f2() {
    yield 233;
    yield 2333;
    return 123;
}

async int f1() {
    int b = 1;
    int a;
    a = await(f2());
    yield a;
    return 333;
}

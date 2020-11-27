async int f2() {
    yield 233;
    yield 2333;
}

async int f1() {
    int a = await(f2());
    yield a;
}

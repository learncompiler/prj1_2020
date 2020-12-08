async int add_1(int* a) {
    yield 1;
    yield 1;
    yield 1;
    yield 1;
    yield 1;
    yield 1;
    yield 1;
    *a = *a + 1;
    return 0;
}

async int add(int* a, int num) {
    int ret;
    for (int i = 0; i < num; i = i + 1) {
        ret = await(add_1(a));
    }
    return ret;
}

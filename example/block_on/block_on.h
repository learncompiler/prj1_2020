async int test2(int num) {
    for (int i = 0; i < num; i = i + 1) {
        yield i;
    }
    return 0;
}

async int test(int num) {
    int ret;
    for (int i = 0; i < num; i = i + 1) {
        ret = await(test2(num));
    }
    return ret;
}

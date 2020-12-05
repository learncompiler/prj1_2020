async int learn_song() {
    return 111;
}

async int sing_song(int song) {
    return (song + 1) * 2;
}

async int learn_and_sing() {
    int song;
    song = await(learn_song());
    int sing;
    sing = await(sing_song(1 + song));
    return sing + 1;
}

async int dance() {
    return 123;
}

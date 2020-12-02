async int learn_song() {
    return 111;
}

async int sing_song() {
    return 112;
}

async int learn_and_sing() {
    int song;
    song = await(learn_song());
    int sing;
    sing = await(sing_song());
    return sing + song;
}

async int dance() {
    return 113;
}

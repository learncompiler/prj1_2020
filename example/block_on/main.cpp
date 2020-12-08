#include <iostream>
#include "block_on_out.h"

int main() {
    test tmp(3);
    Future<int> fu(&tmp);
    block_on(fu);
}
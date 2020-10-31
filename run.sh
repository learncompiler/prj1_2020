python3 -m src testfile/gen.h testfile/gen_out.h
cd testfile
g++ test.cpp -o test.out
./test.out

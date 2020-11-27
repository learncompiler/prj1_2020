python3 -m src testfile/gen.h testfile/gen_out.h
cp utils/generator.h testfile/generator.h
cp utils/future.h testfile/future.h
cd testfile
g++ test.cpp -o test.out
./test.out

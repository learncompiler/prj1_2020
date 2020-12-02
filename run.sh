python3 -m src testfile/gen.h testfile/gen_out.h
cp utils/generator.h testfile/generator.h
cp utils/future.h testfile/future.h
cp utils/executor.h testfile/executor.h
cd testfile
g++ test.cpp -o test.out -std=c++11
./test.out

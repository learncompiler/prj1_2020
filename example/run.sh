dir=$1

cd ..
python3 -m src example/$dir/$dir.h example/$dir/${dir}_out.h
cd example
cp ../utils/generator.h $dir/generator.h
cp ../utils/future.h $dir/future.h
cp ../utils/executor.h $dir/executor.h
g++ $dir/main.cpp -o $dir/main.out -std=c++11
taskset -c 0 ./$dir/main.out

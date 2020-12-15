# Async in C++

> 2017011313 刘丰源

## 背景介绍

Rust 已经开始支持语言级别的异步协程，C++ 语言则不支持。

- [Rust 异步入门](https://github.com/xy-plus/StudyDiary/blob/master/diary/2020-10-16/SUMMARY.md)

上面链接包含了入门 Rust 异步所需要知道的最基础的知识，如果不具备这些知识，可能会导致后续阅读困难。

Rust 异步最关键的 crate 是 Future 。尽管在 C++ 中也有类似的头文件和协程支持，但是无论是功能还是性能，都远不如 Rust 。

本项目基于 minidecaf(简化的 C 语言) ，在 C++ 中增加了迭代器（generator）、异步（async、await）语法，并实现了 Future 和 Executor 作为运行时。

## Rust 异步分析

异步本质上是一个语法糖，如果 Rust 语言官方不支持 async、await 语法，我们仍然可以通过 Rust 写出异步程序，但是实现过程会更加复杂、可读性也不高。

### await

await 是 Rust 异步的核心语法之一，举例如下：

```Rust
async fn learn_song() -> Song { ... }
async fn sing_song(song: Song) { ... }
async fn dance() { ... }

async fn learn_and_sing() {
    // 在唱歌之前等待学歌完成
    // 这里我们使用 `.await` 而不是 `block_on` 来防止阻塞线程，这样就可以同时执行 `dance` 了。
    let song = learn_song().await;
    sing_song(song).await;
}
 async fn async_main() {
    let f1 = learn_and_sing();
    let f2 = dance();
     // `join!` 类似于 `.await` ，但是可以等待多个 future 并发完成
     // 如果学歌的时候有了短暂的阻塞，跳舞将会接管当前的线程，如果跳舞变成了阻塞
     // 学歌将会返回来接管线程。如果两个futures都是阻塞的，
     // 这个‘async_main'函数就会变成阻塞状态，并生成一个执行器
    futures::join!(f1, f2)
}
 fn main() {
    block_on(async_main());
}
```

await 在 async function 中使用，作用为：等待指定的异步函数执行完成。

那么这和直接调用常规的同步函数的区别是什么？

如果直接调用同步函数，那么就会直接跳转执行，**执行结束** 后才会回到上一层函数（调用者）。然而异步函数不一样，如果遇到资源不足等问题（比如在等待网络、IO 等），会返回 `Poll::Pending` 给调用者。然而，之前的异步函数并没有执行完，却提前返回了。这么做的目的是为了能把自己占用的 CPU 资源先让给别人，而自己开始等待所需资源。

那么 await 是如何等待异步函数执行完毕的呢？`expr.await` 也是一个语法糖，其展开如下（简化后的伪代码）（TODO：源代码链接）：

```Rust
{
    let future = expr;
    loop {
        ret = future.poll()
        match ret {
            Polll::Read<T> => { break; }
            Poll::Pending => { yield; }
        }

    }
    ret.unwrap();
}
```

### yield

前面我们遇到了一个新的语法：yield。yield 的作用是主动暂时让出 CPU 资源。但是其本质和 return 是一样的，协程在主动 yield 的时候，会 return Poll::Pending 。区别在于，Future(async function) 通过 yield 返回时，会保存当前的执行状态，下次再进入该 Future 时，会从上次保存的状态继续执行；而常规的函数则会清空调用栈，下次执行还是从头开始执行。

如果在 generator 中进行 yield 则会保存当前 generator 的状态并返回。那么在 async function 中展开 await ，也有 yield 。那为什么在 async function 中也可以用 yield 呢？首先，async funtion 的返回值是 Future 。执行 future.await 才能得到 async funtion 的执行结果。在 Rust 中，async function 和 generator 本质上是一样的，[有函数](https://doc.rust-lang.org/src/core/future/mod.rs.html#61) 可以将 generator 转换成 Future 。

generator 怎么使用呢？一般来说，得代码不断执行 `gen.next()` 。同理，Future 也得有代码执行，这部分代码我们称为 executor（调度器）（后续介绍）。

注意，编写程序的程序员并不能在 async function 中直接使用 yield ，但是 tokio、async_std 提供了 `yield_now()` 函数，效果和 yield 相同，并且会将该协程放到 executor 的就绪队列队尾，等待下一次执行。

[tokio 中 yield_now 的实现](https://docs.rs/tokio/0.3.5/src/tokio/task/yield_now.rs.html#16-37) 如下：

```Rust
cfg_rt! {
    pub async fn yield_now() {
        struct YieldNow {
            yielded: bool,
        }

        impl Future for YieldNow {
            type Output = ();

            fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
                if self.yielded {
                    return Poll::Ready(());
                }

                self.yielded = true;
                cx.waker().wake_by_ref();
                Poll::Pending
            }
        }

        YieldNow { yielded: false }.await
    }
}
```

### executor

前面已经提到过，executor 的功能是用来执行协程。我们先来介绍最简单的 executor：block_on（tokio、async_std 里都有），举例如下：

```Rust
async fn B() { ... }

async fn A() {
    B().await;
}


fn main() {
    block_on(A());
}
```

执行过程为，反复 poll 顶层 Future A ，A 中的 await 会不断 poll B ，直到执行完。

我们来看一个稍微复杂一点的例子：

树形结构

```Rust
async fn D() { ... }

async fn C() { ... }

async fn B() {
    C().await;
    D().await;
}

async fn A() {
    B().await;
    D().await;
}


fn main() {
    block_on(A());
}
```

上面所有的 async funtion 都会被实例化为 Future ，而这些 Future 的关系可以化成一棵树，每有一个 await ，就创建一个子结点：

```
    A
   / \
  B   D2
 / \
C   D1
```

executor 从顶层结点 A 开始执行，逐渐执行完全部的子结点。

上面的例子会像同步函数一样，一口气执行到底。那 await 里的 yield 不是会主动让出计算资源吗，让给谁呢？

如果只有 block_on ，那确实还不如同步函数。但是顶层 Future 可能不止有一个比如 `join!`（tokio、async_std 里都有）（用法举例：`join!(A(), D())`），可以让 executor 拥有两个顶层 Future（通过别的方法可以拥有多个顶层 Future）。如果一个下层 Future C 对上层 Future B 返回了 Pending ，则 Future B 会向它的上层 Future A 也返回 Pending 。如果顶层 Future A 向 executor 返回 Pending ，则会开始执行其它顶层 Future D3 。

由于 executor 可以由我们（用户）自行编写，所以当 executor 收到 Pending 时的行为可以自行定义。目前 tokio 和 async_std 的做法都是将该 Future 移动到队尾。但是如果是自行实现的话，其实可以将该 Future 移出就绪队列，放到休眠队列中。知道该 Future 等待的资源就绪时，再将该 Future 唤醒。基于这一点，就可以理解为什么 `future.poll(self.waker)` 需要传入自己的 waker 了，就是为了能够让自己等待的 future 能够在就绪后唤醒自己。

## 实现过程

> 为了阅读的流畅性，接下来所有展示的代码可能被部分“阉割”

一个完整的编译器需要将 C++ 代码转换成汇编代码。但是，我最终选择的做法是：自定义一些 C++ 关键词，然后识别这部分关键词，然后生成标准的 C++ 代码。这样看起来十分投机取巧，但是我是经过仔细的思考后才决定的。原因有以下几点：

1. async/await 本质上是语法糖，不需要语言级别的支持也能实现，只不过比较复杂，那么纯 C++ 理论上也能实现协程，并不需要 从汇编层面来进行支持。
2. 这种事情有人干过。在 [Mnemosyne](https://github.com/xy-plus/StudyDiary/blob/master/diary/2020-12-03.md#持久内存事务) 中，他们为了让 C++ 更简单的支持 NVM ，简化事务性代码的编写方式，增加了 `atomic` 关键词。具体做法就是通过自己的编译器，识别 `atomic` 关键词，将被关键词表示的变量的相关操作，转换成事务性代码。
3. C/C++ 的功能性极强（代价是安全性），随着更多高级语言（如：Rust、Go）的出现，C/C++ 已经逐渐被认为是一种“高级的 asm”。

我一开始也尝试过从汇编层面来实现异步，然而过程及其丑陋，而且实现异步状态保存的过程，和实现 switch 跳转的过程极其相似。所以我想到，也许可以直接通过 switch 来实现异步。

实现过程中的主要内容分为：generator、Future、async/await、executor 。

### generator

前面提到过，Future 可以由 generator 生成，且本质上是一致的，所以我先在 C++ 中实现语言级别的 generartor 。不过，在此之前，需要先通过标准 C++ 实现一个 generator 。我的做法如下：

```cpp
template <class T>
class _generator {
   protected:
    int _line;

   public:
    _generator() : _line(0) {}
    virtual int next(T& V) = 0;
    void reset() { _line = 0; }
};
```

定义一个 \_generator 抽象类，如果要实现 generator ，就需要继承 \_generator 并 为其实现 next 函数。next 内部为 generator 的逻辑，数据通过参数中的引用传递，返回值为 0 或 1，用于标示 generator 是否已经执行完毕。

通过宏可以更简单的实现自己的 generator：

```cpp
#define $generator(NAME, T) struct NAME : public _generator<T>

#define $emit(T)         \
   public:               \
    Poll next(T& _rv) {  \
        switch (_line) { \
            case 0:;

#define $stop     \
    }             \
    _line = 0;    \
    return 0; \
    }

#define $return(V)              \
    {                           \
        case __LINE__:          \
            _line = __LINE__;   \
            _rv = (V);          \
            return 0;           \
    }

#define $yield(V)           \
    {                       \
        _line = __LINE__;   \
        _rv = (V);          \
        return 1;           \
        case __LINE__:;     \
    }
#endif
```

直接看宏可能还不太能理解这么做的原理，我们来看一个例子，通过例子来理解：

```cpp
$generator(f) {
    int a = 1;
    $emit(int) {
        $yield(a);
        $yield(22);
        $yield(333);
        $return(0);
    }
    $stop
};

int main() {
    f gen;
    int n;
    while (gen.next(n)) {
        printf("next number is: %d\n", n);
    }
    printf("return number is: %d\n", n);
    return 0;
}
```

这里通过维护 `_line` 变量来判断 generator 的状态，但是通过宏的形式，使得编程人员不会感知到 switch 的存在，也不需要手动维护状态，或者进行状态转换。

但是，这样做有几个很严重的缺点：

1. 所有用到的变量都需要提前声明（就像久的 C 语言一样），十分不方便。
2. 不支持诸如 `for (int i = 0; i < 10; ++i) { $yield(0); }` 之类的操作。因为 i 是临时变量，yield 后会被析构，下一次进入 generator 时，只知道所处的状态，但是不知道状态内变量的值。
3. 传递参数较为麻烦。当然，可以手动为每个 generator 加上带参数的构造函数。

对于以上问题，解决方案为：通过自己实现的 parser 识别 async function ，通过代码自动生成相应的结构体，将其中所有定义的变量作为结构体的成员变量；如果函数需要参数，则同时为结构体自动生成相应的带参数的构造函数。

改进之后，定义 generator 的语法如下：

```cpp
generator int f(int m, int n) {
    int a = m;
    yield a;
    a = n;
    yield a;
    int b = a = m + a;
    yield b;
    for (int i = 0; i < 4; i = i + 1) {
        yield i;
        yield i;
    }
    return;
}
```

### Future && async/await

Future 就是简单对 generator 进行了一层包装：

```cpp
enum Poll { Ready, PendingAndSleep, PendingAndDontSleep };

template <class T>
class Future {
   private:
    _generator<T>* gen;

   public:
    Poll poll(T& a) { return gen->next(a); }

    Future(_generator<T>* gen_) : gen(gen_) {}

    void reset() { gen->reset(); }

    ~Future() { // don't delete gen }
};
```

> 注意到，这里 poll/next 的返回值已经变为了 enum Poll ，generator 的代码也有了一些相应的变化，感兴趣的话可以自行阅读源码。

除了对接口进行了封装，Future 和 generator 几乎没有不同。这部分核心的内容在于 await 语法。

我们先来看一个例子：

```cpp
async int f2() {
    yield 233;
    yield 2333;
    return 123;
}

async int f1() {
    int b = 1;
    int a;
    a = await(f2());
    yield a;
    return 333;
}
```

async 和 generator 关键词的识别方式是相似的，我们重点关注 await 。我将 await 定为关键词，`await(...)` 的内部必须是一个 async function call ，这个关键词的作用和 Rust 中 `.await` 的效果相同，就是等待一个 async function call 执行完毕。因此将其展开后，自动生成的 C++ 代码大致如下：

```cpp
// origin code
int a;
a = await(async_func_call());

// autogen code
int tmp;
Future fu;
while (fu.poll(tmp) != Poll::Ready) { yield tmp; }
a = tmp;
```

> 上述代码只是简化后的示例，真实生成的代码更为复杂。完整代码请自行运行 example 然后阅读生成的 `*_out.h` ，或直接阅读 `parser.py` 内的生成逻辑。

仔细看这个上面的 poll 函数，和 Rust 中的 poll 似乎有一些不一样。Rust 中的 poll 还需要传入一个 waker ，而这里没有 waker ，似乎也没什么问题。那么 waker 是用来做什么的呢？等写到 executor 的时候，就知道答案了。

### executor

executor 有一个队列，用于执行顶层 future 。由于有些 future 会 yield ，给 executor 返回 Pending ，那么在这个 future 等待（await）的另一个 future 执行结束之前，executor 都不会再调用这个 future 。我们通过定义一个 class Task ，其内容就是对 Future 进行了简单的包装，并增加了一个任务状态，可以由 executor 设置为 sleep ，同时也可以被别的 future 唤醒：

```cpp
template <class T>
class Task {
   private:
    Future<T> fu;
    bool sleep;
    Task* other;

   public:
    Task(Future<T> fu_, Task* other_) : fu(fu_), sleep(false), other(other_) {}
    void wake_up() { sleep = false; }
    void set_sleep() { sleep = true; }
    bool is_sleep() { return sleep; }
    void wake_other() { if (other != nullptr) other->wake_up(); }
    Poll poll(T& V) { return fu.poll(V); }
};
```

executor 做的事情就是不断从队列中取出队首（且不在休眠）的任务来执行，然后根据任务的执行结果进行不同的处理。

如果是程序员手动执行 yield ，效果和 yield_now() 是相同的，poll 的返回值为 `Poll::PendingAndDontSleep` ，会将任务放回队列尾部（否则没有别的协程唤醒这个任务，将永远休眠）。

如果是通过 await 执行的 yield ，那这个任务将返回 `Poll::PendingAndSleep` ，executor 将其设为休眠，在其等待的协程执行完毕将其唤醒之前，都不会再次执行。

```cpp
void run(bool log) {
    while (tasks.size() > 0) {
        current_task = tasks.front();
        tasks.pop_front();
        if (current_task->is_sleep()) {
            tasks.push_back(current_task);
            continue;
        }
        T a;
        Poll ret = current_task->poll(a);
        if (ret != Poll::Ready) {
            if (ret == Poll::PendingAndSleep) {
                current_task->set_sleep();
            }
            tasks.push_back(current_task);
        } else {
            if (log) {
                cout << "future run to the end" << endl;
                cout << "ret val is: " << a << endl;
            }
            current_task->wake_other();
            delete current_task;
        }
    }
}
```

## 性能改进

前面我们提到过，future 的调用过程可以画成一棵树，如果需要执行底层 future ，需要从顶层开始，一层一层向下调用，层数越多性能越差。

为了解决这个问题，我作出来如下改进，将 await 展开改为：

```diff

Future fu;
int tmp;
- while (fu.poll(tmp) != Poll::Ready) { yield tmp; }
+ this->get_executor()->spawn(fn)
+ yield 0;
+ fu.poll(tmp);
a = tmp;
```

> 上述代码只是简化后的示例，真实生成的代码更为复杂。完整代码请自行运行 example 然后阅读生成的 `*_out.h` ，或直接阅读 `parser.py` 内的生成逻辑。

yield 后该协程会被休眠，并且将 fu 作为顶层 future 加入（spawn）到 executor 内。fu 执行完后会唤醒该协程，此时通过 fu.poll 就可以获得 fu 的返回值。

将所有 future 都放在顶层可以避免前面提到的多次调用，从而提升性能。

## 性能测试

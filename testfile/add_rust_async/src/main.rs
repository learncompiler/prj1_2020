// use futures::executor::block_on;
use std::sync::{Arc, Mutex};
use stopwatch::Stopwatch;

async fn add_1(a: Arc<Mutex<i32>>) {
    tokio::task::yield_now().await;
    tokio::task::yield_now().await;
    tokio::task::yield_now().await;
    tokio::task::yield_now().await;
    tokio::task::yield_now().await;
    tokio::task::yield_now().await;
    tokio::task::yield_now().await;
    let mut a = a.lock().unwrap();
    *a += 1;
}

async fn add(a: Arc<Mutex<i32>>, b: i32) {
    for _i in 0..b {
        add_1(a.clone()).await;
    }
}

#[tokio::main(worker_threads = 1)]
async fn main() {
    let a = Arc::new(Mutex::new(0));
    const num: i32 = 234;
    let sw = Stopwatch::start_new();
    let mut handles = Vec::new();
    for i in 0..num {
        handles.push(tokio::spawn(add(a.clone(), i)));
    }
    for h in handles {
        h.await.unwrap();
    }
    println!("{:#?}", a);
    println!("It took {} ms", sw.elapsed_ms());
}

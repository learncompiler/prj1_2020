use async_std::{task, task::spawn};
use std::sync::{Arc, Mutex};
use stopwatch::Stopwatch;

async fn add_1(a: Arc<Mutex<i32>>) {
    task::yield_now().await;
    task::yield_now().await;
    task::yield_now().await;
    task::yield_now().await;
    task::yield_now().await;
    task::yield_now().await;
    task::yield_now().await;
    let mut a = a.lock().unwrap();
    *a += 1;
}

async fn add(a: Arc<Mutex<i32>>, b: i32) {
    for _i in 0..b {
        add_1(a.clone()).await;
    }
}

#[async_std::main]
async fn main() {
    let a = Arc::new(Mutex::new(0));
    const NUM: i32 = 234;
    let sw = Stopwatch::start_new();
    let mut handles = Vec::new();
    for i in 0..NUM {
        handles.push(spawn(add(a.clone(), i)));
    }
    for h in handles {
        h.await;
    }
    println!("{:#?}", a);
    println!("It took {} ms", sw.elapsed_ms());
}

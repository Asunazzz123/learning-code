#include <atomic>
#include <chrono>
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <string>
#include <thread>

using namespace std::chrono_literals;

class OneShotBarrier {
public:
    explicit OneShotBarrier(int total) : total_(total) {}

    void arrive_and_wait() {
        std::unique_lock<std::mutex> lock(mutex_);
        ++arrived_;

        if (arrived_ == total_) {
            cv_.notify_all();
            return;
        }

        cv_.wait(lock, [this] { return arrived_ == total_; });
    }

private:
    int total_;
    int arrived_ = 0;
    std::mutex mutex_;
    std::condition_variable cv_;
};

std::mutex output_mutex;

void log(const std::string& thread_name, const std::string& message) {
    std::lock_guard<std::mutex> lock(output_mutex);
    std::cout << thread_name << " | " << message << '\n';
}

void unsafe_increment_once(std::atomic<int>& x,
                           std::atomic<bool>& start,
                           OneShotBarrier& both_loaded,
                           const std::string& thread_name) {
    while (!start.load()) {
        std::this_thread::yield();
    }

    int simulated_register = x.load();
    log(thread_name, "load x into local register: r=" +
                         std::to_string(simulated_register));

    both_loaded.arrive_and_wait();

    ++simulated_register;
    std::this_thread::sleep_for(50ms);
    x.store(simulated_register);

    log(thread_name, "store local register back to x: x=" +
                         std::to_string(simulated_register));
}

void locked_increment_once(int& x,
                           std::atomic<bool>& start,
                           std::mutex& x_mutex,
                           const std::string& thread_name) {
    while (!start.load()) {
        std::this_thread::yield();
    }

    std::lock_guard<std::mutex> lock(x_mutex);

    int simulated_register = x;
    log(thread_name, "lock, load x into local register: r=" +
                         std::to_string(simulated_register));

    ++simulated_register;
    std::this_thread::sleep_for(50ms);
    x = simulated_register;

    log(thread_name, "store local register back to x, unlock: x=" +
                         std::to_string(x));
}

void run_unsafe_demo() {
    std::cout << "\n[1] Unsynchronized load-modify-store demo\n";
    std::cout << "Expected mathematical result: x = 2\n";

    std::atomic<int> x{0};
    std::atomic<bool> start{false};
    OneShotBarrier both_loaded(2);

    std::thread t1(unsafe_increment_once, std::ref(x), std::ref(start),
                   std::ref(both_loaded), "Thread-A");
    std::thread t2(unsafe_increment_once, std::ref(x), std::ref(start),
                   std::ref(both_loaded), "Thread-B");

    start.store(true);

    t1.join();
    t2.join();

    std::cout << "Final x = " << x.load()
              << " (lost update: two increments became one)\n";
}

void run_locked_demo() {
    std::cout << "\n[2] Mutex-protected load-modify-store demo\n";
    std::cout << "Expected mathematical result: x = 2\n";

    int x = 0;
    std::atomic<bool> start{false};
    std::mutex x_mutex;

    std::thread t1(locked_increment_once, std::ref(x), std::ref(start),
                   std::ref(x_mutex), "Thread-A");
    std::thread t2(locked_increment_once, std::ref(x), std::ref(start),
                   std::ref(x_mutex), "Thread-B");

    start.store(true);

    t1.join();
    t2.join();

    std::cout << "Final x = " << x << " (correct because the critical section is locked)\n";
}

int main() {
    std::cout << "Real std::thread demo for shared variable x\n";
    std::cout << "-------------------------------------------\n";

    run_unsafe_demo();
    run_locked_demo();

    return 0;
}

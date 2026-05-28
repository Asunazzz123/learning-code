#include <atomic>
#include <chrono>
#include <iostream>
#include <mutex>
#include <semaphore>
#include <string>
#include <thread>
#include <vector>

using namespace std::chrono_literals;

// 当前正在读共享数据的读者数量。
int reader_count = 0;

// 被读者读取、被写者修改的共享数据。
int shared_data = 0;

// P/V 信号量。
// reader_count_mutex 用来保护 reader_count。
// resource_mutex 用来保护共享数据：写者独占，第一个读者加锁，最后一个读者解锁。
std::binary_semaphore reader_count_mutex(1);
std::binary_semaphore resource_mutex(1);

// 只保护控制台输出，避免多线程打印互相穿插；它不参与读者-写者算法本身。
std::mutex output_mutex;

// demo 的运行期检查：用于发现读写冲突或多个写者同时写入。
std::atomic<int> active_readers{0};
std::atomic<int> active_writers{0};
std::atomic<int> error_count{0};

void log(const std::string& role, int id, const std::string& message) {
    std::lock_guard<std::mutex> lock(output_mutex);
    std::cout << role << id << " | " << message << '\n';
}

void writer(int writer_id, int rounds) {
    for (int round = 1; round <= rounds; ++round) {
        log("Writer", writer_id, "wants to write");

        resource_mutex.acquire();  // P(resource)：申请共享资源。

        const int writers_before = active_writers.fetch_add(1);
        if (writers_before != 0 || active_readers.load() != 0) {
            error_count.fetch_add(1);
            log("Writer", writer_id, "ERROR: write conflict detected");
        }

        const int before = shared_data;
        log("Writer", writer_id, "starts writing, round " + std::to_string(round));
        std::this_thread::sleep_for(120ms);
        shared_data = before + 1;
        log("Writer", writer_id, "updates shared_data: " + std::to_string(before) +
                                " -> " + std::to_string(shared_data));

        active_writers.fetch_sub(1);
        resource_mutex.release();  // V(resource)：释放共享资源。

        log("Writer", writer_id, "leaves");
        std::this_thread::sleep_for(80ms);
    }
}

void reader(int reader_id, int rounds) {
    for (int round = 1; round <= rounds; ++round) {
        log("Reader", reader_id, "wants to read");

        reader_count_mutex.acquire();  // P(mutex)：进入 reader_count 的临界区。
        ++reader_count;
        if (reader_count == 1) {
            resource_mutex.acquire();  // 第一个读者阻塞写者。
            log("Reader", reader_id, "is first reader, blocks writers");
        }
        reader_count_mutex.release();  // V(mutex)：离开 reader_count 的临界区。

        const int readers_now = active_readers.fetch_add(1) + 1;
        if (active_writers.load() != 0) {
            error_count.fetch_add(1);
            log("Reader", reader_id, "ERROR: read-write conflict detected");
        }

        log("Reader", reader_id, "reads shared_data=" + std::to_string(shared_data) +
                                ", active_readers=" + std::to_string(readers_now) +
                                ", round " + std::to_string(round));
        std::this_thread::sleep_for(60ms);

        active_readers.fetch_sub(1);

        reader_count_mutex.acquire();  // P(mutex)：进入 reader_count 的临界区。
        --reader_count;
        if (reader_count == 0) {
            resource_mutex.release();  // 最后一个读者释放资源，允许写者进入。
            log("Reader", reader_id, "is last reader, allows writers");
        }
        reader_count_mutex.release();  // V(mutex)：离开 reader_count 的临界区。

        log("Reader", reader_id, "leaves");
        std::this_thread::sleep_for(40ms);
    }
}

int main() {
    constexpr int reader_rounds = 4;
    constexpr int writer_rounds = 3;

    std::cout << "Reader-priority readers-writers demo\n";
    std::cout << "------------------------------------\n";

    std::vector<std::thread> threads;
    threads.emplace_back(writer, 0, writer_rounds);
    threads.emplace_back(reader, 0, reader_rounds);
    threads.emplace_back(reader, 1, reader_rounds);
    threads.emplace_back(reader, 2, reader_rounds);
    threads.emplace_back(writer, 1, writer_rounds);

    for (auto& thread : threads) {
        thread.join();
    }

    std::cout << "------------------------------------\n";
    std::cout << "Final shared_data = " << shared_data << '\n';
    std::cout << "Conflict errors = " << error_count.load() << '\n';

    return error_count.load() == 0 ? 0 : 1;
}

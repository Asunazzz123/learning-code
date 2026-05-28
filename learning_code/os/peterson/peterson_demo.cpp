#include <array>
#include <atomic>
#include <chrono>
#include <iostream>
#include <mutex>
#include <string>
#include <thread>

using namespace std::chrono_literals;

std::array<std::atomic<bool>, 2> flag = {false, false};
std::atomic<int> turn{0};

std::atomic<int> shared_counter{0};
std::atomic<int> active_in_critical{0};
std::mutex output_mutex;

void log(int process_id, const std::string& message) {
    std::lock_guard<std::mutex> lock(output_mutex);
    std::cout << "P" << process_id << " | " << message << '\n';
}

void peterson_lock(int process_id) {
    const int other = 1 - process_id;

    flag[process_id].store(true);
    turn.store(other);

    log(process_id, "wants to enter: flag[" + std::to_string(process_id) +
                        "]=true, turn=" + std::to_string(other));

    bool printed_wait_message = false;
    while (flag[other].load() && turn.load() == other) {
        if (!printed_wait_message) {
            log(process_id, "waits because flag[" + std::to_string(other) +
                                "]=true and turn=" + std::to_string(other));
            printed_wait_message = true;
        }
        std::this_thread::sleep_for(20ms);
    }

    if (printed_wait_message) {
        log(process_id, "can enter now");
    }
}

void peterson_unlock(int process_id) {
    flag[process_id].store(false);
    log(process_id, "leaves: flag[" + std::to_string(process_id) + "]=false");
}

void critical_section(int process_id, int round) {
    const int already_inside = active_in_critical.fetch_add(1);
    if (already_inside != 0) {
        log(process_id, "ERROR: mutual exclusion was broken");
    }

    log(process_id, "enters critical section, round " + std::to_string(round));

    const int before = shared_counter.load();
    std::this_thread::sleep_for(80ms);
    shared_counter.store(before + 1);

    log(process_id, "updates shared_counter: " + std::to_string(before) +
                        " -> " + std::to_string(before + 1));
    log(process_id, "exits critical section, round " + std::to_string(round));

    active_in_critical.fetch_sub(1);
}

void process(int process_id, int rounds) {
    for (int round = 1; round <= rounds; ++round) {
        peterson_lock(process_id);
        critical_section(process_id, round);
        peterson_unlock(process_id);

        std::this_thread::sleep_for(process_id == 0 ? 35ms : 55ms);
    }
}

int main() {
    constexpr int rounds = 2;

    std::cout << "Peterson algorithm demo: two threads, one critical section\n";
    std::cout << "----------------------------------------------------------\n";

    std::thread p0(process, 0, rounds);
    std::thread p1(process, 1, rounds);

    p0.join();
    p1.join();

    std::cout << "----------------------------------------------------------\n";
    std::cout << "Final shared_counter = " << shared_counter.load()
              << " (expected " << rounds * 2 << ")\n";

    return 0;
}

#include<iostream>
#include<thread>
#include<chrono>
#include<vector>
#include<string>

using namespace std::chrono_literals;

struct ThreadContext{
    std::string name;
    int pc = 0;
    int r1 = 0;
    int r2 = 0;
    int x = 1;
    bool finished = false;
};


void Thread_(ThreadContext& ctx){
    if (ctx.finished) {
        return ;
    }
    else{
        switch (ctx.pc){
            case 0:
                ctx.r1 = ctx.x;
                ctx.r1 ++;
                ctx.x = ctx.r1;
                std::cout << ctx.name << " | pc=0, r1=x+1, x=" << ctx.x << "\n" ;
                ctx.pc ++;
                break;
            case 1:
                ctx.r2 = ctx.x;
                ctx.r2 --;
                ctx.x = ctx.r2;
                std::cout << ctx.name << " | pc=1, r2=x-1, x=" << ctx.x << "\n" ;
                ctx.pc ++;
                break;
            default:
                ctx.finished = true;
                std::cout << ctx.name << " | finished\n";
                break;
        }
        return ;
    }

}


int main(){
    std::vector<ThreadContext> threads = {
        {"Thread-A"},
        {"Thread-B"}
    };
    bool all_finished = false;
    while (!all_finished){
        all_finished = true;
        for (auto& thread : threads){
            if (!thread.finished){
                Thread_(thread);
                all_finished = false;
            }
        }
    }
    return 0;
}


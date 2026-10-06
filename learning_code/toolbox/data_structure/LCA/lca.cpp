#include <iostream>
#include <vector>


void solve(const std::vector<int>& L, int x, int y) {
    while (x != y) {
        if (x > y) {
            x = (x - 1) / 2;
        }
        else {
            y = (y - 1) / 2;
        }
    }

    std::cout << L[x] << std::endl;
}



int main(){
    std::vector<int> a =  {0,1,2,3,4,5,6};
    solve(a,3,4);
}
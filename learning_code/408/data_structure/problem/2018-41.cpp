#include<iostream>
#include<vector>

int MinInteger(std::vector<int> a){
    int max_elem = 0;
    for (int x: a){
        if (x > max_elem){
            max_elem = x;
        } 
    }
    std::vector<bool> exists(max_elem+1,false);

    for (int x: a){
        if (x > 0 && x <= max_elem){
            exists[x] = true;
        }
    }

    for (int i = 1; i <= max_elem; i++) {
        if (!exists[i]) {
            return i;
        }
    }
    return max_elem+1;
}

int main(){
    std::vector<int> test = {1,2,3,4,5,9};
    int res = MinInteger(test);
    std::cout << res << std::endl;
}

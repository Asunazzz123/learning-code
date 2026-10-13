#include <iostream>
#include <vector>

bool judge(const std::vector<int> &tree, int n, int low, int high){
    if (n >= tree.size() || tree[n] == -1)
        return true;

    if (tree[n] <= low || tree[n] >= high)
        return false;

    return judge(tree, 2*n + 1, low, tree[n])
        && judge(tree, 2*n + 2, tree[n], high);
}


int solve(const std::vector<int> &tree) {

    return judge(tree, 0, 0, 1000000001) ? 1 : 0;
}




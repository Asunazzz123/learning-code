#include <iostream>
#include <vector>


struct TreeNode{
    int data;
    TreeNode* left;
    TreeNode* right;
};


std::vector<TreeNode*> _create(const std::vector<int>& data){
    const std::size_t n = data.size();
    std::vector<TreeNode*> res(n);
    for (std::size_t i = 0; i < n; ++i) {
        res[i] = new TreeNode{data[i], nullptr, nullptr};
    }
    for (std::size_t i = 0; i < n; ++i) {
        if (i < n / 2) {
            res[i]->left = res[2*i + 1];
        }
        if (i < (n - 1) / 2) {
            res[i]->right = res[2*i + 2];
        }
    }

    return res;

}

void _delete(std::vector<TreeNode*> nodelist){
    for (TreeNode* ptr : nodelist){
        delete ptr;
    }
    nodelist.clear();
}


int _abs(int x, int y){
    return x>=y?x-y:y-x;
}

void printClosest(TreeNode* root, int K){
    int dist = _abs(root->data,K);
    if (_abs(root->left->data,K) < dist){
        printClosest(root->left,K);
    }
    if (_abs(root->right->data,K)< dist){
        printClosest(root->right,K);
    }

}

void printClosest_2(TreeNode* root, int K){
    TreeNode* pred = nullptr;
    TreeNode* succ = nullptr;

    while(root != nullptr){
        if (root->data == K){
            std::cout << 0 << '\n';
            std::cout << root->data << '\n';
            return ;
        }
        if (root->data < K){
            pred = root;
            root = root->right;
        }
        else{
            succ = root;
            root = root->left;
        }
    }
    int dPred = std::numeric_limits<int>::max();
    int dSucc = std::numeric_limits<int>::max();
    if (pred != nullptr){
        dPred = K - pred->data;
    }
    if (succ != nullptr){
        dSucc = succ->data - K;
    }
    int dist = dPred < dSucc ? dPred : dSucc;

    if (pred != nullptr && dPred == dist) {
        std::cout << pred->data << ' ';
    }
    if (succ != nullptr && dSucc == dist) {
        std::cout << succ->data << ' ';
    }
    std::cout << '\n';
}


int main(){
    auto nodes = _create({8,4,12,2,6,10,14});
    TreeNode* root = nodes[0];

    printClosest_2(root,5);
    _delete(nodes);
    root = nullptr;
}
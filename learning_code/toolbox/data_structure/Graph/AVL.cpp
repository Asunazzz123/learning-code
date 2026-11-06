#include<iostream>
#include<vector>
#include<cmath>


class AVLTree{
    private:
        std::vector<int> data;
    public:
        int find(int k){
            for (int i = 0; i < data.size(); i++){
                if (data[i] == k) return i;
            }
            return -1;
        }

        void push(std::vector<int>& data, int k){
            int len = data.size();
            int height = int(log2f(len));
            int layer_min = len - std::pow(2,(height-1));
            int layer_max = std::pow(2,height) - len;

            for (int i = layer_min; i < layer_max; i++){
                if (k > data[i] && k < data[(i+1)/2]){
                    data[2*(i+1)] = k;
                }
                // if (k > data[i] && )
            }

        }
};

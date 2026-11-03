#include<iostream>
#include<vector>


// int div(std::vector<int> nums, int k){
//     int n = nums.size();
//     int twist = 0;
//     int grp = 0;
//     std::vector<int> tmp = nums;
//     while (twist < n)
//     {
//         for (int i = 0; i<n; i++){
//             tmp[i] = (twist == 0) ?  k / nums[(i+twist)%n] : tmp[i] / nums[(i+twist)%n];
//             if (tmp[(i+twist)%n]>0){
//                 grp++;
//             }
//         }
//         twist ++;
//     }
//     return grp;
// }

int div(const std::vector<int>& nums, int k) {
    if (k <= 1) return 0;

    int n = nums.size();
    int grp = 0;
    std::vector<int> tmp(n, k - 1);

    for (int twist = 0; twist < n; ++twist) {
        for (int i = 0; i + twist < n; ++i) {
            tmp[i] /= nums[i + twist];
            if (tmp[i] > 0) {
                ++grp;
            }
        }
    }
    return grp;
}

int countSubarrays(const std::vector<int>& nums, int k) {
    if (k <= 1) return 0;

    long long product = 1;
    int left = 0;
    int count = 0;

    for (int right = 0; right < nums.size(); ++right) {
        product *= nums[right];

        while (left <= right && product >= k) {
            product /= nums[left];
            ++left;
        }

        count += right - left + 1;
    }

    return count;
}



int main(){
    std::vector<int> nums = {10,5,2,6};
    int k = 100;
    std::cout << div(nums,k) << "\n";
}

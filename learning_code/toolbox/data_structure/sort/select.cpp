#include <iostream>
#include <vector>
#include <utility> 

void SimpleSelectSort(std::vector<int>& a){
    int length = a.size();
    for (int i = 0 ; i < length ; i++){
        int min = i;
        for (int j = i+1; j < length; j++){
            if(a[j] < a[min]){
                min = j;
            }
            if (min != i){
                std::swap(a[i],a[min]);
            }
        }
    }
}


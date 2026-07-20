#include<iostream>
#include<vector>

#define MAX_DIST 65535;

int _abs(int a, int b){
    int res = a > b ? a-b : b-a;
    return res;
}

int _min(int a, int b){
    int min = a > b ? b : a;
    return min;
}

int _min3(int a, int b, int c){
    return _min(a,_min(b,c));
}

int distance(int a, int b, int c){
    return _abs(a,b)+_abs(b,c)+_abs(a,c);
}

struct node{
    int data;
    int set;
    node* next;
};


int mindist(std::vector<int> set1, std::vector<int> set2, std::vector<int> set3){
    int n1 = set1.size();
    int n2 = set2.size();
    int n3 = set3.size();
    int i = 0 ; int j = 0; int k = 0;
    int dist = MAX_DIST;
    
    while( i < n1 && j < n2 && k < n3){
        int d = distance(set1[i],set2[j],set3[k]);
        dist = _min(dist,d);
        int v = _min3(set1[i],set2[j],set3[k]);

        if ( v == set1[i] ){
            i++;
        }
        else if (v == set2[j]){
            j++;
        }
        else {
            k++;
        }


    }
    return dist;
}

int main(){
    std::vector<int> set1 = {-1,0,9};
    std::vector<int> set2 = {-25,-10,10,11};
    std::vector<int> set3 = {2,9,17,30,41};
    
    int min  = mindist(set1,set2,set3);
    std::cout << min << std::endl;
}
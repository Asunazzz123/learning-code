#include<string>
#include<iostream>
#include<vector>

using namespace std;

vector<int> _next(string s){
    int n = static_cast<int>(s.length());
    vector<int> next(n);
    for (int i = 1; i < n; i++){
        int j = next[i-1];
        while (j > 0 && s[i] != s[j]){
            j = next[j-1]; // 递归, 计算更小的子串
        }
        if (s[i] == s[j]){
            j++;           // next[j+1] = next[j] + 1
        }
        next[i] = j;
    }
    return next;
}


vector<int> _next_val(string s){
    int n = static_cast<int>(s.length());
    vector<int> next = _next(s) ;
    vector<int> next_val(n);
    for (int i = 1; i < n; i ++){
        int j = next[i-1];
        if (s[i] != s[j]){
            next_val[i] = j;
        }
        else{
            next_val[i] = next_val[j];
        }
    }
    return next_val;
}


int kmp(string s, string t){
    if (t.empty()){
        return 0;
    }
    vector<int> next_val = _next_val(t);
    int i = 0;
    int j = 0;
    int sl = static_cast<int>(s.size());
    int tl = static_cast<int>(t.size());
    while (i < sl){
        if (s[i] == t[j]){
            ++i;
            ++j;
            if (j == tl){
                return i-j;
            }
        }
        else if (j == 0){
            ++i;
        }
        else{
            j = next_val[j];
        }
    }
    return -1;
}
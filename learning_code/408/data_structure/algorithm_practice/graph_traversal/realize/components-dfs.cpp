#include<iostream>
#include<vector>

struct MGraph
{
    std::vector<std::vector<int>> Nmatrix;
};

void DFS(const MGraph&G,std::vector<int>& visited, int vertex){
    visited[vertex] = 1;

    int n = G.Nmatrix.size();
    for (int next = 0; next < n ; ++next){
        if (G.Nmatrix[vertex][next] != 0 && !visited[next]){
            DFS(G, visited, next);
        }
    }
}


int countComponents(const MGraph &G){
    int n = G.Nmatrix.size();
    std::vector<int> visited(n,0);
    int count = 0;
    for (int vertex = 0; vertex < n; ++vertex){
        ++count;
        DFS(G,visited,vertex);
    }
    return count;
}




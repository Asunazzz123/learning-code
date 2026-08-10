#include<iostream>
#include<vector>
#include<queue>

struct graph_TbENode{
    int adjvex;
    graph_TbENode* nextarc = nullptr;
};


struct graph_TbPNode{
    int data;
    graph_TbENode* firstarc = nullptr;
};



struct ALGraph{
    std::vector<graph_TbPNode> HNode;
};


void _visit(graph_TbPNode* p){
    std::cout << p->data << std::endl;
}

void BFS(graph_TbPNode* p){
    _visit(p);
    std::queue<int> Layer;
    graph_TbENode* tmp = p->firstarc;
    while (tmp -> nextarc != nullptr){
        Layer.push(tmp->adjvex);
    }
}




#include<stdio.h>
#include <stdlib.h>

#define INFINITY 65535
#define MAXVEX 100

typedef int EdgeType;
typedef char VertexType;


typedef struct {
    VertexType vexs[MAXVEX];            
    EdgeType arc[MAXVEX][MAXVEX];       
    int numVertexes, numEdges;          
} MGraph;

EdgeType Bellman(const MGraph *G, int x, int y)
{
    if (G == NULL ||
        x < 0 || x >= G->numVertexes ||
        y < 0 || y >= G->numVertexes) {
        return INFINITY;
    }
    EdgeType dist[MAXVEX];
    for (int i = 0; i < G->numVertexes; i++) {
        dist[i] = INFINITY;
    }
    dist[x] = 0;
    for (int k = 0; k < G->numVertexes - 1; k++) {
        int updated = 0;
        for (int u = 0; u < G->numVertexes; u++) {
            if (dist[u] == INFINITY) {
                continue;
            }
            for (int v = 0; v < G->numVertexes; v++) {
                if (G->arc[u][v] != INFINITY &&
                    dist[u] + G->arc[u][v] < dist[v]) {
                    dist[v] = dist[u] + G->arc[u][v];
                    updated = 1;
                }
            }
        }
        if (!updated) {
            break;
        }
    }
    return dist[y];
}

# 03 频次数组：最常出现值与集合交集

基础与变形题。

两个数组 A、B 的值均位于 [0,M]，M≥0，数组允许为空。

## 任务 A

返回 A 中出现次数最多的值；并列时取值较小者；A 为空时返回 -1。

```cpp
int mostFrequent(const int A[], int n, int M);
```

## 任务 B

按升序输出同时出现在 A、B 中的值，每个值只输出一次。

```cpp
void printIntersection(const int A[], int na,
                       const int B[], int nb, int M);
```

## 要求

- 两个任务分别实现，不能修改输入。
- 时间分别为 O(n+M)、O(na+nb+M)，辅助空间 O(M+1)。
- 不排序，不使用 set 或 map。
- 解释任务 A 为何不能只用 bool 标记，以及任务 B 如何避免重复输出。

## 自测

- A=[3,1,3,1,2]：任务 A 返回 1。
- A=[3,1,3,1,2]，B=[3,3,0,1]，M=3：任务 B 输出 1 3。
- 其中一数组为空；M=0 且数组中只有 0。


BeginPackage["Distribution`"];

Chi::usage = "Chi[k] 表示自由度为 k 的 Chi方 分布。";
t::usage = "t[k] 表示自由度为 k 的 t分布";

Begin["`Private`"];

Chi /: Mean[Chi[k_]] :=
    k

Chi /: Variance[Chi[k_]] :=
    2*k

Chi /: PDF[Chi[k_],r_] :=
    Piecewise[{
        {
            2^(1 - k/2) r^(k - 1) Exp[-r^2/2]/Gamma[k/2],
            r >= 0
        }
    }, 0]

t /: Mean[t[k_]] :=
    0



End[];
EndPackage[];


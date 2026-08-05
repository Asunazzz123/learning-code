BeginPackage["Distribution`"];

Chi::usage = "Chi[k] 表示自由度为 k 的 Chi方 分布。";
Begin["`Private`"];

Chi /: Mean[Chi[k_]] :=
    k

Chi /: Variance[Chi[k_]] :=
    2*k

End[];
EndPackage[];


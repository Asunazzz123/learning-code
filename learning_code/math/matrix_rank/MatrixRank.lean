import Mathlib.LinearAlgebra.Matrix.Rank
import Lean.Elab.Tactic.Omega

/-!
# Sylvester 秩不等式

设 A 为 m × n 矩阵，B 为 n × p 矩阵，系数取自任意域 K。
证明 rank A + rank B ≤ rank (A * B) + n，继而得到减法形式。
-/

namespace MatrixRank

open Module LinearMap

variable {K : Type*} [Field K] {m n p : ℕ}

/-- Sylvester 秩不等式的加法形式。 -/
theorem sylvester_rank_add (A : Matrix (Fin m) (Fin n) K)
    (B : Matrix (Fin n) (Fin p) K) :
    A.rank + B.rank ≤ (A * B).rank + n := by
  classical
  -- 将 A 限制在 B 的像空间上。
  let V := LinearMap.range B.mulVecLin
  let f := A.mulVecLin.domRestrict V
  have hnull := f.finrank_range_add_finrank_ker
  have hA := A.mulVecLin.finrank_range_add_finrank_ker
  -- 限制映射的像等于 AB 的像。
  have hrange : LinearMap.range f = LinearMap.range (A * B).mulVecLin := by
    simp [f, V, Matrix.mulVecLin_mul, LinearMap.range_comp]
  -- 限制映射的核嵌入 A 的核，因此维数不增。
  have hker : finrank K (LinearMap.ker f) ≤ finrank K (LinearMap.ker A.mulVecLin) := by
    calc
      finrank K (LinearMap.ker f) =
          finrank K ((LinearMap.ker f).map V.subtype) :=
        (Submodule.finrank_map_subtype_eq V (LinearMap.ker f)).symm
      _ ≤ finrank K (LinearMap.ker A.mulVecLin) := by
        apply Submodule.finrank_mono
        rintro x ⟨y, hy, rfl⟩
        exact hy
  rw [hrange] at hnull
  change (A * B).rank + finrank K (LinearMap.ker f) = B.rank at hnull
  have hAn : A.rank + finrank K (LinearMap.ker A.mulVecLin) = n := by
    simpa [Matrix.rank, Module.finrank_pi] using hA
  omega

/-- Sylvester 秩不等式：rank(AB) ≥ rank(A) + rank(B) - n。
这里的秩属于 ℕ，减法是自然数的截断减法。 -/
theorem sylvester_rank (A : Matrix (Fin m) (Fin n) K)
    (B : Matrix (Fin n) (Fin p) K) :
    A.rank + B.rank - n ≤ (A * B).rank := by
  have h := sylvester_rank_add A B
  omega

end MatrixRank

#!/usr/bin/env python3
"""
セグメンテーション違反修正の段階的テスト
ドキュメントで提案されている手順に従ってテストを実行
"""

import numpy as np
import scipy.sparse as sp
import time
import sys
import os

# rk4_sparse_cppモジュールをインポート
try:
    from rk4_sparse._rk4_sparse_cpp import (
        test_basic_sparse_multiply, 
        rk4_sparse_blas_optimized, 
        rk4_sparse_eigen
    )
    print("✓ rk4_sparse_cppモジュールのインポート成功")
except ImportError as e:
    print(f"✗ rk4_sparse_cppモジュールのインポート失敗: {e}")
    sys.exit(1)

def create_test_matrices(dim):
    """テスト用のスパース行列を作成"""
    print(f"  {dim}次元のテスト行列を作成中...")
    
    # 対角成分
    diag_indices = np.arange(dim)
    diag_data = np.random.random(dim) + 1j * np.random.random(dim)
    
    # 非対角成分（近接相互作用）
    off_diag_data = []
    off_diag_row = []
    off_diag_col = []
    
    for i in range(dim):
        # 隣接する要素との相互作用
        if i > 0:
            off_diag_row.append(i)
            off_diag_col.append(i-1)
            off_diag_data.append(0.1 * (np.random.random() + 1j * np.random.random()))
        
        if i < dim - 1:
            off_diag_row.append(i)
            off_diag_col.append(i+1)
            off_diag_data.append(0.1 * (np.random.random() + 1j * np.random.random()))
    
    # 行列の構築
    row_indices = np.concatenate([diag_indices, off_diag_row])
    col_indices = np.concatenate([diag_indices, off_diag_col])
    data = np.concatenate([diag_data, off_diag_data])
    
    # スパース行列の作成
    H0 = sp.csr_matrix((data, (row_indices, col_indices)), shape=(dim, dim))
    mux = sp.csr_matrix((data * 0.1, (row_indices, col_indices)), shape=(dim, dim))
    muy = sp.csr_matrix((data * 0.1, (row_indices, col_indices)), shape=(dim, dim))
    
    # 明示的にC順・型指定でデータを再作成
    H0.data = np.ascontiguousarray(H0.data, dtype=np.complex128)
    H0.indices = np.ascontiguousarray(H0.indices, dtype=np.int32)
    H0.indptr = np.ascontiguousarray(H0.indptr, dtype=np.int32)
    
    mux.data = np.ascontiguousarray(mux.data, dtype=np.complex128)
    mux.indices = np.ascontiguousarray(mux.indices, dtype=np.int32)
    mux.indptr = np.ascontiguousarray(mux.indptr, dtype=np.int32)
    
    muy.data = np.ascontiguousarray(muy.data, dtype=np.complex128)
    muy.indices = np.ascontiguousarray(muy.indices, dtype=np.int32)
    muy.indptr = np.ascontiguousarray(muy.indptr, dtype=np.int32)
    
    return H0, mux, muy

def main():
    print("セグメンテーション違反修正の段階的テスト")
    print("=" * 50)
    
    # ステップ1: 基本的なスパース行列-ベクトル積のテスト
    print("\n=== ステップ1: 基本的なスパース行列-ベクトル積のテスト ===")
    dim = 1024
    print(f"  次元: {dim}")
    
    print("  行列作成開始...")
    H0, mux, muy = create_test_matrices(dim)
    print("  行列作成完了")
    
    print("  ベクトル作成開始...")
    x = np.random.rand(dim) + 1j * np.random.rand(dim)
    print("  ベクトル作成完了")
    x = np.ascontiguousarray(x, dtype=np.complex128)
    
    print("  行列の情報:")
    print(f"    H0.shape: {H0.shape}")
    print(f"    H0.nnz: {H0.nnz}")
    print(f"    H0.data.shape: {H0.data.shape}")
    print(f"    H0.indices.shape: {H0.indices.shape}")
    print(f"    H0.indptr.shape: {H0.indptr.shape}")
    print(f"    x.shape: {x.shape}")
    print(f"    x.dtype: {x.dtype}")

    try:
        print("  test_basic_sparse_multiply呼び出し開始...")
        y = test_basic_sparse_multiply(H0, x)
        print("✓ 基本的なスパース行列-ベクトル積: 成功")
        print(f"  結果の形状: {y.shape}")
        print(f"  結果の型: {y.dtype}")
    except Exception as e:
        print(f"✗ 基本的なスパース行列-ベクトル積: 失敗 - {e}")
        return

    # ステップ2: 標準版のRK4テスト（比較用）
    print("\n=== ステップ2: 標準版のRK4テスト（比較用） ===")
    Ex = np.random.rand(10)
    Ey = np.random.rand(10)
    Ex = np.ascontiguousarray(Ex, dtype=np.float64)
    Ey = np.ascontiguousarray(Ey, dtype=np.float64)
    psi0 = np.random.rand(dim) + 1j * np.random.rand(dim)
    psi0 = np.ascontiguousarray(psi0, dtype=np.complex128)

    try:
        print("  rk4_sparse_eigen呼び出し開始...")
        result_standard = rk4_sparse_eigen(H0, mux, muy, Ex, Ey, psi0, 0.01, False, 1, False)
        print("✓ 標準版のRK4: 成功")
        print(f"  結果の形状: {result_standard.shape}")
        print(f"  結果の型: {result_standard.dtype}")
    except Exception as e:
        print(f"✗ 標準版のRK4: 失敗 - {e}")
        return

    # ステップ3: BLAS無効化版のRK4テスト
    print("\n=== ステップ3: BLAS無効化版のRK4テスト ===")
    Ex = np.random.rand(10)
    Ey = np.random.rand(10)
    Ex = np.ascontiguousarray(Ex, dtype=np.float64)
    Ey = np.ascontiguousarray(Ey, dtype=np.float64)
    psi0 = np.random.rand(dim) + 1j * np.random.rand(dim)
    psi0 = np.ascontiguousarray(psi0, dtype=np.complex128)
    
    print("  入力データの情報:")
    print(f"    Ex.shape: {Ex.shape}, Ex.dtype: {Ex.dtype}")
    print(f"    Ey.shape: {Ey.shape}, Ey.dtype: {Ey.dtype}")
    print(f"    psi0.shape: {psi0.shape}, psi0.dtype: {psi0.dtype}")
    print(f"    H0.nnz: {H0.nnz}")
    print(f"    mux.nnz: {mux.nnz}")
    print(f"    muy.nnz: {muy.nnz}")
    
    # 行列のパターンが一致しているかを確認
    print("  行列パターンの確認:")
    print(f"    H0.data.shape == mux.data.shape: {H0.data.shape == mux.data.shape}")
    print(f"    H0.data.shape == muy.data.shape: {H0.data.shape == muy.data.shape}")
    print(f"    H0.indices.shape == mux.indices.shape: {H0.indices.shape == mux.indices.shape}")
    print(f"    H0.indices.shape == muy.indices.shape: {H0.indices.shape == muy.indices.shape}")
    print(f"    H0.indptr.shape == mux.indptr.shape: {H0.indptr.shape == mux.indptr.shape}")
    print(f"    H0.indptr.shape == muy.indptr.shape: {H0.indptr.shape == muy.indptr.shape}")

    try:
        print("  rk4_sparse_blas_optimized呼び出し開始...")
        result = rk4_sparse_blas_optimized(H0, mux, muy, Ex, Ey, psi0, 0.01, False, 1, False)
        print("✓ BLAS無効化版のRK4: 成功")
        print(f"  結果の形状: {result.shape}")
        print(f"  結果の型: {result.dtype}")
    except Exception as e:
        print(f"✗ BLAS無効化版のRK4: 失敗 - {e}")
        return

    # ステップ4: 結果の比較テスト
    print("\n=== ステップ4: 結果の比較テスト ===")
    try:
        # 結果の比較
        diff = np.abs(result - result_standard).max()
        print(f"  最大差分: {diff}")
        if diff < 1e-10:
            print("✓ 結果が一致しています")
        else:
            print("✗ 結果が一致していません")
            
    except Exception as e:
        print(f"✗ 結果の比較: 失敗 - {e}")
        return

    # ステップ5: より大きな次元でのテスト
    print("\n=== ステップ5: より大きな次元でのテスト ===")
    dim_large = 2048
    H0_large, mux_large, muy_large = create_test_matrices(dim_large)
    psi0_large = np.random.rand(dim_large) + 1j * np.random.rand(dim_large)
    psi0_large = np.ascontiguousarray(psi0_large, dtype=np.complex128)

    try:
        result_large = rk4_sparse_blas_optimized(H0_large, mux_large, muy_large, Ex, Ey, psi0_large, 0.01, False, 1, False)
        print("✓ 大次元でのBLAS無効化版のRK4: 成功")
        print(f"  結果の形状: {result_large.shape}")
    except Exception as e:
        print(f"✗ 大次元でのBLAS無効化版のRK4: 失敗 - {e}")
        return

    print("\n=== テスト完了 ===")
    print("✓ セグメンテーション違反の修正が成功しました！")
    print("  すべてのテストが正常に完了しました。")

if __name__ == "__main__":
    main() 
import numpy as np
import cupy as cp
from . import config

# 寻找到cfRNA和单细胞中的交集
def filter_with_overlap_gene(sample_exp, cell_exp_adata):

    # if disease_name == 'tuberculosis':
    #     # Refine `marker_genes` so that they are shared by both adatas
    #     genes = list(set(sample_cfRNA_exp.Ensemble_name) & set(cell_exp_adata.var['ensemblid']))
    #     genes.sort()
    # elif disease_name == 'pregnancy':
    #     ids_no_version = [id.split('.')[0] for id in cell_exp_adata.var['ensemblid'].tolist()]
    #     cell_exp_adata.var.index = ids_no_version
    #     cell_exp_adata.var_names_make_unique()

    #     genes = list(set(sample_cfRNA_exp.Ensemble_name) & set(ids_no_version))
    #     genes.sort()

    sample_cfRNA_names = sample_exp.columns
    sample_cfRNA_names = [eid.split('.')[0] for eid in sample_cfRNA_names]
    sample_exp.columns = sample_cfRNA_names

    scRNA_cfRNA_names = cell_exp_adata.var['ensemblid']
    scRNA_cfRNA_names = [eid.split('.')[0] for eid in scRNA_cfRNA_names]
    cell_exp_adata.var.index = scRNA_cfRNA_names
    cell_exp_adata.var_names_make_unique()

    genes = list(set(sample_cfRNA_names) & set(scRNA_cfRNA_names))

    print('Number of overlap genes:', len(genes))


    # cell_exp_adata.uns["overlap_genes"] = genes
    cell_exp_adata = cell_exp_adata[:, genes]   

    sample_exp = sample_exp[genes]

    return sample_exp, cell_exp_adata


def GNMF(sample_cfRNA, cell_cfRNA, sample_sim, alpha, beta, iter_num, random_seed = config.seed_value):
    X = cell_cfRNA.T
    U = sample_cfRNA
    np.random.rand(random_seed)
    V = np.random.rand(sample_cfRNA.shape[0], cell_cfRNA.shape[0])

    S_sample = sample_sim
    I_sample = np.diag(S_sample.sum(axis = 1))
    F_sample = I_sample - S_sample

    for cur_iter in range(iter_num):
        # 更新基矩阵U
        VX = V @ X.T
        VV = V @ V.T
        VVU = VV @ U

        denominator = VX + beta * S_sample @ U
        numerator = (1 + alpha) * VVU + beta * I_sample @ U

        U = U * (denominator / np.maximum(numerator, 1e-10))

        # 更新系数矩阵
        UX = U @ X
        UU = U @ U.T
        UUV = UU @ V

        denominator = UX
        numerator = (1 + alpha) * UUV

        V = V * (denominator / np.maximum(numerator, 1e-10))

        # 计算目标函数和误差
        dA = X - U.T @ V
        obj = (dA ** 2).sum() + alpha * ((U.T @ V)**2).sum() + beta * (U.T @ F_sample @ U).trace()

        if cur_iter == 0:
            last_error = 0
        else:
            last_error = error

        error = abs(dA).mean() / X.mean()

        if (cur_iter + 1) % 10 == 0:
            print('GNMF: step=%d  obj=%f  error=%f\n, last_error=%f\n, ddd:%10f' % (cur_iter+1, obj, error, last_error, last_error - error))

        # 终止条件
        if abs(last_error - error) < 1e-10:
            break
            # 输出结果

    return U.T @ V, U, V


# GNMF
def GNMF_gpu(sample_cell, sample_cfRNA, cell_cfRNA, sample_sim, cell_sim, alpha, beta, iter_num):
    # 初始化基矩阵和系数矩阵
    # X = sample_cell
    X = cp.asarray(sample_cfRNA @ cell_cfRNA.T)
    U = cp.asarray(sample_cfRNA)
    V = cp.asarray(cell_cfRNA)

    S_s = cp.asarray(sample_sim)
    I_s = S_s.sum(axis=1)
    F_s = I_s - S_s

    S_c = cp.asarray(cell_sim)
    I_c = S_c.sum(axis=1)
    F_c = I_c - S_c

    # 矩阵分解迭代
    for cur_iter in range(iter_num):
        # 更新基矩阵U
        XV = X @ V
        VV = V.T @ V
        UVV = U @ VV

        denominator = XV + beta * S_s @ U
        numerator = (1+alpha) * UVV + beta * I_s @ U

        U = U * (denominator / cp.maximum(numerator, 1e-10))

        # 更新系数矩阵
        XU = X.T @ U
        UU = U.T @ U
        VUU = V @ UU

        denominator = XU + beta * S_c @ V
        numerator = (1+alpha) * VUU + beta * I_c @ V

        V = V * (denominator / cp.maximum(numerator, 1e-10))


        # 计算目标函数和误差
        dA = X - U @ V.T
        obj = (dA**2).sum() + alpha * ((U @ V.T)**2).sum() + beta * ((U.T @ F_s @ U).trace() + (V.T @ F_c @ V).trace())

        if cur_iter == 0:
            last_error = 0
        else:
            last_error = error

        error = abs(dA).mean() / X.mean()


        print('GNMF: step=%d  obj=%f  error=%f\n, last_error=%f\n, ddd:%10f' % (cur_iter, obj, error, last_error, last_error - error))

        # 终止条件
        if abs(last_error - error) < 1e-10:
            break
            # 输出结果


        if cur_iter != 0:
            last_error = error

    return cp.asnumpy(cp.dot(U, V.T)), cp.asnumpy(U), cp.asnumpy(V)


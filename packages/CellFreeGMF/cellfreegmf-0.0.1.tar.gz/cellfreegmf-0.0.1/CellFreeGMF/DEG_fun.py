from . import config
from . import R_script
import pandas as pd
import numpy as np
import os

def DEG_DESeq2_fun(exp_matrix, label, file_path = None):
    import rpy2.robjects as robjects
    from rpy2.robjects import pandas2ri
    from rpy2.robjects.packages import importr

    # 创建目录
    if not os.path.exists(file_path):
        os.makedirs(file_path, exist_ok=True)
    # 开启 pandas ↔ R 自动转换
    pandas2ri.activate()

    # 定义 R 函数
    robjects.r(R_script.DESeq2_function)

    # 取 R 函数句柄
    DESeq2_function = robjects.globalenv['DESeq2_function']

    group = pd.Series(label.tolist(),
                    index=label.index)

    # file_path = current_path + '/save_data/' + disease_name
    # ✅ 调用 R 函数
    if file_path is None:
        res_r = DESeq2_function(exp_matrix.T, group, 'FALSE')
    else:
        res_r = DESeq2_function(exp_matrix.T, group, 'TRUE', file_path)

    # ✅ 转回 pandas
    res_df = pandas2ri.rpy2py(res_r)
    res_df = res_df.dropna()
    res_df = res_df.sort_values(by='padj', ascending=True)
    res_df = res_df[res_df['padj'] < 0.05]

    if file_path is not None:
        res_df.to_csv(file_path + '/DEG_res.csv')

    return res_df

def standard_count(count_matrix):
    import rpy2.robjects as robjects
    from rpy2.robjects import numpy2ri

    # 启用 numpy <-> R 自动转换
    numpy2ri.activate()

    robjects.r(R_script.DESeq2_standard)

    # 获取 R 函数句柄
    my_fun = robjects.globalenv['DESeq2_standard']

    # 3️⃣ 调用 R 函数
    # numpy → R 矩阵会自动转换（因为 activate）
    output_r = my_fun(count_matrix.T.to_numpy())

    # 4️⃣ R 矩阵 → numpy
    standard_matrix = np.array(output_r)

    standard_matrix = pd.DataFrame(standard_matrix,
                                   index=count_matrix.index,
                                   columns=count_matrix.columns)
    
    return standard_matrix


def DEG_limma_fun(exp_matrix, label, file_path = None):
    import rpy2.robjects as robjects
    from rpy2.robjects import pandas2ri
    from rpy2.robjects.packages import importr

    # 创建目录
    if not os.path.exists(file_path):
        os.makedirs(file_path, exist_ok=True)
    # 开启 pandas ↔ R 自动转换
    pandas2ri.activate()

    # 定义 R 函数
    robjects.r(R_script.limma_function)

    # 取 R 函数句柄
    limma_function = robjects.globalenv['limma_function']

    group = pd.Series(label.tolist(),
                    index=label.index)

    # file_path = current_path + '/save_data/' + disease_name
    # ✅ 调用 R 函数
    if file_path is None:
        res_r = limma_function(exp_matrix.T, group, 'TRUE')
    else:
        res_r = limma_function(exp_matrix.T, group, 'TRUE', file_path)

    # ✅ 转回 pandas
    res_df = pandas2ri.rpy2py(res_r)
    res_df = res_df.dropna()
    res_df = res_df.sort_values(by='adj.P.Val', ascending=True)
    res_df = res_df[res_df['adj.P.Val'] < 0.05]

    if file_path is not None:
        res_df.to_csv(file_path + '/DEG_res.csv')


    return res_df


import pandas as pd
import numpy as np

# 标准化矩阵
def log_cpm(matrix: pd.DataFrame) -> pd.DataFrame:
    matrix = matrix.T
    lib_size = matrix.sum(axis=0)  # 每个样本或细胞的总 counts
    cpm = matrix.divide(lib_size, axis=1) * 1e6
    log_cpm = np.log2(cpm + 1)
    return log_cpm

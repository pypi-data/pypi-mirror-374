import numpy as np
from scipy.signal import find_peaks

def detect_abnormal_spectra(X, threshold=5, min_abnormal_points=3, ranges=None):
    """
    检测异常光谱（局部尖峰）

    参数:
        X: numpy array, shape = (n_spectra, n_wavelengths)
        threshold: 超过 MAD 的倍数判定为异常
        min_abnormal_points: 一条光谱至少出现多少个异常点才认为是异常光谱
        ranges: list of [start, end]，只检测这些范围的点，例如 [[0,30],[50,100]]

    返回:
        abnormal_spectra: 异常光谱索引列表
        abnormal_detail: {光谱索引: 异常点索引列表(全局索引)}
        normal_spectra: 正常光谱数据 (list)
    """
    X = np.array(X, dtype=float)
    n, m = X.shape

    # 生成需要检测的索引
    if ranges:
        scan_indices = []
        for start, end in ranges:
            scan_indices.extend(range(start, min(end+1, m)))  # 防止越界
        scan_indices = np.array(sorted(set(scan_indices)))
    else:
        scan_indices = np.arange(m)
    # 只计算检测范围内的 MAD
    med = np.median(X[:, scan_indices], axis=0)
    mad = np.median(np.abs(X[:, scan_indices] - med), axis=0) + 1e-9  

    abnormal_spectra = []
    abnormal_detail = []

    for i in range(n):
        diff = np.abs(X[i, scan_indices] - med) / mad
        abnormal_points_local = np.where(diff > threshold)[0]
        if len(abnormal_points_local) >= min_abnormal_points:
            abnormal_spectra.append(i)
            # 映射回原始全局索引
            detail = {"index":i,"point":scan_indices[abnormal_points_local].tolist()}
            abnormal_detail.append(detail)

    # ✅ 计算正常光谱（完整数据）
    all_indices = set(range(n))
    normal_indices = sorted(list(all_indices - set(abnormal_spectra)))
    normal_spectra = X[normal_indices, :].tolist()  # 取出完整光谱数据

    return abnormal_spectra, abnormal_detail, normal_spectra


def detect_abnormal_spectra_normal(X, threshold=3, min_abnormal_points=3, ranges=None):
    """
    检测异常光谱（基于正态分布 z-score）

    参数:
        X: numpy array, shape = (n_spectra, n_wavelengths)
        threshold: 超过多少倍标准差判定异常
        min_abnormal_points: 一条光谱至少出现多少个异常点才认为是异常光谱
        ranges: list of [start, end]，只检测这些范围的点，例如 [[0,30],[50,100]]

    返回:
        abnormal_spectra: 异常光谱索引列表
        abnormal_detail: [{"index": 光谱索引, "point": 异常点索引列表(全局索引)}]
        normal_spectra: 正常光谱数据 (list)
    """
    X = np.array(X, dtype=float)
    n, m = X.shape

    # 生成需要检测的索引
    if ranges:
        scan_indices = []
        for start, end in ranges:
            scan_indices.extend(range(start, min(end+1, m)))  # 防止越界
        scan_indices = np.array(sorted(set(scan_indices)))
    else:
        scan_indices = np.arange(m)

    # 只计算检测范围内的均值和标准差
    mean = np.mean(X[:, scan_indices], axis=0)
    std = np.std(X[:, scan_indices], axis=0) + 1e-9  # 防止除零

    abnormal_spectra = []
    abnormal_detail = []

    for i in range(n):
        z = np.abs(X[i, scan_indices] - mean) / std
        abnormal_points_local = np.where(z > threshold)[0]
        if len(abnormal_points_local) >= min_abnormal_points:
            abnormal_spectra.append(i)
            detail = {"index": i, "point": scan_indices[abnormal_points_local].tolist()}
            abnormal_detail.append(detail)

    # ✅ 计算正常光谱（完整数据）
    all_indices = set(range(n))
    normal_indices = sorted(list(all_indices - set(abnormal_spectra)))
    normal_spectra = X[normal_indices, :].tolist()

    return abnormal_spectra, abnormal_detail, normal_spectra



import os
from . import ipath
import numpy as np
import os.path as osp
from pypcd4 import PointCloud
from pyquaternion import Quaternion


"""
函数列表:
- read_pcd_as_np
    读取pcd文件并转换成numpy数组
- save_pace
    存储点云
- get_transformation_matrix
    从3x3|四元数,平移向量获取变换矩阵

"""

def read_pcd_as_np(fpath, dtype=np.float32):
    return PointCloud.from_path(fpath).numpy().astype(dtype)


def read_pcd_slice_as_np(dir_, file_type='.pcd'):
    paths = ipath.get_paths(dir_, file_type, is_lis=True, is_sort=True)
    pts_lis = list()
    for path in paths:
        pts = read_pcd_as_np(path)
        pts_lis.append(pts)
    all_pts = np.concatenate(pts_lis, axis=0)
    return all_pts


def save_pcd_slice(dir_, pcd, slice_num=1e7, fields=None, types=None, n_cols=None):
    # 点云太大, 将点云分成多个片段存储
    os.makedirs(dir_, exist_ok=True)
    slice_num = int(slice_num)
    idx, cnt = 0, 0
    while True:
        pcd_ = pcd[cnt:cnt+slice_num]
        if len(pcd_) == 0:
            break
        path = osp.join(dir_, f"{idx}.pcd")
        save_pcd(path, pcd_, fields, types, n_cols)
        idx += 1
        cnt += slice_num


def save_pcd(path, pcd, fields=None, types=None, n_cols=None):
    """Save numpy ndarray|torch.Tensor -> pcd

    Args:
        path (str): path
        pcd (nd.array): N x <3|4|5>
    """
    if types is None:
        types = (np.float32, np.float32, np.float32, np.float32, np.float32)
    if fields is None:
        fields = ("x", "y", "z", "intensity", "new_field")

    if n_cols is None:
        n_cols = pcd.shape[1]

    fields = fields[:n_cols]
    types = types[:n_cols]
    pcd = pcd[:, :n_cols]
    pc = PointCloud.from_points(pcd, fields, types)
    pc.save(path)


def get_transformation_matrix(rot, tran, is_quat=False):
    """获取变换矩阵

    Args:
        rot (np.array|quat): 3x3 矩阵 | 四元数(默认[w, x, y, z])
        tran (np.array|list|...): [x, y, z]
        is_quat (bool, optional): rot 是否为四元数

    Returns:
        4x4矩阵
    """
    M = np.eye(4, dtype=np.float64)
    _rot = rot
    if is_quat:
        _rot = Quaternion(_rot).rotation_matrix
    _tran = np.array(tran)
    M[:3, :3] = _rot
    M[:3, 3] = _tran
    return M, _rot, _tran


def pcd_matrix_multi(pcd, M):
    """对点云进行变换

    Args:
        pcd (np.array): Nx3| Nx4| Nx5
        M (np.array): 4x4 变换矩阵
            | R T |
            | 0 1 |
    """
    # 先拷贝原始点云 -> 使用前3列并齐次化 -> 矩阵相乘得到结果 -> 结果填充到拷贝的点云中
    axis_1 = pcd.shape[1]
    assert axis_1 >= 3
    new_pcd = pcd.copy()
    tmp_pcd = pcd[:, :3].copy()
    tmp_pcd = np.pad(tmp_pcd, ((0, 0), (0, 1)), 
                     mode='constant', constant_values=1)
    tmp_pcd = tmp_pcd @ M.T
    new_pcd[:, :3] = tmp_pcd[:, :3]
    return new_pcd


def get_range_mask(pc, range_=None, is_mask=True):
    # range: [x_min, y_min, z_min, x_max, y_max, z_max]
    mask = ((pc[:, 0] > range_[0])
            & (pc[:, 0] < range_[3])
            & (pc[:, 1] > range_[1])
            & (pc[:, 1] < range_[4])
            & (pc[:, 2] > range_[2])
            & (pc[:, 2] < range_[5]))
    if is_mask:
        pc = pc[mask]
    return pc, mask
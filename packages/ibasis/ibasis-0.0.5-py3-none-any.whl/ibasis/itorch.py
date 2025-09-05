import math
import numpy as np
import torch
from typing import List, Optional, Tuple, Union


def parse_img_from_tensor(tensor, idx=None,
                          ipt_fmt='NCHW', ipt_type='float', ipt_space='rgb',
                          opt_fmt='HWC', opt_type='uint8', opt_space='rgb',
                          mean=None, std_var=None):
    """Convert tensor to image

    Args:
        tensor (torch.Tensor): input tensor
        idx (int, optional): index. Defaults to None. None mean get all
        ipt_fmt (str, optional): input format. Defaults to 'NCHW'
        ipt_type (str, optional): input type. Defaults to float[0~1] or uint8
        ipt_space (str, optional): input image color space
        opt_fmt (str, optional): output format. Defaults to 'HWC'
        opt_type (str, optional): output type. Defaults to 'uint8'
        opt_space (str, optional): output image color space
        mean (np.arr, optional): mean, length should map with input,
            e.g. input is NCHW, or CHW (c! = 1), mean should be: [v1, v2, v3]
            e.g. input is NCHW, or CHW (c == 1) or C NOT IN input, mean = [v1]
        std_var (float, optional): standard variance

    Returns:
        list: [img, ...]
    """
    if isinstance(tensor, torch.Tensor):
        array = tensor.to('cpu').detach().numpy()
    else:
        array = tensor

    is_convert_value = ipt_type.lower() != opt_type.lower()
    is_convert_space = ipt_space.lower() != opt_space.lower()

    if ipt_fmt.startswith('N'):         # ['NCHW', 'NHW', 'NHWC']
        arr_lis = [array[i] for i in range(len(array))]
        if idx is not None:
            arr_lis = [arr_lis[idx]]
        ipt_fmt = ipt_fmt[1:]
    else:                               # ['CHW', 'HW', 'HWC']
        arr_lis = [array]

    # auto squeeze axis when axis == 1
    if 'C' in ipt_fmt:
        c_idx = ipt_fmt.find('C')
        if c_idx != -1:
            sqz_arr_lis = [arr.squeeze(c_idx) if arr.shape[c_idx] == 1 
                           else arr for arr in arr_lis]
            if len(sqz_arr_lis[0].shape) == len(arr_lis[0].shape)-1:
                ipt_fmt = ipt_fmt.replace('C', '')
                if 'C' in opt_fmt:
                    opt_fmt = opt_fmt.replace('C', '')
                arr_lis = sqz_arr_lis
    einsum_rule = ''
    if ipt_fmt != opt_fmt:
        if len(ipt_fmt) != len(opt_fmt):
            raise TypeError(f"Input format '{ipt_fmt}' DO NOT match Output \
                             format '{opt_fmt}'")
        else:
            einsum_rule = f"{ipt_fmt}->{opt_fmt}"

    res_lis = []
    for arr in arr_lis:
        if einsum_rule:
            arr = np.einsum(einsum_rule, arr)
        if is_convert_value:
            arr *= 255
            if std_var is not None:
                arr *= std_var
            if mean is not None:
                arr += mean
            arr = np.clip(arr, 0, 255)
        if is_convert_space:
            arr = arr[..., ::-1].copy()
        if 'uint8' in opt_type:
            # use: arr = arr.astype(arr) get ERROR
            # img = cv2.polylines(img, [coords], 1, color, 1)
            # cv2.error: OpenCV(4.5.5) :-1: error: (-5:Bad argument) in function 'polylines'
            # > Overload resolution failed:
            # >  - Layout of the output array img is incompatible with cv::Mat
            # >  - Expected Ptr<cv::UMat> for argument 'img'
            arr = np.ascontiguousarray(arr).astype(np.uint8)
        res_lis.append(arr)
    return res_lis


def make_grid(
    tensor: Union[np.ndarray, List[np.ndarray]],  # 修改输入类型为numpy数组
    nrow: int = 8,
    padding: int = 2,
    normalize: bool = False,
    value_range: Optional[Tuple[int, int]] = None,
    scale_each: bool = False,
    pad_value: float = 0.0,
) -> np.ndarray:  # 返回类型改为numpy数组
    """
    from torchvision.utils import make_grid
    Make a grid of images (numpy版本).
    参数说明与原函数保持一致...
    """
    # ... 原有日志记录代码保持不变 ...

    if not isinstance(tensor, np.ndarray):
        if isinstance(tensor, list):
            for t in tensor:
                if not isinstance(t, np.ndarray):
                    raise TypeError(f"numpy array or list of arrays expected, got a list containing {type(t)}")
        else:
            raise TypeError(f"numpy array or list of arrays expected, got {type(tensor)}")

    # 将列表中的数组合并为4D数组
    if isinstance(tensor, list):
        tensor = np.stack(tensor, axis=0)

    # 处理不同维度的情况
    if tensor.ndim == 2:  # H x W
        tensor = np.expand_dims(tensor, axis=0)
    if tensor.ndim == 3:  # C x H x W 或 H x W x C
        if tensor.shape[0] == 1:  # 单通道转3通道
            tensor = np.concatenate([tensor, tensor, tensor], axis=0)
        tensor = np.expand_dims(tensor, axis=0)
    if tensor.ndim == 4 and tensor.shape[1] == 1:  # 批次单通道
        tensor = np.concatenate([tensor, tensor, tensor], axis=1)

    # 归一化处理
    if normalize:
        tensor = tensor.copy()
        def norm_ip(img, low, high):
            img[:] = np.clip(img, low, high)
            img[:] = (img - low) / max(high - low, 1e-5)
        
        def norm_range(t, value_range):
            if value_range is not None:
                norm_ip(t, value_range[0], value_range[1])
            else:
                norm_ip(t, float(t.min()), float(t.max()))
        
        if scale_each:
            for t in tensor:
                norm_range(t, value_range)
        else:
            norm_range(tensor, value_range)

    # 创建网格
    nmaps = tensor.shape[0]
    xmaps = min(nrow, nmaps)
    ymaps = int(math.ceil(nmaps / xmaps))
    height, width = int(tensor.shape[2] + padding), int(tensor.shape[3] + padding)
    num_channels = tensor.shape[1]
    
    # 使用numpy full初始化网格
    grid = np.full(
        (num_channels, height * ymaps + padding, width * xmaps + padding),
        pad_value,
        dtype=tensor.dtype
    )
    
    k = 0
    for y in range(ymaps):
        for x in range(xmaps):
            if k >= nmaps:
                break
            # 使用numpy切片替换narrow操作
            y_start = y * height + padding
            x_start = x * width + padding
            grid[:, y_start:y_start+height-padding, x_start:x_start+width-padding] = tensor[k]
            k += 1
            
    return grid

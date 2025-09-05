import numpy as np
from PIL import Image
import os.path as osp
from .iplt import show_img_lis


def load_nusc_imgs(path_lis):
    map_ = dict(CAM_FRONT_LEFT=0, CAM_FRONT=1, CAM_FRONT_RIGHT=2,
                CAM_BACK_LEFT=3, CAM_BACK=4, CAM_BACK_RIGHT=5)
    img_lis = [0 for _ in range(len(map_))]
    for fpath in path_lis:
        img = Image.open(fpath)
        cam_name = osp.split(fpath)[-1].split('__')[1]
        img_lis[map_[cam_name]] = img
    return img_lis


def show_nusc_imgs(path_lis):
    img_lis = load_nusc_imgs(path_lis)
    fig = show_img_lis(img_lis)
    return fig


def show_nusc_imgs_dic(dic, data_root=None, mode='path', figsize=(7, 2)):
    map_ = dict(CAM_FRONT_LEFT=0, CAM_FRONT=1, CAM_FRONT_RIGHT=2,
                CAM_BACK_LEFT=3, CAM_BACK=4, CAM_BACK_RIGHT=5)
    
    img_dic = list()
    if mode == 'path':
        for name, path in dic.itmes():
            if data_root is not None:
                path = osp.join(data_root, path)
                img = Image.open(path)
            img_dic[name] = np.array(img, dtype=np.uint8)
    if mode == 'image':
        img_dic = dic
    
    # img_dic['CAM_BACK'] = np.fliplr(img_dic['CAM_BACK'])
    
    img_lis = [0 for _ in range(len(img_dic))]
    for name, img in img_dic.items():
        img_lis[map_[name]] = img
    show_img_lis(img_lis, figsize)
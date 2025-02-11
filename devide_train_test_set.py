# -*- coding: utf-8 -*-            
# @Author : luojincheng
# @Time : 2025/2/11 
目标是把分类数据集按照ratio比率划分为训练集和测试集
import os
import numpy as np
import shutil
from tqdm import tqdm

def devide_dataset(origin_dataset_path, destination_path, ratio=0.1):
    """
    origin_dataset_path:
    原始数据集路径,路径包含目录如下：
    dataset/
        cls1/
            file1
            file2
        cls2/
            file1
            file2
            ...
    destination_path
    
     dataset/
         train:
            cls1/
                file1
                file2
            cls2/
                file1
                file2
                ...
        test:
            cls1/
                file1
                file2
            cls2/
                file1
                file2
                ...
    """
    # 检查源数据集是否存在
    if not os.path.exists(origin_dataset_path):
        raise FileNotFoundError(f"Error: {origin_dataset_path} does not exist!")

    origin_cls_files = os.listdir(origin_dataset_path)
    if len(origin_cls_files) == 0:
        raise ValueError(f"Error: No class directories found in {origin_dataset_path}!")

    # 创建训练集和测试集目录
    test_path = os.path.join(destination_path, "test")
    os.makedirs(test_path, exist_ok=True)
    train_path = os.path.join(destination_path, "train")
    os.makedirs(train_path, exist_ok=True)

    print("Test path:", test_path)
    print("Train path:", train_path)

    # 遍历类别
    for cls_file in origin_cls_files:
        train_destination_cls = os.path.join(train_path, cls_file)
        os.makedirs(train_destination_cls, exist_ok=True)
        test_destination_cls = os.path.join(test_path, cls_file)
        os.makedirs(test_destination_cls, exist_ok=True)

        samples_files_path = os.path.join(origin_dataset_path, cls_file)
        samples_files = os.listdir(samples_files_path)

        if len(samples_files) == 0:
            print(f"Warning: {cls_file} has no files, skipping.")
            continue  # 跳过该类别

        pbar = tqdm(total=len(samples_files), desc=f"Processing {cls_file}")

        # 遍历当前类别的所有文件
        for sample_file in samples_files:
            sample_file_path = os.path.join(samples_files_path, sample_file)
            
            is_train = np.random.rand() > ratio  # 生成 0~1 之间的随机数
            if is_train:
                shutil.copy2(sample_file_path, train_destination_cls)
            else:
                shutil.copy2(sample_file_path, test_destination_cls)

            pbar.update(1)

        pbar.close()

if __name__ == "__main__":
    ratio = 0.1
    origin_dataset_path = "data/train/train_V1.0_all"
    destination_path = f"data/train/devide_{ratio}"
    devide_dataset(origin_dataset_path, destination_path, ratio)

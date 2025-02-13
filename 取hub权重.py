# -*- coding: utf-8 -*-            
# @Author : luojincheng
# @Time : 2025/2/13
import os
import shutil

#函数的目的是提取从huggingface下载的权重到一个完整的文件夹中，保持和hf 仓库中的versions一致，方便理解和使用
# 定义路径
snapshots_dir = "/.cache/huggingface/hub/datasets--argilla--synthetic-domain-text-classification/snapshots/a7175aa094c34ae66d1d8bd2695d969804cacae4/"
blobs_dir = "/.cache/huggingface/hub/datasets--argilla--synthetic-domain-text-classification/blobs/"
output_dir = "/kas_workspace/s_luojincheng_workspace/project/classification/add_cls_project/modernbert/synthetic-domain-text-classification"

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 遍历 snapshots 目录，处理所有链接
for root, _, files in os.walk(snapshots_dir):
    for file in files:
        snapshot_file_path = os.path.join(root, file)

        # 计算目标路径，保留目录结构
        relative_path = os.path.relpath(snapshot_file_path, snapshots_dir)
        target_path = os.path.join(output_dir, relative_path)

        # 确保目标目录存在
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        # 检查文件是否是软链接
        if os.path.islink(snapshot_file_path):
            # 获取指向的 blob 文件
            blob_link = os.readlink(snapshot_file_path)  # 链接内容
            blob_file_path = os.path.join(blobs_dir, os.path.basename(blob_link))

            # 确保 blob 文件存在
            if os.path.exists(blob_file_path):
                # 将 blob 文件复制到目标路径
                shutil.copy(blob_file_path, target_path)
                print(f"Recovered: {relative_path} -> {target_path}")
            else:
                print(f"Blob file missing: {blob_file_path}")
        else:
            # 如果不是链接，直接复制普通文件
            shutil.copy(snapshot_file_path, target_path)
            print(f"Copied: {relative_path}")

print("All files and directories recovered successfully!")

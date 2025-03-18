import os
import cv2
import ffmpeg
import numpy as np
from mtcnn import MTCNN
from mtcnn.utils.images import load_image
import tensorflow as tf
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import os
from imutils.face_utils import FaceAligner
from imutils.face_utils import rect_to_bb
import imutils
import dlib
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


# 输入视频目录和输出图像目录
video_path = "/data/DISFA/Videos_LeftCamera/"

# MTCNN人脸检测器
detector = MTCNN()
aligner = FaceAligner()

def extract_frames(video_path, output_dir):
    """使用ffmpeg提取视频的每一帧并保存为PNG"""
    cap = cv2.VideoCapture(video_path)
    # 获取视频信息
    fps = cap.get(cv2.CAP_PROP_FPS)         # 帧率
    frame_count_all = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 总帧数
    # duration = frame_count / fps            # 视频时长（秒）
    print(frame_count_all)

# 初始化 MTCNN
    detector = MTCNN(device="GPU")
    frame_count = 0

    # 遍历每一帧并用 tqdm 显示进度
    for i in tqdm(range(frame_count_all), desc="Processing video frames"):
        ret, frame = cap.read()
        # print("111111111")
        # 如果读取失败，视频结束
        if not ret:
            print(ret)
            break
        
        crop_frame=align_and_crop_faces(frame,detector)
        
        if crop_frame is None:
            print("没检测到人类的帧：",frame_count+1)
            print("路径：",video_path)
            frame_count += 1
            continue
        

        # 保存帧图像
        frame_filename = os.path.join(output_dir, f"{frame_count}.png")
        #{frame_count:04d}.png自动填充0,保证有4位
        cv2.imwrite(frame_filename, crop_frame)

        # 增加帧计数
        frame_count += 1

    # 释放视频文件资源
    cap.release()

def align_and_crop_faces(frame,detector):
    """用MTCNN对每一帧进行人脸检测、对齐和裁剪"""
    cv2.imwrite("data/DISFA/DISFA/temp_mtcnn.png", frame)
    # Load an image
    image = load_image("data/DISFA/DISFA/temp_mtcnn.png")

    # Detect faces in the image
    result = detector.detect_faces(image)
    if not result:
        print("原图检测不到人脸")
        return None
    
    crop_frame=crop(frame,result)
    aligned_face=align(crop_frame,detector)
    return aligned_face

def crop(frame,result):
    face = result[0]
    x, y, w, h = face['box']  # 人脸框
    cropped_face = frame[ y-50:y+h+50,x-50:x+w+50]
    return cropped_face
    
    
def align(crop_frame,detector,aligner=aligner):
 

# align_face=aligner.align(frame, result)
    """用人脸检测结果进行对齐"""
    
    # # 假设检测到至少一个人脸，选择第一个人脸
    # align_face=aligner.align(frame, result_pre)
    cv2.imwrite("data/DISFA/DISFA/temp_crop.png", crop_frame)#写入裁剪后的人脸
    image = load_image("data/DISFA/DISFA/temp_crop.png")#裁剪后的image
    result = detector.detect_faces(image)
    if not result:
        print("裁剪后无法检测到人脸")
        return None
    # last_frame=cv2.imread("data/DISFA/DISFA/temp_align.png")#读取裁剪后的image
    aligned_face=aligner.align(crop_frame, result)#用裁剪后的人脸做对齐
    
    cv2.imwrite("data/DISFA/DISFA/temp_align.png",aligned_face)#写入对齐后的人脸
    image1 = load_image("data/DISFA/DISFA/temp_align.png")
    result1 = detector.detect_faces(image1)
    if not result1:
        print("对齐后无法检测到人脸")
        return None
    
    face = result1[0]
    x, y, w, h = face['box']  # 人脸框
    cropped_aligned_face = aligned_face[ y:y+h+2,x:x+w+2]
    # if cropped_aligned_face == 0:
    #     print("Cropped face is empty, check the coordinates!")
    #     return None
    return resize_width_to_256(cropped_aligned_face)

def resize_width_to_256(image):
    # 获取原始宽高
    original_height, original_width = image.shape[:2]
    
    # 计算新的高度，保持宽度为 256
    new_width = 256
    new_height = int(original_height * (new_width / original_width))
    # print("111111111")
    # 调用 cv2.resize 进行等比例缩放
    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    return resized_image
    

def process_video(video_file):
    """处理每个视频：提取每一帧，进行人脸检测、裁剪，并保存图像"""
    # 创建每个视频对应的输出文件夹
    video_name = os.path.splitext(os.path.basename(video_file))[0]#不包含扩展
    match = re.search(r'SN\d{3}', video_name)
    video_output_dir = os.path.join("data/Datasets/DISFA/img/DISFA", match.group())
    print("111111111")
    os.makedirs(video_output_dir, exist_ok=True)
    # 提取视频帧
    extract_frames(video_file, video_output_dir)

# # 定义一个处理单个视频的函数
# def process_video(video_file):
#     print(f"正在处理视频：{video_file}")
#     # 在这里执行实际的视频处理逻辑
#     # 比如：提取帧、裁剪等操作
#     pass

# 主函数，多线程处理
def process_videos_multithread(video_files, max_threads=4):
    with ThreadPoolExecutor(max_threads) as executor:
        # 提交所有任务
        futures = {executor.submit(process_video, video_file): video_file for video_file in video_files}
        
        # 使用 tqdm 显示进度条
        for future in tqdm(as_completed(futures), total=len(futures)):
            video_file = futures[future]
            try:
                future.result()  # 获取线程执行结果（如果有异常会抛出）
            except Exception as e:
                print(f"处理视频 {video_file} 时出错：{e}")

if __name__ == "__main__":
    # 获取所有视频文件[16,18]
    video_files = [os.path.join(video_path, f) for f in os.listdir(video_path) if f.endswith('.avi')]
    path="data/DISFA/Videos_LeftCamera/LeftVideoSN018_comp.avi"
    process_video(path)
    
    # 对每个视频进行处理
    # for video_file in tqdm(video_files):
    #     print("正在处理视频：",video_file)
        # process_video(video_file)
        
        # 调用多线程函数
        # process_videos_multithread(video_files, max_threads=32)
        

    # # 裁剪对齐后的人脸区域
    # cropped_face = aligned_face[y:y+h, x:x+w]
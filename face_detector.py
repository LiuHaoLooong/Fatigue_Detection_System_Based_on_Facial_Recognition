"""
面部检测模块
使用MediaPipe Face Mesh进行面部特征点检测
"""

import cv2
import mediapipe as mp
import numpy as np


class FaceDetector:
    """
    面部检测器类
    使用MediaPipe Face Mesh检测面部特征点
    """
    
    def __init__(self):
        """
        初始化面部检测器
        """
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
    
    def process(self, img):
        """
        处理图像，检测面部特征点
        
        Args:
            img: 输入图像（BGR格式）
        
        Returns:
            results: MediaPipe Face Mesh检测结果
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(img_rgb)
        return results
    
    def draw_face_mesh(self, img, face_landmarks, draw=True):
        """
        绘制面部特征点网格
        
        Args:
            img: 输入图像
            face_landmarks: 面部特征点
            draw: 是否绘制（默认True）
        """
        if draw:
            self.mp_draw.draw_landmarks(
                image=img,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
            )
    
    def get_landmarks_array(self, face_landmarks, img_shape):
        """
        将MediaPipe特征点转换为numpy数组
        
        Args:
            face_landmarks: MediaPipe面部特征点
            img_shape: 图像形状 (h, w, c)
        
        Returns:
            landmarks: 特征点坐标数组 [[x1, y1], [x2, y2], ...]
        """
        h, w, c = img_shape
        landmarks = []
        for lm in face_landmarks.landmark:
            landmarks.append([lm.x * w, lm.y * h])
        return np.array(landmarks)

"""
工具函数模块
包含各种计算函数
"""

import numpy as np
import math
from config import LEFT_EYE_INDICES, RIGHT_EYE_INDICES, MOUTH_INDICES


def calculate_ear(eye_indices, landmarks):
    """
    计算眼睛纵横比（Eye Aspect Ratio）
    
    Args:
        eye_indices: 眼睛特征点索引列表
        landmarks: 所有面部特征点坐标
    
    Returns:
        ear: 眼睛纵横比
    """
    eye_points = np.array(eye_indices)
    
    # 计算垂直距离
    vertical1 = np.linalg.norm(landmarks[eye_points[1]] - landmarks[eye_points[5]])
    vertical2 = np.linalg.norm(landmarks[eye_points[2]] - landmarks[eye_points[4]])
    
    # 计算水平距离
    horizontal = np.linalg.norm(landmarks[eye_points[0]] - landmarks[eye_points[3]])
    
    # 计算眼睛纵横比
    ear = (vertical1 + vertical2) / (2.0 * horizontal)
    return ear


def calculate_mar(mouth_indices, landmarks):
    """
    计算嘴部纵横比（Mouth Aspect Ratio）
    
    Args:
        mouth_indices: 嘴部特征点索引列表
        landmarks: 所有面部特征点坐标
    
    Returns:
        mar: 嘴部纵横比
    """
    mouth_points = np.array(mouth_indices)
    
    # 计算垂直距离（上嘴唇到下嘴唇）
    vertical = np.linalg.norm(landmarks[mouth_points[0]] - landmarks[mouth_points[1]])
    
    # 计算水平距离（左嘴角到右嘴角）
    horizontal = np.linalg.norm(landmarks[mouth_points[2]] - landmarks[mouth_points[3]])
    
    # 计算嘴部纵横比
    mar = vertical / horizontal
    return mar


def get_eye_landmarks(landmarks):
    """
    获取左右眼睛的特征点坐标
    
    Args:
        landmarks: 所有面部特征点坐标
    
    Returns:
        left_eye_landmarks: 左眼特征点
        right_eye_landmarks: 右眼特征点
    """
    left_eye_landmarks = landmarks[LEFT_EYE_INDICES]
    right_eye_landmarks = landmarks[RIGHT_EYE_INDICES]
    
    return left_eye_landmarks, right_eye_landmarks


def get_mouth_landmarks(landmarks):
    """
    获取嘴部的特征点坐标
    
    Args:
        landmarks: 所有面部特征点坐标
    
    Returns:
        mouth_landmarks: 嘴部特征点
    """
    mouth_landmarks = landmarks[MOUTH_INDICES]
    return mouth_landmarks

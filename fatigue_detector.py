"""
疲劳检测模块
包含眨眼、打哈欠检测逻辑
"""

import time
import numpy as np
from collections import deque

import config
from utils import calculate_ear, calculate_mar, get_eye_landmarks, get_mouth_landmarks


class FatigueDetector:
    """
    疲劳检测器类
    检测眨眼、打哈欠等疲劳指标
    """
    
    def __init__(self):
        """
        初始化疲劳检测器
        """
        # 疲劳检测状态
        self.blink_counter = 0
        self.total_blinks = 0
        self.eye_closed_frames = 0
        self.yawn_counter = 0
        self.yawn_frames = 0
        
        # 历史记录
        self.blink_history = deque(maxlen=config.BLINK_HISTORY_LEN)
        self.ear_history = deque(maxlen=config.EAR_HISTORY_LEN)
        self.mar_history = deque(maxlen=config.MAR_HISTORY_LEN)
        
        # 状态标志
        self.is_fatigued = False
        self.is_yawning = False
        
        # 当前指标
        self.current_ear = 0.0
        self.current_mar = 0.0
    
    def detect(self, landmarks):
        """
        检测疲劳状态
        
        Args:
            landmarks: 面部特征点坐标数组
        """
        # 获取眼睛和嘴部特征点
        left_eye_landmarks, right_eye_landmarks = get_eye_landmarks(landmarks)
        mouth_landmarks = get_mouth_landmarks(landmarks)
        
        # 计算眼睛纵横比
        left_ear = calculate_ear(config.LEFT_EYE_INDICES, landmarks)
        right_ear = calculate_ear(config.RIGHT_EYE_INDICES, landmarks)
        self.current_ear = (left_ear + right_ear) / 2.0
        
        # 计算嘴部纵横比
        self.current_mar = calculate_mar(config.MOUTH_INDICES, landmarks)
        
        # 更新历史记录
        self.ear_history.append(self.current_ear)
        self.mar_history.append(self.current_mar)
        
        # 眨眼检测
        self._detect_blink()
        
        # 打哈欠检测
        self._detect_yawn()
    
    def _detect_blink(self):
        """
        检测眨眼
        """
        if self.current_ear < config.EAR_THRESHOLD:
            self.eye_closed_frames += 1
            self.is_fatigued = self.eye_closed_frames >= config.EYE_AR_CONSEC_FRAMES
        else:
            if self.eye_closed_frames > 0 and self.eye_closed_frames < config.EYE_AR_CONSEC_FRAMES:
                self.total_blinks += 1
                self.blink_history.append(time.time())
            self.eye_closed_frames = 0
            self.is_fatigued = False
    
    def _detect_yawn(self):
        """
        检测打哈欠
        """
        if self.current_mar > config.MOUTH_AR_THRESHOLD:
            self.yawn_frames += 1
            self.is_yawning = self.yawn_frames >= config.YAWN_CONSEC_FRAMES
        else:
            if self.yawn_frames > 0 and self.yawn_frames >= config.YAWN_CONSEC_FRAMES:
                self.yawn_counter += 1
            self.yawn_frames = 0
            self.is_yawning = False
    
    def get_blink_rate(self):
        """
        获取眨眼频率（每分钟）
        
        Returns:
            blink_rate: 眨眼频率（次/分钟）
        """
        if len(self.blink_history) > 1:
            time_span = self.blink_history[-1] - self.blink_history[0]
            if time_span > 0:
                return len(self.blink_history) / time_span * 60
        return 0.0
    
    def get_eye_closed_duration(self):
        """
        获取闭眼时长（秒）
        
        Returns:
            duration: 闭眼时长（秒）
        """
        if self.eye_closed_frames > 0:
            return self.eye_closed_frames / 30.0
        return 0.0
    
    def reset(self):
        """
        重置所有计数器和状态
        """
        self.blink_counter = 0
        self.total_blinks = 0
        self.eye_closed_frames = 0
        self.yawn_counter = 0
        self.yawn_frames = 0
        self.blink_history.clear()
        self.ear_history.clear()
        self.mar_history.clear()
        self.is_fatigued = False
        self.is_yawning = False

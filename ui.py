"""
UI绘制模块
负责绘制所有UI元素
"""

import cv2
import numpy as np

import config
from utils import get_eye_landmarks, get_mouth_landmarks
from fatigue_level import FatigueLevel


class UIDrawer:
    """
    UI绘制器类
    负责绘制眼睛、嘴部区域和状态面板
    """
    
    def __init__(self):
        """
        初始化UI绘制器
        """
        pass
    
    def draw_eye_region(self, img, landmarks, eye_indices, ear, label):
        """
        绘制眼睛区域
        
        Args:
            img: 输入图像
            landmarks: 面部特征点坐标数组
            eye_indices: 眼睛特征点索引
            ear: 眼睛纵横比
            label: 眼睛标签（Left/Right）
        """
        eye_points = landmarks[eye_indices]
        
        # 绘制眼睛轮廓
        for i in range(len(eye_points)):
            p1 = tuple(eye_points[i].astype(int))
            p2 = tuple(eye_points[(i + 1) % len(eye_points)].astype(int))
            cv2.line(img, p1, p2, config.COLOR_INFO, 2)
        
        # 绘制眼睛中心
        center = tuple(np.mean(eye_points, axis=0).astype(int))
        color = config.COLOR_WARNING if ear < config.EAR_THRESHOLD else config.COLOR_NORMAL
        cv2.circle(img, center, 5, color, -1)
        
        # 显示EAR值
        cv2.putText(img, f"{label} EAR: {ear:.2f}", 
                   (center[0] - 50, center[1] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    def draw_mouth_region(self, img, landmarks, mouth_indices, mar):
        """
        绘制嘴部区域
        
        Args:
            img: 输入图像
            landmarks: 面部特征点坐标数组
            mouth_indices: 嘴部特征点索引
            mar: 嘴部纵横比
        """
        mouth_points = landmarks[mouth_indices]
        
        # 绘制嘴部轮廓
        for i in range(len(mouth_points)):
            p1 = tuple(mouth_points[i].astype(int))
            p2 = tuple(mouth_points[(i + 1) % len(mouth_points)].astype(int))
            cv2.line(img, p1, p2, config.COLOR_INFO, 2)
        
        # 绘制嘴部中心
        center = tuple(np.mean(mouth_points, axis=0).astype(int))
        color = config.COLOR_WARNING if mar > config.MOUTH_AR_THRESHOLD else config.COLOR_NORMAL
        cv2.circle(img, center, 5, color, -1)
        
        # 显示MAR值
        cv2.putText(img, f"Mouth MAR: {mar:.2f}", 
                   (center[0] - 50, center[1] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    def draw_fatigue_level(self, img, fatigue_level, fatigue_score):
        """
        绘制疲劳等级
        
        Args:
            img: 输入图像
            fatigue_level: 疲劳等级
            fatigue_score: 疲劳评分（0-100）
        """
        # 获取疲劳等级颜色和名称
        color = fatigue_level.get_color()
        level_name = fatigue_level.get_name()
        progress = fatigue_level.get_progress()
        
        # 绘制疲劳等级面板背景
        panel_x = config.PANEL_X + config.PANEL_WIDTH + 10
        panel_y = config.PANEL_Y
        panel_w = config.FATIGUE_LEVEL_PANEL_WIDTH
        panel_h = config.FATIGUE_LEVEL_PANEL_HEIGHT
        
        cv2.rectangle(img, (panel_x, panel_y), 
                    (panel_x + panel_w, panel_y + panel_h), 
                    config.COLOR_PANEL_BG, -1)
        cv2.rectangle(img, (panel_x, panel_y), 
                    (panel_x + panel_w, panel_y + panel_h), 
                    color, 2)
        
        # 绘制疲劳等级文字
        cv2.putText(img, f"Fatigue Level: {level_name}", 
                   (panel_x + 10, panel_y + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # 绘制疲劳评分
        cv2.putText(img, f"Score: {fatigue_score}/100", 
                   (panel_x + 10, panel_y + 45),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, config.COLOR_PANEL_BORDER, 1)
        
        # 绘制进度条背景
        bar_x = config.FATIGUE_LEVEL_BAR_X
        bar_y = config.FATIGUE_LEVEL_BAR_Y
        bar_w = config.FATIGUE_LEVEL_BAR_WIDTH
        bar_h = config.FATIGUE_LEVEL_BAR_HEIGHT
        
        cv2.rectangle(img, (bar_x, bar_y), 
                    (bar_x + bar_w, bar_y + bar_h), 
                    (50, 50, 50), -1)
        
        # 绘制进度条
        filled_width = int(bar_w * progress)
        cv2.rectangle(img, (bar_x, bar_y), 
                    (bar_x + filled_width, bar_y + bar_h), 
                    color, -1)
        
        # 绘制进度条边框
        cv2.rectangle(img, (bar_x, bar_y), 
                    (bar_x + bar_w, bar_y + bar_h), 
                    config.COLOR_PANEL_BORDER, 1)
    
    def draw_status_panel(self, img, fatigue_detector, fatigue_level, fatigue_score):
        """
        绘制状态面板
        
        Args:
            img: 输入图像
            fatigue_detector: 疲劳检测器实例
            fatigue_level: 疲劳等级
            fatigue_score: 疲劳评分（0-100）
        """
        # 绘制面板背景
        cv2.rectangle(img, 
                   (config.PANEL_X, config.PANEL_Y), 
                   (config.PANEL_X + config.PANEL_WIDTH, config.PANEL_Y + config.PANEL_HEIGHT), 
                   config.COLOR_PANEL_BG, -1)
        cv2.rectangle(img, 
                   (config.PANEL_X, config.PANEL_Y), 
                   (config.PANEL_X + config.PANEL_WIDTH, config.PANEL_Y + config.PANEL_HEIGHT), 
                   config.COLOR_PANEL_BORDER, 2)
        
        # 状态信息
        y_offset = config.PANEL_Y + 30
        
        # 疲劳状态
        fatigue_color = config.COLOR_WARNING if fatigue_detector.is_fatigued else config.COLOR_NORMAL
        fatigue_text = "FATIGUE DETECTED!" if fatigue_detector.is_fatigued else "Normal"
        cv2.putText(img, f"Status: {fatigue_text}", 
                   (config.PANEL_X + 10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, fatigue_color, 2)
        y_offset += config.LINE_HEIGHT
        
        # 眨眼统计
        cv2.putText(img, f"Total Blinks: {fatigue_detector.total_blinks}", 
                   (config.PANEL_X + 10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, config.COLOR_PANEL_BORDER, 1)
        y_offset += config.LINE_HEIGHT
        
        # 打哈欠统计
        yawn_color = config.COLOR_WARNING if fatigue_detector.is_yawning else config.COLOR_PANEL_BORDER
        cv2.putText(img, f"Yawns: {fatigue_detector.yawn_counter}", 
                   (config.PANEL_X + 10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, yawn_color, 1)
        y_offset += config.LINE_HEIGHT
        
        # 眨眼频率（每分钟）
        blink_rate = fatigue_detector.get_blink_rate()
        cv2.putText(img, f"Blink Rate: {blink_rate:.1f}/min", 
                   (config.PANEL_X + 10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, config.COLOR_PANEL_BORDER, 1)
        y_offset += config.LINE_HEIGHT
        
        # 闭眼时长
        close_duration = fatigue_detector.get_eye_closed_duration()
        if close_duration > 0:
            cv2.putText(img, f"Eyes Closed: {close_duration:.1f}s", 
                       (config.PANEL_X + 10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, config.COLOR_PANEL_BORDER, 1)
            y_offset += config.LINE_HEIGHT
        
        # 当前指标
        cv2.putText(img, f"EAR: {fatigue_detector.current_ear:.3f}", 
                   (config.PANEL_X + 10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, config.COLOR_PANEL_BORDER, 1)
        y_offset += config.LINE_HEIGHT
        
        cv2.putText(img, f"MAR: {fatigue_detector.current_mar:.3f}", 
                   (config.PANEL_X + 10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, config.COLOR_PANEL_BORDER, 1)
    
    def draw_all(self, img, landmarks, fatigue_detector, fatigue_level=None, fatigue_score=0, draw_ui=True):
        """
        绘制所有UI元素
        
        Args:
            img: 输入图像
            landmarks: 面部特征点坐标数组
            fatigue_detector: 疲劳检测器实例
            fatigue_level: 疲劳等级（可选）
            fatigue_score: 疲劳评分（可选）
            draw_ui: 是否绘制UI（默认True）
        """
        if draw_ui:
            # 绘制眼睛区域
            left_eye_landmarks, right_eye_landmarks = get_eye_landmarks(landmarks)
            self.draw_eye_region(img, landmarks, config.LEFT_EYE_INDICES, 
                              fatigue_detector.current_ear, "Left")
            self.draw_eye_region(img, landmarks, config.RIGHT_EYE_INDICES, 
                              fatigue_detector.current_ear, "Right")
            
            # 绘制嘴部区域
            self.draw_mouth_region(img, landmarks, config.MOUTH_INDICES, 
                               fatigue_detector.current_mar)
            
            # 绘制疲劳等级
            if fatigue_level is not None:
                self.draw_fatigue_level(img, fatigue_level, fatigue_score)
            
            # 绘制状态面板
            self.draw_status_panel(img, fatigue_detector, fatigue_level, fatigue_score)

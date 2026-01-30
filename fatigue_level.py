"""
疲劳等级模块
综合多个指标计算疲劳等级
"""

from enum import Enum
import numpy as np

import config


class FatigueLevel(Enum):
    """
    疲劳等级枚举
    """
    NORMAL = 0      # 正常
    MILD = 1        # 轻度疲劳
    MODERATE = 2    # 中度疲劳
    SEVERE = 3      # 重度疲劳
    
    def get_color(self):
        """
        获取疲劳等级对应的颜色
        
        Returns:
            color: BGR颜色元组
        """
        color_map = {
            FatigueLevel.NORMAL: (0, 255, 0),      # 绿色
            FatigueLevel.MILD: (0, 255, 255),      # 黄色
            FatigueLevel.MODERATE: (0, 165, 255),  # 橙色
            FatigueLevel.SEVERE: (0, 0, 255)       # 红色
        }
        return color_map[self]
    
    def get_name(self):
        """
        获取疲劳等级名称
        
        Returns:
            name: 等级名称
        """
        name_map = {
            FatigueLevel.NORMAL: "Normal",
            FatigueLevel.MILD: "Mild Fatigue",
            FatigueLevel.MODERATE: "Moderate Fatigue",
            FatigueLevel.SEVERE: "Severe Fatigue"
        }
        return name_map[self]
    
    def get_progress(self):
        """
        获取疲劳进度（0-1）
        
        Returns:
            progress: 进度值
        """
        progress_map = {
            FatigueLevel.NORMAL: 0.0,
            FatigueLevel.MILD: 0.33,
            FatigueLevel.MODERATE: 0.67,
            FatigueLevel.SEVERE: 1.0
        }
        return progress_map[self]


class FatigueLevelCalculator:
    """
    疲劳等级计算器类
    综合多个指标计算疲劳等级
    """
    
    def __init__(self):
        """
        初始化疲劳等级计算器
        """
        # 权重配置
        self.blink_rate_weight = 0.45      # 眨眼频率权重
        self.yawn_count_weight = 0.35       # 打哈欠次数权重
        self.eye_closed_weight = 0.20       # 闭眼时长权重
        
        # 阈值配置
        self.blink_rate_threshold = 15.0    # 眨眼频率阈值（次/分钟）
        self.yawn_count_threshold = 3       # 打哈欠次数阈值
        self.eye_closed_threshold = 2.0     # 闭眼时长阈值（秒）
        
        # 历史数据
        self.history = []
        self.max_history_len = 100
    
    def calculate(self, fatigue_detector):
        """
        计算疲劳等级
        
        Args:
            fatigue_detector: 疲劳检测器实例
        
        Returns:
            fatigue_level: 疲劳等级
            fatigue_score: 疲劳评分（0-100）
        """
        # 获取各项指标
        blink_rate = fatigue_detector.get_blink_rate()
        yawn_count = fatigue_detector.yawn_counter
        eye_closed_duration = fatigue_detector.get_eye_closed_duration()
        
        # 计算各项得分（0-1）
        blink_score = self._calculate_blink_score(blink_rate)
        yawn_score = self._calculate_yawn_score(yawn_count)
        eye_closed_score = self._calculate_eye_closed_score(eye_closed_duration)
        
        # 加权计算综合得分
        total_score = (
            blink_score * self.blink_rate_weight +
            yawn_score * self.yawn_count_weight +
            eye_closed_score * self.eye_closed_weight
        )
        
        # 转换为0-100分制
        fatigue_score = int(total_score * 100)
        
        # 确定疲劳等级
        fatigue_level = self._determine_level(total_score)
        
        # 记录历史
        self.history.append({
            'score': fatigue_score,
            'level': fatigue_level,
            'blink_rate': blink_rate,
            'yawn_count': yawn_count,
            'eye_closed': eye_closed_duration
        })
        
        # 保持历史长度
        if len(self.history) > self.max_history_len:
            self.history.pop(0)
        
        return fatigue_level, fatigue_score
    
    def _calculate_blink_score(self, blink_rate):
        """
        计算眨眼频率得分
        
        Args:
            blink_rate: 眨眼频率（次/分钟）
        
        Returns:
            score: 得分（0-1）
        """
        if blink_rate < 5:
            return 0.0
        elif blink_rate < 10:
            return 0.2
        elif blink_rate < 15:
            return 0.5
        elif blink_rate < 20:
            return 0.7
        else:
            return 1.0
    
    def _calculate_yawn_score(self, yawn_count):
        """
        计算打哈欠得分
        
        Args:
            yawn_count: 打哈欠次数
        
        Returns:
            score: 得分（0-1）
        """
        if yawn_count == 0:
            return 0.0
        elif yawn_count < 2:
            return 0.3
        elif yawn_count < 4:
            return 0.6
        elif yawn_count < 6:
            return 0.8
        else:
            return 1.0
    
    def _calculate_eye_closed_score(self, eye_closed_duration):
        """
        计算闭眼时长得分
        
        Args:
            eye_closed_duration: 闭眼时长（秒）
        
        Returns:
            score: 得分（0-1）
        """
        if eye_closed_duration == 0:
            return 0.0
        elif eye_closed_duration < 1.0:
            return 0.3
        elif eye_closed_duration < 2.0:
            return 0.6
        elif eye_closed_duration < 3.0:
            return 0.8
        else:
            return 1.0
    
    def _determine_level(self, total_score):
        """
        根据综合得分确定疲劳等级
        
        Args:
            total_score: 综合得分（0-1）
        
        Returns:
            level: 疲劳等级
        """
        if total_score < 0.25:
            return FatigueLevel.NORMAL
        elif total_score < 0.5:
            return FatigueLevel.MILD
        elif total_score < 0.75:
            return FatigueLevel.MODERATE
        else:
            return FatigueLevel.SEVERE
    
    def get_average_score(self, window_size=30):
        """
        获取最近N次检测的平均得分
        
        Args:
            window_size: 窗口大小
        
        Returns:
            avg_score: 平均得分
        """
        if len(self.history) < window_size:
            return 0
        
        recent_history = self.history[-window_size:]
        scores = [h['score'] for h in recent_history]
        return sum(scores) / len(scores)
    
    def get_trend(self):
        """
        获取疲劳趋势
        
        Returns:
            trend: 趋势（'up', 'down', 'stable'）
        """
        if len(self.history) < 10:
            return 'stable'
        
        recent_scores = [h['score'] for h in self.history[-10:]]
        older_scores = [h['score'] for h in self.history[-20:-10]]
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)
        
        if recent_avg > older_avg + 10:
            return 'up'
        elif recent_avg < older_avg - 10:
            return 'down'
        else:
            return 'stable'
    
    def reset(self):
        """
        重置疲劳等级计算器
        """
        self.history.clear()

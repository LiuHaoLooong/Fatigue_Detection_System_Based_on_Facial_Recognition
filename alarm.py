"""
警报模块
处理疲劳状态的声音警报
"""

import time
import threading
import winsound

import config


class AlarmManager:
    """
    警报管理器类
    负责在检测到疲劳状态时发出声音警报
    """
    
    def __init__(self):
        """
        初始化警报管理器
        """
        self.last_alarm_time = 0
        self.alarm_cooldown = config.ALARM_COOLDOWN
        self.alarm_enabled = True
    
    def check_and_trigger(self, is_fatigued, is_yawning):
        """
        检查是否需要发出警报
        
        Args:
            is_fatigued: 是否检测到疲劳
            is_yawning: 是否检测到打哈欠
        
        Returns:
            should_alarm: 是否应该发出警报
        """
        current_time = time.time()
        
        # 检查是否需要发出警报
        if (is_fatigued or is_yawning) and \
           (current_time - self.last_alarm_time > self.alarm_cooldown) and \
           self.alarm_enabled:
            
            # 发出警报
            self._play_alarm()
            self.last_alarm_time = current_time
            return True
        
        return False
    
    def _play_alarm(self):
        """
        播放警报声音（在独立线程中运行）
        """
        try:
            threading.Thread(target=self._beep, daemon=True).start()
        except Exception as e:
            print(f"Error playing alarm: {e}")
    
    def _beep(self):
        """
        播放蜂鸣声
        """
        try:
            winsound.Beep(1000, 500)  # 频率1000Hz，持续500ms
        except Exception as e:
            print(f"Error in beep: {e}")
    
    def enable(self):
        """
        启用警报
        """
        self.alarm_enabled = True
        print("Alarm enabled")
    
    def disable(self):
        """
        禁用警报
        """
        self.alarm_enabled = False
        print("Alarm disabled")
    
    def set_cooldown(self, cooldown):
        """
        设置警报冷却时间
        
        Args:
            cooldown: 冷却时间（秒）
        """
        self.alarm_cooldown = cooldown
        print(f"Alarm cooldown set to {cooldown} seconds")
    
    def reset(self):
        """
        重置警报状态
        """
        self.last_alarm_time = 0
        print("Alarm reset")

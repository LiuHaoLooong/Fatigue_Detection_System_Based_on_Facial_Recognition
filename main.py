"""
疲劳检测系统 - 主程序
整合所有模块，实现完整的疲劳检测功能
"""

import cv2
import time
import sys
import argparse

import config
from face_detector import FaceDetector
from fatigue_detector import FatigueDetector
from fatigue_level import FatigueLevelCalculator
from alarm import AlarmManager
from ui import UIDrawer
from web_server import web_server


class FatigueDetectionSystem:
    """
    疲劳检测系统主类
    整合所有功能模块
    """
    
    def __init__(self, use_web=False):
        """
        初始化疲劳检测系统
        """
        self.face_detector = FaceDetector()
        self.fatigue_detector = FatigueDetector()
        self.fatigue_level_calculator = FatigueLevelCalculator()
        self.alarm_manager = AlarmManager()
        self.ui_drawer = UIDrawer()
        self.use_web = use_web
        
        self.cap = None
        self.running = False
        self.frame_count = 0
        self.start_time = 0
        self.current_fatigue_level = None
        self.current_fatigue_score = 0
    
    def initialize_camera(self):
        """
        初始化摄像头
        """
        print("Step 1: Initializing camera...")
        self.cap = cv2.VideoCapture(config.CAMERA_INDEX)
        self.cap.set(3, config.CAMERA_WIDTH)
        self.cap.set(4, config.CAMERA_HEIGHT)
        
        if not self.cap.isOpened():
            print("Error: Cannot open camera")
            print("Please check:")
            print("1. Camera is connected")
            print("2. Camera is not being used by another application")
            print("3. Camera permissions are granted")
            return False
        
        print("Camera initialized successfully")
        
        # 测试读取一帧
        print("Step 2: Testing camera frame...")
        test_success, test_img = self.cap.read()
        if not test_success:
            print("Error: Cannot read camera frame")
            self.cap.release()
            return False
        
        print("Camera frame test successful")
        return True
    
    def process_frame(self, img):
        """
        处理单帧图像

        """
        # 检测面部特征点
        results = self.face_detector.process(img)
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # 转换特征点坐标
                landmarks = self.face_detector.get_landmarks_array(
                    face_landmarks, img.shape
                )
                
                # 检测疲劳状态
                self.fatigue_detector.detect(landmarks)
                
                # 计算疲劳等级
                self.current_fatigue_level, self.current_fatigue_score = \
                    self.fatigue_level_calculator.calculate(self.fatigue_detector)
                
                # 更新Web服务器数据
                if self.use_web:
                    web_server.update_frame(img)
                    web_server.update_fatigue_data(
                        self.fatigue_detector,
                        self.current_fatigue_level,
                        self.current_fatigue_score
                    )
                
                # 绘制面部特征点网格（始终绘制以体现识别效果）
                self.face_detector.draw_face_mesh(img, face_landmarks, draw=True)
                
                # 绘制UI（Web模式下不绘制）
                self.ui_drawer.draw_all(img, landmarks, self.fatigue_detector, 
                                   self.current_fatigue_level, self.current_fatigue_score,
                                   draw_ui=not self.use_web)
                
                # 检查是否需要发出警报
                self.alarm_manager.check_and_trigger(
                    self.fatigue_detector.is_fatigued,
                    self.fatigue_detector.is_yawning
                )
        
        return img
    
    def run(self):
        """
        运行疲劳检测系统
        """
        if not self.initialize_camera():
            input("\nPress Enter to exit...")
            return
        
        if self.use_web:
            web_server.start()
            print("\nFatigue Detection System (Web Mode)")
            print("=" * 50)
            print("Web server started at http://localhost:5000")
            print("Open the URL in your browser to view the interface")
            print("\nPress 'q' to exit")
            print("=" * 50)
        else:
            print("\nFatigue Detection System")
            print("=" * 50)
            print("Features:")
            print("- Eye blink detection")
            print("- Yawn detection")
            print("- Head pose detection")
            print("- Fatigue alarm")
            print("\nPress 'q' to exit")
            print("\nStarting camera feed...")
            print("=" * 50)
        
        self.running = True
        self.frame_count = 0
        self.start_time = time.time()
        
        try:
            while self.running:
                success, img = self.cap.read()
                if not success:
                    print(f"Error: Cannot read camera frame at frame {self.frame_count}")
                    time.sleep(0.1)
                    continue
                
                self.frame_count += 1
                
                # 翻转图像（镜像效果）
                img = cv2.flip(img, 1)
                
                # 处理帧
                try:
                    img = self.process_frame(img)
                except Exception as e:
                    print(f"Error in detection at frame {self.frame_count}: {e}")
                    continue
                
                # 在非Web模式下显示画面
                if not self.use_web:
                    cv2.imshow('Fatigue Detection System', img)
                    
                    # 处理键盘输入
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        print("\nUser requested to quit")
                        self.running = False
                else:
                    # Web模式下，检查是否有键盘输入
                    import msvcrt
                    if msvcrt.kbhit():
                        key = msvcrt.getch()
                        if key == b'q':
                            print("\nUser requested to quit")
                            self.running = False
        
        except KeyboardInterrupt:
            print("\nProgram interrupted by user")
        except Exception as e:
            print(f"\nError during execution: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """
        清理资源
        """
        print("\nCleaning up...")
        
        if self.use_web:
            web_server.stop()
        
        if self.cap is not None:
            self.cap.release()
        
        cv2.destroyAllWindows()
        
        elapsed = time.time() - self.start_time
        print(f"Total frames processed: {self.frame_count}")
        print(f"Total time: {elapsed:.1f}s")
        print(f"Average FPS: {self.frame_count / elapsed:.1f}")
        print("Program terminated")


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='疲劳检测系统')
    parser.add_argument('--web', action='store_true', 
                       help='使用Web界面模式（默认为桌面界面模式）')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                       help='Web服务器地址（默认：0.0.0.0）')
    parser.add_argument('--port', type=int, default=5000,
                       help='Web服务器端口（默认：5000）')
    
    args = parser.parse_args()
    
    print("Initializing Fatigue Detection System...")
    print("=" * 50)
    
    if args.web:
        print(f"Mode: Web Interface")
        print(f"Server: http://{args.host}:{args.port}")
        web_server.host = args.host
        web_server.port = args.port
    else:
        print("Mode: Desktop Interface")
    
    print("=" * 50)
    
    try:
        system = FatigueDetectionSystem(use_web=args.web)
        system.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()

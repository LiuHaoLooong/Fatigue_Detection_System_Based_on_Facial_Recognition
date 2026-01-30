import cv2
import mediapipe as mp
import numpy as np
import time
import math
import threading
import winsound
from collections import deque

# 眼睛纵横比阈值
EAR_THRESHOLD = 0.15
# 连续闭眼帧数阈值（约2秒）
EYE_AR_CONSEC_FRAMES = 60
# 嘴部张开阈值
MOUTH_AR_THRESHOLD = 0.65
# 连续打哈欠帧数阈值（约2秒）
YAWN_CONSEC_FRAMES = 45
# 低头角度阈值
HEAD_TILT_THRESHOLD = 30

class FaceDetector:
    def __init__(self):
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
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(img_rgb)
        return results

def calculate_ear(eye_points, landmarks):
    eye_points = np.array(eye_points)
    
    # 计算垂直距离
    vertical1 = np.linalg.norm(landmarks[eye_points[1]] - landmarks[eye_points[5]])
    vertical2 = np.linalg.norm(landmarks[eye_points[2]] - landmarks[eye_points[4]])
    
    # 计算水平距离
    horizontal = np.linalg.norm(landmarks[eye_points[0]] - landmarks[eye_points[3]])
    
    # 计算眼睛纵横比
    ear = (vertical1 + vertical2) / (2.0 * horizontal)
    return ear

def calculate_mar(mouth_points, landmarks):
    mouth_points = np.array(mouth_points)
    
    # 计算垂直距离（上嘴唇到下嘴唇）
    vertical = np.linalg.norm(landmarks[mouth_points[0]] - landmarks[mouth_points[1]])
    
    # 计算水平距离（左嘴角到右嘴角）
    horizontal = np.linalg.norm(landmarks[mouth_points[2]] - landmarks[mouth_points[3]])
    
    # 计算嘴部纵横比
    mar = vertical / horizontal
    return mar

def calculate_head_tilt(landmarks):
    # 使用鼻子、左眼、右眼计算头部倾斜角度
    nose = landmarks[1]
    left_eye = landmarks[33]
    right_eye = landmarks[263]
    
    # 计算两眼之间的向量
    eye_vector = right_eye - left_eye
    
    # 计算水平角度
    angle = math.degrees(math.atan2(eye_vector[1], eye_vector[0]))
    
    return angle

def play_alarm():
    try:
        winsound.Beep(1000, 500)
    except:
        pass

class FatigueDetector:
    def __init__(self):
        self.detector = FaceDetector()
        
        # 疲劳检测状态
        self.blink_counter = 0
        self.total_blinks = 0
        self.eye_closed_frames = 0
        self.yawn_counter = 0
        self.yawn_frames = 0
        self.head_tilt_frames = 0
        
        # 历史记录
        self.blink_history = deque(maxlen=100)
        self.ear_history = deque(maxlen=30)
        self.mar_history = deque(maxlen=30)
        
        # 警报状态
        self.last_alarm_time = 0
        self.alarm_cooldown = 2.0
        
        # 状态标志
        self.is_fatigued = False
        self.is_yawning = False
        self.is_head_down = False
    
    def detect(self, img):
        results = self.detector.process(img)
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # 转换特征点坐标
                h, w, c = img.shape
                landmarks = []
                for lm in face_landmarks.landmark:
                    landmarks.append([lm.x * w, lm.y * h])
                landmarks = np.array(landmarks)
                
                # 左眼特征点索引
                left_eye_indices = [33, 160, 158, 133, 153, 144]
                # 右眼特征点索引
                right_eye_indices = [362, 385, 387, 263, 373, 380]
                # 嘴部特征点索引（上唇、下唇、左嘴角、右嘴角）
                mouth_indices = [13, 14, 61, 291]
                
                # 计算眼睛纵横比
                left_ear = calculate_ear(left_eye_indices, landmarks)
                right_ear = calculate_ear(right_eye_indices, landmarks)
                avg_ear = (left_ear + right_ear) / 2.0
                
                # 计算嘴部纵横比
                mar = calculate_mar(mouth_indices, landmarks)
                
                # 计算头部倾斜角度
                head_tilt = calculate_head_tilt(landmarks)
                
                # 更新历史记录
                self.ear_history.append(avg_ear)
                self.mar_history.append(mar)
                
                # 眨眼检测
                if avg_ear < EAR_THRESHOLD:
                    self.eye_closed_frames += 1
                    self.is_fatigued = self.eye_closed_frames >= EYE_AR_CONSEC_FRAMES
                else:
                    if self.eye_closed_frames > 0 and self.eye_closed_frames < EYE_AR_CONSEC_FRAMES:
                        self.total_blinks += 1
                        self.blink_history.append(time.time())
                    self.eye_closed_frames = 0
                    self.is_fatigued = False
                
                # 打哈欠检测
                if mar > MOUTH_AR_THRESHOLD:
                    self.yawn_frames += 1
                    self.is_yawning = self.yawn_frames >= YAWN_CONSEC_FRAMES
                else:
                    if self.yawn_frames > 0 and self.yawn_frames >= YAWN_CONSEC_FRAMES:
                        self.yawn_counter += 1
                    self.yawn_frames = 0
                    self.is_yawning = False
                
                # 头部姿态检测
                if abs(head_tilt) > HEAD_TILT_THRESHOLD:
                    self.head_tilt_frames += 1
                    self.is_head_down = self.head_tilt_frames >= 30
                else:
                    self.head_tilt_frames = 0
                    self.is_head_down = False
                
                # 绘制面部特征点
                self.draw_face_landmarks(img, face_landmarks)
                
                # 绘制眼睛和嘴部区域
                self.draw_eye_region(img, landmarks, left_eye_indices, left_ear, "Left")
                self.draw_eye_region(img, landmarks, right_eye_indices, right_ear, "Right")
                self.draw_mouth_region(img, landmarks, mouth_indices, mar)
                
                # 绘制状态信息
                self.draw_status(img)
                
                # 检查是否需要发出警报
                self.check_alarm()
        
        return img
    
    def draw_face_landmarks(self, img, face_landmarks):
        mp.solutions.drawing_utils.draw_landmarks(
            image=img,
            landmark_list=face_landmarks,
            connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_tesselation_style()
        )
    
    def draw_eye_region(self, img, landmarks, eye_indices, ear, label):
        eye_points = landmarks[eye_indices]
        
        # 绘制眼睛轮廓
        for i in range(len(eye_points)):
            p1 = tuple(eye_points[i].astype(int))
            p2 = tuple(eye_points[(i + 1) % len(eye_points)].astype(int))
            cv2.line(img, p1, p2, (0, 255, 255), 2)
        
        # 绘制眼睛中心
        center = tuple(np.mean(eye_points, axis=0).astype(int))
        color = (0, 0, 255) if ear < EAR_THRESHOLD else (0, 255, 0)
        cv2.circle(img, center, 5, color, -1)
        
        # 显示EAR值
        cv2.putText(img, f"{label} EAR: {ear:.2f}", 
                   (center[0] - 50, center[1] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    def draw_mouth_region(self, img, landmarks, mouth_indices, mar):
        mouth_points = landmarks[mouth_indices]
        
        # 绘制嘴部轮廓
        for i in range(len(mouth_points)):
            p1 = tuple(mouth_points[i].astype(int))
            p2 = tuple(mouth_points[(i + 1) % len(mouth_points)].astype(int))
            cv2.line(img, p1, p2, (0, 255, 255), 2)
        
        # 绘制嘴部中心
        center = tuple(np.mean(mouth_points, axis=0).astype(int))
        color = (0, 0, 255) if mar > MOUTH_AR_THRESHOLD else (0, 255, 0)
        cv2.circle(img, center, 5, color, -1)
        
        # 显示MAR值
        cv2.putText(img, f"Mouth MAR: {mar:.2f}", 
                   (center[0] - 50, center[1] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    def draw_status(self, img):
        h, w = img.shape[:2]
        
        # 绘制状态面板
        panel_x, panel_y = 10, 10
        panel_w, panel_h = 300, 200
        cv2.rectangle(img, (panel_x, panel_y), 
                    (panel_x + panel_w, panel_y + panel_h), 
                    (0, 0, 0), -1)
        cv2.rectangle(img, (panel_x, panel_y), 
                    (panel_x + panel_w, panel_y + panel_h), 
                    (255, 255, 255), 2)
        
        # 状态信息
        y_offset = 30
        line_height = 25
        
        # 疲劳状态
        fatigue_color = (0, 0, 255) if self.is_fatigued else (0, 255, 0)
        fatigue_text = "FATIGUE DETECTED!" if self.is_fatigued else "Normal"
        cv2.putText(img, f"Status: {fatigue_text}", 
                   (panel_x + 10, panel_y + y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, fatigue_color, 2)
        y_offset += line_height
        
        # 眨眼统计
        cv2.putText(img, f"Total Blinks: {self.total_blinks}", 
                   (panel_x + 10, panel_y + y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += line_height
        
        # 打哈欠统计
        yawn_color = (0, 0, 255) if self.is_yawning else (255, 255, 255)
        cv2.putText(img, f"Yawns: {self.yawn_counter}", 
                   (panel_x + 10, panel_y + y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, yawn_color, 1)
        y_offset += line_height
        
        # 头部姿态
        head_color = (0, 0, 255) if self.is_head_down else (255, 255, 255)
        head_text = "Head Down!" if self.is_head_down else "Head Normal"
        cv2.putText(img, f"Head: {head_text}", 
                   (panel_x + 10, panel_y + y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, head_color, 1)
        y_offset += line_height
        
        # 眨眼频率（每分钟）
        if len(self.blink_history) > 1:
            time_span = self.blink_history[-1] - self.blink_history[0]
            if time_span > 0:
                blink_rate = len(self.blink_history) / time_span * 60
                cv2.putText(img, f"Blink Rate: {blink_rate:.1f}/min", 
                           (panel_x + 10, panel_y + y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += line_height
        
        # 闭眼时长
        if self.eye_closed_frames > 0:
            close_duration = self.eye_closed_frames / 30.0
            cv2.putText(img, f"Eyes Closed: {close_duration:.1f}s", 
                       (panel_x + 10, panel_y + y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def check_alarm(self):
        current_time = time.time()
        
        # 检查是否需要发出警报
        if (self.is_fatigued or self.is_yawning or self.is_head_down) and \
           (current_time - self.last_alarm_time > self.alarm_cooldown):
            threading.Thread(target=play_alarm, daemon=True).start()
            self.last_alarm_time = current_time

def main():
    print("Initializing Fatigue Detection System...")
    print("=" * 50)
    
    # 初始化摄像头
    print("Step 1: Initializing camera...")
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    
    if not cap.isOpened():
        print("Error: Cannot open camera")
        print("Please check:")
        print("1. Camera is connected")
        print("2. Camera is not being used by another application")
        print("3. Camera permissions are granted")
        input("Press Enter to exit...")
        return
    
    print("Camera initialized successfully")
    
    # 测试读取一帧
    print("Step 2: Testing camera frame...")
    test_success, test_img = cap.read()
    if not test_success:
        print("Error: Cannot read camera frame")
        cap.release()
        input("Press Enter to exit...")
        return
    print("Camera frame test successful")
    
    # 初始化疲劳检测器
    print("Step 3: Initializing fatigue detector...")
    try:
        detector = FatigueDetector()
        print("Fatigue detector initialized successfully")
    except Exception as e:
        print(f"Error initializing fatigue detector: {e}")
        import traceback
        traceback.print_exc()
        cap.release()
        input("Press Enter to exit...")
        return
    
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
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            success, img = cap.read()
            if not success:
                print(f"Error: Cannot read camera frame at frame {frame_count}")
                time.sleep(0.1)
                continue
            
            frame_count += 1
            
            # 每30帧输出一次状态
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"Running... Frame: {frame_count}, FPS: {fps:.1f}")
            
            # 翻转图像（镜像效果）
            img = cv2.flip(img, 1)
            
            # 检测疲劳
            try:
                img = detector.detect(img)
            except Exception as e:
                print(f"Error in detection at frame {frame_count}: {e}")
                continue
            
            # 显示画面
            cv2.imshow('Fatigue Detection System', img)
            
            # 处理键盘输入
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nUser requested to quit")
                break
    
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"\nError during execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nCleaning up...")
        elapsed = time.time() - start_time
        print(f"Total frames processed: {frame_count}")
        print(f"Total time: {elapsed:.1f}s")
        print(f"Average FPS: {frame_count / elapsed:.1f}")
        
        cap.release()
        cv2.destroyAllWindows()
        print("Program terminated")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()

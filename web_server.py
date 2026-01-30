"""
Web服务器模块
提供Web界面显示疲劳检测系统的实时数据
"""

from flask import Flask, render_template, Response, jsonify
import cv2
import base64
import threading
import time
import json

app = Flask(__name__)

class WebServer:
    """
    Web服务器类
    提供Web界面和实时数据传输
    """
    
    def __init__(self, host='0.0.0.0', port=5000):
        """
        初始化Web服务器
        
        Args:
            host: 服务器地址
            port: 服务器端口
        """
        self.host = host
        self.port = port
        self.current_frame = None
        self.fatigue_data = {
            'fatigue_level': 'Normal',
            'fatigue_score': 0,
            'total_blinks': 0,
            'yawn_count': 0,
            'is_fatigued': False,
            'is_yawning': False,
            'blink_rate': 0.0,
            'eye_closed_duration': 0.0,
            'ear': 0.0,
            'mar': 0.0,
            'runtime': '00:00:00',
            'fps': 0
        }
        self.running = False
        self.server_thread = None
        self.start_time = None
        self.frame_count = 0
    
    def update_frame(self, frame):
        """
        更新当前帧
        
        Args:
            frame: 当前帧图像
        """
        self.current_frame = frame
    
    def update_fatigue_data(self, fatigue_detector, fatigue_level, fatigue_score):
        """
        更新疲劳数据
        
        Args:
            fatigue_detector: 疲劳检测器实例
            fatigue_level: 疲劳等级
            fatigue_score: 疲劳评分
        """
        level_name = fatigue_level.get_name() if fatigue_level else 'Normal'
        
        # 计算运行时间
        if self.start_time is None:
            self.start_time = time.time()
        self.frame_count += 1
        
        elapsed = time.time() - self.start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        runtime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # 计算FPS
        if elapsed > 0:
            fps = self.frame_count / elapsed
        else:
            fps = 0
        
        self.fatigue_data = {
            'fatigue_level': level_name,
            'fatigue_score': fatigue_score,
            'total_blinks': fatigue_detector.total_blinks,
            'yawn_count': fatigue_detector.yawn_counter,
            'is_fatigued': fatigue_detector.is_fatigued,
            'is_yawning': fatigue_detector.is_yawning,
            'blink_rate': fatigue_detector.get_blink_rate(),
            'eye_closed_duration': fatigue_detector.get_eye_closed_duration(),
            'ear': fatigue_detector.current_ear,
            'mar': fatigue_detector.current_mar,
            'runtime': runtime,
            'fps': round(fps, 1)
        }
    
    def start(self):
        """
        启动Web服务器
        """
        if self.running:
            return
        
        self.running = True
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        print(f"Web server started at http://{self.host}:{self.port}")
    
    def stop(self):
        """
        停止Web服务器
        """
        self.running = False
    
    def _run_server(self):
        """
        运行Web服务器（内部方法）
        """
        app.run(host=self.host, port=self.port, debug=False, use_reloader=False)


@app.route('/')
def index():
    """
    主页路由
    """
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """
    视频流路由
    """
    def generate():
        while True:
            if web_server.current_frame is not None:
                ret, buffer = cv2.imencode('.jpg', web_server.current_frame, 
                                          [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                if ret:
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.033)
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/fatigue_data')
def get_fatigue_data():
    """
    获取疲劳数据API
    """
    return jsonify(web_server.fatigue_data)


web_server = WebServer()

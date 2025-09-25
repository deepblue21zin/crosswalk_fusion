#안녕하세용 이상윤입니당
# visualization.py
"""원본 mmw_demo_run_2.py의 MyWidget 클래스 - 디버깅 개선"""

import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
from data_processing import readAndParseData14xx
import serial_functions
import numpy as np


class MyWidget(pg.GraphicsLayoutWidget):
    """원본 MyWidget 클래스 - 디버깅 개선"""
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)  # 100ms 간격
        self.timer.timeout.connect(self.onNewData)
        self.timer.start()
        
        self.plotItem = self.addPlot(title="Radar points (x vs y)")
        self.plotItem.setLabel('bottom', 'x [m]')
        self.plotItem.setLabel('left', 'y [m]')
        self.plotItem.showGrid(x=True, y=True, alpha=0.3)
        self.plotItem.enableAutoRange('xy', True)
        
        # 플롯 범위 설정 (더 넓게)
        self.plotItem.setXRange(-5, 5)
        self.plotItem.setYRange(0, 10)
        
        self.plotDataItem = self.plotItem.plot([], [], pen=None,
                                               symbol='o', symbolSize=8,  # 크기 증가
                                               symbolBrush=(255, 0, 0), symbolPen=None)
        
        self.frame_count = 0
        self.detection_count = 0

    def setData(self, x, y):
        """데이터 검증 후 설정"""
        if len(x) > 0 and len(y) > 0:
            print(f"[PLOT] Plotting {len(x)} points")
            self.plotDataItem.setData(x, y)
            self.detection_count += 1
        else:
            print("[PLOT] No points to plot")
            # 빈 데이터일 때는 이전 점들을 유지 (지우지 않음)

    def onNewData(self):
        """데이터 업데이트 - 디버깅 강화"""
        if serial_functions.Dataport is None:
            print("[DEBUG] Dataport is None")
            return
            
        self.frame_count += 1
        
        try:
            ok, frame_no, det = readAndParseData14xx(serial_functions.Dataport)
            
            if ok:
                x_data = det.get("x", [])
                y_data = det.get("y", [])
                num_objects = det.get("numObj", 0)
                
                print(f"[FRAME {self.frame_count}] Frame#{frame_no}, Objects: {num_objects}")
                
                if num_objects > 0 and len(x_data) > 0:
                    print(f"[DATA] X: {x_data[:3]}... Y: {y_data[:3]}...")  # 처음 3개만 출력
                    self.setData(x_data, y_data)
                else:
                    print("[DATA] No objects detected")
                    
                # 10초마다 통계 출력
                if self.frame_count % 100 == 0:
                    print(f"[STATS] Frames: {self.frame_count}, Detections: {self.detection_count}")
                    
            else:
                if self.frame_count % 50 == 0:  # 가끔씩만 출력
                    print(f"[DEBUG] No valid frame at count {self.frame_count}")
                    
        except Exception as e:
            print(f"[ERROR] Exception in onNewData: {e}")
            import traceback
            traceback.print_exc()
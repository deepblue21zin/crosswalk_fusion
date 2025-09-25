# main.py
"""원본 mmw_demo_run_2.py의 main 함수 - 단순히 import만 변경"""

import argparse
from PyQt5 import QtWidgets
import pyqtgraph as pg
import serial_functions  # 모듈 전체를 import
import data_processing
from visualization import MyWidget
from cli_functions import _wait_cli


def main():
    """원본 main 함수 그대로 복사 - import만 변경됨"""
    ap = argparse.ArgumentParser(description="TI mmWave cfg runner + live point cloud plotter (robust)")
    ap.add_argument('--cli-port', required=True, help='CLI serial port (e.g., COM7)')
    ap.add_argument('--data-port', help='DATA serial port (e.g., COM8). If omitted, auto-detect near CLI.')
    ap.add_argument('--cfg', required=True, help='Path to cfg file')
    ap.add_argument('--line-delay-ms', type=int, default=80, help='Delay after each cfg line write (ms)')
    ap.add_argument('--char-delay-ms', type=int, default=3, help='Delay between chars when writing cfg (ms)')
    ap.add_argument('--echo', action='store_true', help='Echo CLI responses during cfg send')
    ap.add_argument('--debug', action='store_true', help='Verbose parser debug')
    args = ap.parse_args()

    # 전역 DEBUG 설정
    data_processing.DEBUG = args.debug

    try:
        serial_functions.serialConfig(args)  # 모듈명.함수명으로 호출
    except Exception as e:
        print(f"[FATAL] serialConfig 실패: {e}")
        return

    app = QtWidgets.QApplication([])
    pg.setConfigOptions(antialias=False)
    win = MyWidget()
    win.resize(800, 600)
    win.setWindowTitle("mmWave Live Points (robust)")
    win.show()

    try:
        app.exec_()
    finally:
        try:
            if serial_functions.CLIport and serial_functions.CLIport.is_open:
                serial_functions.CLIport.write(b'sensorStop\r\n')
                _wait_cli(serial_functions.CLIport, timeout=2.0, echo=False)
        except: 
            pass
        try:
            if serial_functions.CLIport and serial_functions.CLIport.is_open: 
                serial_functions.CLIport.close()
        except: 
            pass
        try:
            if serial_functions.Dataport and serial_functions.Dataport.is_open: 
                serial_functions.Dataport.close()
        except: 
            pass


if __name__ == "__main__":
    main()
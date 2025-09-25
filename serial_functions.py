# serial_functions.py
"""원본 mmw_demo_run_2.py의 시리얼 설정 함수들"""

import serial
from typing import Optional
from port_utils import pick_dataport
from cli_functions import send_cfg


# 원본 전역변수들
CLIport: Optional[serial.Serial] = None
Dataport: Optional[serial.Serial] = None


def serialConfig(args):
    """원본 serialConfig 함수 그대로 복사"""
    global CLIport, Dataport
    if not args.cli_port:
        raise RuntimeError("CLI 포트를 지정하세요. (--cli-port COMx)")
    CLIport = serial.Serial(args.cli_port, 115200, timeout=0.2, write_timeout=1.0)
    data_name = args.data_port or pick_dataport(args.cli_port, preferred=None)
    if not data_name:
        CLIport.close()
        raise RuntimeError("DATA 포트를 찾지 못했습니다. --data-port 로 지정하거나 보드 모드/연결을 확인하세요.")
    Dataport = serial.Serial(data_name, 921600, timeout=0.05, write_timeout=0.5)
    print(f"[INFO] CLI  port -> {args.cli_port} @115200")
    print(f"[INFO] DATA port -> {data_name} @921600")
    send_cfg(CLIport, args.cfg,
             line_delay_ms=args.line_delay_ms,
             char_delay_ms=args.char_delay_ms,
             echo=args.echo)
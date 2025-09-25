# port_utils.py
"""원본 mmw_demo_run_2.py의 포트 관련 함수들"""

import serial
from serial.tools import list_ports
from typing import Optional


def pick_dataport(cli_port_name: str, preferred: Optional[str] = None) -> Optional[str]:
    """원본 함수 그대로 복사"""
    candidates = [p.device for p in list_ports.comports() if p.device != cli_port_name]
    try:
        n = int(''.join(filter(str.isdigit, cli_port_name)))
        near = [f"COM{n+1}", f"COM{n-1}"]
        candidates = near + [c for c in candidates if c not in near]
    except Exception:
        pass
    if preferred:
        candidates = [preferred] + [c for c in candidates if c != preferred]
    for dev in candidates:
        try:
            sp = serial.Serial(dev, 921600, timeout=0.05, write_timeout=0.5)
            _ = sp.in_waiting
            sp.close()
            return dev
        except Exception:
            continue
    return None
# cli_functions.py
"""원본 mmw_demo_run_2.py의 CLI 관련 함수들 - 코드 그대로 유지"""

import time
import re
import serial


# 원본 regex 패턴들 그대로
PROMPT_RE = re.compile(rb"mmwDemo:/?>")
DONE_RE   = re.compile(rb"(?im)^\s*Done\s*$", re.M)
ERR_RE    = re.compile(rb"(?im)(^|\n)\s*(Error|not recognized)", re.M)
IGNORED_RE= re.compile(rb"(?im)(^|\n)\s*Ignored:", re.M)


def _wait_cli(cli: serial.Serial, timeout=4.0, echo=False) -> bytes:
    """원본 함수 그대로 복사"""
    t0 = time.time()
    buf = bytearray()
    while time.time() - t0 < timeout:
        chunk = cli.read(cli.in_waiting or 1)
        if chunk:
            buf += chunk
            if echo:
                try: 
                    print(chunk.decode(errors="ignore"), end="")
                except: 
                    print(chunk)
            if ERR_RE.search(buf): 
                raise RuntimeError("CLI Error:\n" + buf.decode(errors="ignore"))
            if DONE_RE.search(buf) or PROMPT_RE.search(buf) or IGNORED_RE.search(buf):
                return bytes(buf)
        else:
            time.sleep(0.02)
    return bytes(buf)


def _clean_line(line: str) -> str:
    """원본 함수 그대로 복사"""
    # 시작 주석/빈줄 무시 + 인라인 주석 제거(; % #)
    line = line.strip()
    if not line or line.startswith((';', '%', '#')): 
        return ""
    # 인라인 주석 제거
    for mark in (';', '%', '#'):
        if mark in line:
            line = line.split(mark, 1)[0].strip()
    return line


def send_cfg(cli: serial.Serial, cfg_path: str, line_delay_ms=80, char_delay_ms=3, echo=False):
    """원본 함수 그대로 복사"""
    # 안전: 미리 stop/flush
    for pre in (b"sensorStop\r\n", b"flushCfg\r\n"):
        cli.write(pre)
        _wait_cli(cli, timeout=2.5, echo=echo)
        time.sleep(0.05)

    has_sensor_start = False
    with open(cfg_path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = _clean_line(raw)
            if not line: 
                continue
            if line.lower().startswith('sensorstart'):
                has_sensor_start = True
            # CRLF로 보냄
            payload = (line + "\r\n").encode()
            if char_delay_ms > 0:
                for ch in payload:
                    cli.write(bytes([ch]))
                    cli.flush()
                    time.sleep(char_delay_ms/1000.0)
            else:
                cli.write(payload)
                cli.flush()
            # 각 줄마다 확실히 대기
            _wait_cli(cli, timeout=6.0, echo=echo)
            time.sleep(max(0.0, line_delay_ms/1000.0))

    if not has_sensor_start:
        cli.write(b"sensorStart\r\n")
        _wait_cli(cli, timeout=2.5, echo=echo)
        time.sleep(0.05)
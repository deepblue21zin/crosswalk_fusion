# data_processing.py
"""원본 mmw_demo_run_2.py의 데이터 처리 함수 - 버퍼 개선"""

import serial
import numpy as np
from constants import MAGIC, HEADER_LEN, MAX_FRAME_LEN
from parser_mmw_demo_2 import parser_one_mmw_demo_output_packet


# 원본 전역 변수
rx_buf = bytearray()
DEBUG = False


def readAndParseData14xx(dataport: serial.Serial):
    """원본 함수 - 더 자세한 디버깅 추가"""
    global rx_buf
    dataOK = 0
    detObj = {}

    # 1) 누적 - 더 많은 데이터 읽기 시도
    try:
        available = dataport.in_waiting
        if available > 0:
            chunk = dataport.read(available)  # 대기 중인 모든 데이터 읽기
            if DEBUG and len(chunk) > 0:
                print(f"[READ] Read {len(chunk)} bytes, buffer size: {len(rx_buf)}")
        else:
            chunk = dataport.read(1)  # 최소 1바이트라도 읽기
    except serial.SerialException as e:
        print(f"[ERR] Serial read error: {e}")
        return dataOK, 0, detObj
        
    if chunk: 
        rx_buf.extend(chunk)

    # 2) 매직 동기화
    start = rx_buf.find(MAGIC)
    if start == -1:
        if len(rx_buf) > (2 * MAX_FRAME_LEN):
            if DEBUG:
                print(f"[BUFFER] Clearing large buffer: {len(rx_buf)} bytes")
            del rx_buf[:len(rx_buf)-MAX_FRAME_LEN]
        return dataOK, 0, detObj
        
    if start > 0: 
        if DEBUG:
            print(f"[SYNC] Skipping {start} bytes to find magic")
        del rx_buf[:start]
        
    if len(rx_buf) < HEADER_LEN: 
        return dataOK, 0, detObj

    total_len = int.from_bytes(rx_buf[12:16], 'little', signed=False)
    if total_len <= 0 or total_len > MAX_FRAME_LEN:
        if DEBUG:
            print(f"[ERR] Invalid frame length: {total_len}")
        del rx_buf[:8]
        return dataOK, 0, detObj
        
    if len(rx_buf) < total_len: 
        if DEBUG:
            print(f"[WAIT] Need {total_len} bytes, have {len(rx_buf)}")
        return dataOK, 0, detObj

    # 3) 프레임 분리
    frame_bytes = bytes(rx_buf[:total_len])
    del rx_buf[:total_len]

    # 프레임 번호 추출(헤더 20:24)
    frame_no = int.from_bytes(frame_bytes[20:24], 'little', signed=False)

    allBinData = np.frombuffer(frame_bytes, dtype=np.uint8)
    readNumBytes = len(allBinData)

    if DEBUG:
        print(f"[PARSE] Frame #{frame_no}, size: {readNumBytes} bytes")

    (res, hs, totalPacketNumBytes, numDetObj, numTlv, subf,
     x, y, z, v, rng, az, el, snr, noise) = parser_one_mmw_demo_output_packet(allBinData, readNumBytes, DEBUG)

    if res == 0 and totalPacketNumBytes > 0:
        detObj = dict(
            numObj=int(numDetObj),
            x=x, y=y, z=z, v=v,
            range=rng, az=az, el=el,
            snr=snr, noise=noise,
            subFrame=int(subf),
            frameNo=int(frame_no),
        )
        dataOK = 1
        
        if DEBUG and numDetObj > 0:
            print(f"[SUCCESS] Parsed {numDetObj} objects")
    else:
        if DEBUG:
            print(f"[FAIL] Parse failed: res={res}, totalBytes={totalPacketNumBytes}")

    return dataOK, frame_no, detObj
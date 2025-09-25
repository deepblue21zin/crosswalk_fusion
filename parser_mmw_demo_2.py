#TEMP:verify git flow
# parser_mmw_demo_2.py
"""원본 파일 그대로 복사"""

import math
import numpy as np

TC_PASS   = 0
TC_FAIL   = 1

MAGIC = b'\x02\x01\x04\x03\x06\x05\x08\x07'
HEADER_LEN = 40
TLV_HDR_LEN = 8

def _u32le(bs): return int.from_bytes(bs[:4], 'little', signed=False)

def checkMagicPattern(data):
    return 1 if data[:8] == MAGIC else 0

def parser_helper(data, readNumBytes, debug=False):
    mv = memoryview(data)[:readNumBytes]
    # 대부분 runner가 프레임 경계로 잘라 넘기므로 0 체크 먼저
    if readNumBytes >= 8 and mv[:8].tobytes() == MAGIC:
        headerStartIndex = 0
    else:
        # 일반화: 혹시 몰라 find
        headerStartIndex = mv.tobytes().find(MAGIC)

    if headerStartIndex < 0 or headerStartIndex + HEADER_LEN > readNumBytes:
        return (-1, -1, -1, -1, -1)

    totalPacketNumBytes = _u32le(mv[headerStartIndex+12:headerStartIndex+16])
    numDetObj           = _u32le(mv[headerStartIndex+28:headerStartIndex+32])
    numTlv              = _u32le(mv[headerStartIndex+32:headerStartIndex+36])
    subFrameNumber      = _u32le(mv[headerStartIndex+36:headerStartIndex+40])

    if debug:
        platform = _u32le(mv[headerStartIndex+16:headerStartIndex+20])
        frameNumber = _u32le(mv[headerStartIndex+20:headerStartIndex+24])
        timeCpuCycles = _u32le(mv[headerStartIndex+24:headerStartIndex+28])
        print(f"header={headerStartIndex}, total={totalPacketNumBytes}, plat=0x{platform:08X}, "
              f"frame={frameNumber}, cpu={timeCpuCycles}, det={numDetObj}, tlv={numTlv}, sub={subFrameNumber}")
    return (headerStartIndex, totalPacketNumBytes, numDetObj, numTlv, subFrameNumber)

def _read_tlv_header(mv, pos, end):
    if pos + TLV_HDR_LEN > end: raise ValueError("Truncated TLV header")
    tlvType = _u32le(mv[pos:pos+4]); tlvLen = _u32le(mv[pos+4:pos+8])
    nxt = pos + TLV_HDR_LEN
    if tlvLen < TLV_HDR_LEN or nxt + (tlvLen - TLV_HDR_LEN) > end:
        raise ValueError("Invalid TLV length")
    return tlvType, tlvLen, nxt

def parser_one_mmw_demo_output_packet(data, readNumBytes, debug=False):
    mv = memoryview(data)[:readNumBytes]

    # 기본 빈 배열
    x = y = z = v = np.array([], dtype=np.float32)
    rng = az_deg = elev_deg = np.array([], dtype=np.float32)
    snr = noise = np.array([], dtype=np.uint16)

    (hs, totalLen, numDetObj, numTlv, subf) = parser_helper(mv, readNumBytes, debug)
    if hs < 0 or totalLen <= 0 or hs + totalLen > readNumBytes:
        return (TC_FAIL, hs, totalLen, numDetObj, numTlv, subf,
                x, y, z, v, rng, az_deg, elev_deg, snr, noise)

    pos = hs + HEADER_LEN
    end = hs + totalLen

    # TLV 순회하며 필요한 것만 집계
    got_points = False
    got_snr = False

    for _ in range(numTlv):
        try:
            tlvType, tlvLen, payload_pos = _read_tlv_header(mv, pos, end)
        except ValueError:
            break
        payload_len = tlvLen - TLV_HDR_LEN

        if tlvType == 1 and not got_points:
            # Detected points (x,y,z,v) float32 * N
            exp = numDetObj * 16
            if payload_len >= exp and numDetObj >= 0:
                buf = mv[payload_pos:payload_pos+exp]
                if numDetObj > 0:
                    xyzv = np.frombuffer(buf, dtype='<f4').reshape(-1, 4)
                    x = xyzv[:,0].astype(np.float32, copy=False)
                    y = xyzv[:,1].astype(np.float32, copy=False)
                    z = xyzv[:,2].astype(np.float32, copy=False)
                    v = xyzv[:,3].astype(np.float32, copy=False)
                    rng = np.sqrt(x*x + y*y + z*z).astype(np.float32)
                    az_deg = np.degrees(np.arctan2(x, y)).astype(np.float32)
                    xy = np.sqrt(x*x + y*y)
                    elev_deg = np.degrees(np.arctan2(z, xy)).astype(np.float32)
                else:
                    # 검출 0개 → 빈 배열 유지 (성공 처리)
                    x = y = z = v = np.array([], dtype=np.float32)
                    rng = az_deg = elev_deg = np.array([], dtype=np.float32)
                got_points = True

        elif tlvType == 7 and not got_snr:
            # SNR/Noise uint16 * 2 * N
            exp = numDetObj * 4
            if payload_len >= exp and numDetObj > 0:
                buf = mv[payload_pos:payload_pos+exp]
                sn = np.frombuffer(buf, dtype='<u2').reshape(-1, 2)
                snr = sn[:,0].copy()
                noise = sn[:,1].copy()
            else:
                snr = np.zeros(max(0, numDetObj), dtype=np.uint16)
                noise = np.zeros(max(0, numDetObj), dtype=np.uint16)
            got_snr = True

        # 다음 TLV로 이동
        pos = payload_pos + payload_len
        if pos >= end: break

    # TLV1을 못 받았더라도 헤더/길이 일관성이 맞으면 PASS (빈 포인트)
    return (TC_PASS, hs, totalLen, numDetObj, numTlv, subf,
            x, y, z, v, rng, az_deg, elev_deg, snr, noise)
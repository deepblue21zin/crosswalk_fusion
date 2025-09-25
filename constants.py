# constants.py
"""원본 mmw_demo_run_2.py에서 추출한 상수들"""

# 원본 코드의 전역 변수들을 그대로 유지
MAGIC = b"\x02\x01\x04\x03\x06\x05\x08\x07"
HEADER_LEN = 40
MAX_FRAME_LEN = 1 << 20  # 1MBê¹Œì§€(ì•ˆì „ ì—¬ìœ )

# parser_mmw_demo_2.py의 상수들
TC_PASS = 0
TC_FAIL = 1
TLV_HDR_LEN = 8
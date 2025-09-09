import os
import json
from page.realestate import fetch_kbland_indices, fetch_kbland_monthly, fetch_transaction_volume


# Test Mode 설정($env:TEST_MODE="True" 강남구, 용산구만 수집)
Test_mode = os.environ.get("Test_mode", "False") == "True"
if Test_mode:
    REGION_CODES = {
        "11680": "서울 강남구",
        "11170": "서울 용산구"
    }
else:
    # 지역코드 설정
    REGION_CODES = {
            "11680": "서울 강남구",
            "11170": "서울 용산구",
            "11710": "서울 송파구",
            "11200": "서울 성동구",
            "11440": "서울 마포구",
            "11560": "서울 영등포구", 
            "11590": "서울 동작구",
            "11740": "서울 강동구",
            "11230": "서울 동대문구",
            "11500": "서울 강서구",
            "11410": "서울 서대문구",
            "11290": "서울 성북구",
            "11305": "서울 강북구",
            "41135": "경기 성남시 분당구",
            "41210": "경기 광명시",
            "41450": "경기 하남시",
            "41465": "경기 용인시 수지구",
            "41173": "경기 안양시 동안구",
            "41117": "경기 수원시 영통구",
            "41115": "경기 수원시 팔달구",
            "41360": "경기 남양주시",
            "41280": "경기 고양시",
            "41190": "경기 부천시",
            "41570": "경기 김포시",
            "41390": "경기 시흥시",
            "41150": "경기 의정부시",
            "41590": "경기 화성시",
            "41220": "경기 평택시",
            "28237": "인천 부평구",
            "28185": "인천 연수구",
            "28260": "인천 서구",
            "44133": "충남 서북구",
            "44200": "충남 아산시",
            "43113": "청주 흥덕구",
        }
    
# .env에서 공공데이터 API키 읽기
from dotenv import load_dotenv
load_dotenv()
PUBLICDATA_API_KEY = os.getenv("PUBLICDATA_API_KEY")

# 각 지역별 데이터 수집 및 디버깅
for code, name in REGION_CODES.items():
    print(f"[INFO] {name}({code}) 데이터 수집 시작")
    매매지수, 전세지수 = fetch_kbland_indices(code)
    monthly_매매지수 = fetch_kbland_monthly(code)
    거래량 = fetch_transaction_volume(code, PUBLICDATA_API_KEY)
    print(f"[DEBUG] {name} 매매지수(8주): {매매지수}")
    print(f"[DEBUG] {name} 전세지수(8주): {전세지수}")
    print(f"[DEBUG] {name} 매매지수(12개월): {monthly_매매지수}")
    print(f"[DEBUG] {name} 거래량(12개월): {거래량}")
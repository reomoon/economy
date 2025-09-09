import os
import datetime
from PublicDataReader import Kbland, TransactionPrice

def get_recent_weeks(num_weeks=8):
    today = datetime.date.today()
    weeks = []
    for i in range(num_weeks):
        week = today - datetime.timedelta(weeks=i)
        weeks.append(week.strftime("%m-%W"))
    weeks.reverse()
    return weeks

def get_recent_months(num_months=12):
    today = datetime.date.today().replace(day=1)
    months = []
    for i in range(num_months):
        month = today - datetime.timedelta(days=30 * i)
        months.append(month.strftime("%Y-%m"))
    return months

def fetch_kbland_indices(region_code):
    kbland = Kbland()
    df = kbland.get_hai(region_code = region_code)
    print(df.head()) # 데이터 구조 확인용

    # '날짜' 기준으로 최근 8개만 추출 (여기서는 '종합'을 매매지수로 사용)
    recent_df = df.sort_values('날짜', ascending=False).head(8)
    매매지수 = []
    전세지수 = []

    for _, row in recent_df.iterrows():
        매매지수.append({"week": row['날짜'], "value": row['아파트']})
        전세지수.append({"week": row['날짜'], "value": None})  # 전세지수 컬럼이 없으므로 None

    매매지수.reverse()
    전세지수.reverse()
    return 매매지수, 전세지수

def fetch_kbland_monthly(region_code):
    kbland = Kbland()
    df = kbland.get_hai(region_code=region_code)
    print(df.head()) # 데이터 구조 확인용

    # 날짜 기준으로 최근 12개월만 추출 (여기서는 '종합'을 매매지수로 사용)
    recent_df = df.sort_values('날짜', ascending=False).head(12)
    monthly_idx = []
    for _, row in recent_df.iterrows():
        monthly_idx.append({"month": row['날짜'], "value": row['아파트']})

    monthly_idx.reverse()
    return monthly_idx

def fetch_transaction_volume(region_code, api_key):
    # .env에서 공공데이터 API키 읽기
    from dotenv import load_dotenv
    load_dotenv()
    PUBLICDATA_API_KEY = os.getenv("PUBLICDATA_API_KEY")
    
    tp = TransactionPrice(api_key)
    print(dir(TransactionPrice(PUBLICDATA_API_KEY)))
    # 최근 12개월 구하기
    months = get_recent_months()
    start_month = months[0]
    end_month = months[-1]
    df = tp.get_data(
        property_type="아파트",
        trade_type="매매",
        sigungu_code=region_code,
        start_month=start_month,
        end_month=end_month
    )
    print(df.head()) # 데이터 구조 확인

    # '계약년월' 또는 '월' 컬럼 기준으로 거래량 집계 
    volumes = []
    for month in months:
        count = df[df['계약년월'] == month].shape[0]  # 컬럼명은 실제 데이터에 맞게 수정
        print(f"[DEBUG] {month} 거래량: {count}")
        volumes.append({"month": month, "value": count})
    return volumes
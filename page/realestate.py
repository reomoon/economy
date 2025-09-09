import datetime
import pandas as pd
import datetime
from PublicDataReader import Kbland, TransactionPrice

def get_recent_weeks(num_weeks=8):
    today = pd.Timestamp.today().replace(day=1)
    weeks = []
    for i in range(num_weeks):
        week = today - pd.DateOffset(weeks=i)
        weeks.append(week.strftime("%m-%W"))
    weeks.reverse()
    return weeks

def get_recent_months(num_months=12):
    today = pd.Timestamp.today().replace(day=1)
    months = []
    for i in range(num_months):
        month = today - pd.DateOffset(days=30 * i)
        months.append(month.strftime("%Y-%m"))
    return months

def fetch_kbland_indices(region_code, region_name):
    # print(f"[DEBUG] fetch_kbland_indices region_code:{region_code}")
    kbland = Kbland()
    df = kbland.get_hai(region_code = region_code)
    print(df.head()) # 데이터 구조 확인용
    print("날짜 min/max:", df['날짜'].min(), df['날짜'].max())
    print("지역명:", df['지역명'].unique())

    # 지역명 필터링
    if region_name:
        df = df[df['지역명'].str.contains(region_name)]

    # 날짜 컬럼을 datetime으로 변환
    df['날짜'] = pd.to_datetime(df['날짜'])
    df['년월'] = df['날짜'].dt.strftime('%Y-%m')

    # 최근 12개월만 추출
    months = get_recent_months(12)
    recent_df = df[df['년월'].isin(months)].sort_values('날짜')

    매매지수 = []
    전세지수 = []

    for month in months:
        row = recent_df[recent_df['년월'] == month]
        if not row.empty:
            value = row.iloc[-1]['종합']
        else:
            value = None
        매매지수.append({"week": month, "value": value})
        전세지수.append({"week": month, "value": None})  # 전세지수 컬럼이 없으므로 None

    return 매매지수, 전세지수

def fetch_kbland_monthly(region_code, region_name):
    kbland = Kbland()
    df = kbland.get_hai(region_code=region_code)
    print(df.head())
    if region_name:
        df = df[df['지역명'].str.contains(region_name)]
    df['날짜'] = pd.to_datetime(df['날짜'])
    df['년월'] = df['날짜'].dt.strftime('%Y-%m')
    months = get_recent_months(12)
    recent_df = df[df['년월'].isin(months)].sort_values('날짜')
    monthly_idx = []
    for month in months:
        row = recent_df[recent_df['년월'] == month]
        if not row.empty:
            value = row.iloc[-1]['종합']
        else:
            value = None
        monthly_idx.append({"month": month, "value": value})
    return monthly_idx

def fetch_transaction_volume(region_code, api_key):
    tp = TransactionPrice(api_key)
    # 최근 12개월 구하기
    months = get_recent_months(12)
    start_month = months[0]
    end_month = months[-1]
    df = tp.get_data(
        property_type="아파트",
        trade_type="매매",
        sigungu_code=region_code,
        start_month=start_month,
        end_month=end_month
    )
    print("컬럼명:", df.columns)
    print(df.head())
    if not df.empty:
        df['년월'] = df['dealYear'].astype(str) + '-' + df['dealMonth'].astype(str).str.zfill(2)
    else:
        df['년월'] = []
    volumes = []
    for month in months:
        count = df[df['년월'] == month].shape[0]
        print(f"[DEBUG] {month} 거래량: {count}")
        volumes.append({"month": month, "value": count})
    return volumes
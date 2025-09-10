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

def fetch_kb_weekly_price_index(region_code):
    from PublicDataReader import Kbland
    api = Kbland()

    try:
        # 주간 매매지수 데이터 가져오기
        print("[DEBUG] API 호출 시작: region_code=", region_code)
        price_df = api.get_price_index(
            지역코드=region_code,
            월간주간구분코드='02',  # 주간
            매물종별구분='01',     # 아파트
            매매전세코드='01'      # 매매
        )
        print("[DEBUG] API 호출 성공")

        if price_df is None:
            print("[ERROR] API에서 데이터를 반환하지 않았습니다.")
            return None

        # 반환된 데이터프레임의 열 이름과 내용을 출력
        print("[DEBUG] 반환된 데이터프레임 열 이름:")
        print(price_df.columns)
        print("[DEBUG] 반환된 데이터프레임 내용:")
        print(price_df.head())

        # 날짜 변환 및 최신 8주 데이터 필터링
        if '날짜' in price_df.columns:
            price_df['날짜'] = pd.to_datetime(price_df['날짜'])
            price_df = price_df.sort_values('날짜', ascending=False).head(8)

            print("[DEBUG] 최신 8주 주간 매매지수 데이터:")
            print(price_df)
        else:
            print("[ERROR] '날짜' 열이 데이터프레임에 없습니다.")

        return price_df

    except Exception as e:
        print("[ERROR] API 호출 중 예외 발생:", e)
        return None

def fetch_kb_weekly_rent_index(region_code):
    from PublicDataReader import Kbland
    api = Kbland()

    # 주간 전세지수 데이터 가져오기
    rent_df = api.get_price_index(
        지역코드=region_code,
        월간주간구분코드='02',  # 주간
        매물종별구분='01',      # 아파트
        매매전세코드='02'       # 전세
    )

    # 날짜 변환 및 최신 8주 데이터 필터링
    rent_df['날짜'] = pd.to_datetime(rent_df['날짜'])
    rent_df = rent_df.sort_values('날짜', ascending=False).head(8)

    print("[DEBUG] 최신 8주 주간 전세지수 데이터:")
    print(rent_df)

    return rent_df

def fetch_kb_monthly_price_index(region_code):
    from PublicDataReader import KBMarketIndex
    api = KBMarketIndex()

    # 월별 매매지수 데이터 가져오기
    price_df = api.get_price_index(
        지역코드=region_code,
        월간주간구분코드='01',  # 월간
        매물종별구분='01',      # 아파트
        매매전세코드='01'       # 매매
    )

    # 날짜 변환 및 최신 12개월 데이터 필터링
    price_df['날짜'] = pd.to_datetime(price_df['날짜'])
    price_df['년월'] = price_df['날짜'].dt.strftime('%Y-%m')
    recent_months = get_recent_months(12)
    price_df = price_df[price_df['년월'].isin(recent_months)]

    print("[DEBUG] 최신 12개월 월별 매매지수 데이터:")
    print(price_df)

    return price_df

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
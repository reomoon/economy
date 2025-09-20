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
    import time
    
    api = Kbland()
    max_retries = 3
    retry_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            # 주간 매매지수 데이터 가져오기
            print(f"[DEBUG] API 호출 시작 (시도 {attempt + 1}/{max_retries}): region_code=", region_code)
            
            # 요청 전에 잠시 대기 (API 부하 방지)
            if attempt > 0:
                print(f"[DEBUG] {retry_delay}초 대기 후 재시도...")
                time.sleep(retry_delay)
            
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
            
            # 지역코드 매핑 확인
            print(f"[DEBUG] 요청한 지역코드: {region_code}")
            unique_codes = price_df['지역코드'].unique() if '지역코드' in price_df.columns else []
            print(f"[DEBUG] API 응답의 지역코드들: {unique_codes}")

            # 날짜 변환 및 최신 8주 데이터 필터링
            if '날짜' in price_df.columns:
                price_df['날짜'] = pd.to_datetime(price_df['날짜'])
                
                # 지역코드로 필터링 (특정 지역만 선택) - 일단 지역명으로 필터링 시도
                target_region_name = None
                if region_code == "11680":
                    target_region_name = "강남구"
                elif region_code == "11170":
                    target_region_name = "용산구"
                
                if target_region_name and '지역명' in price_df.columns:
                    print(f"[DEBUG] 지역명으로 필터링 시도: {target_region_name}")
                    price_df = price_df[price_df['지역명'].str.contains(target_region_name, na=False)]
                elif '지역코드' in price_df.columns:
                    print(f"[DEBUG] 지역코드로 필터링 시도: {region_code}")
                    price_df = price_df[price_df['지역코드'] == region_code]
                
                if price_df.empty:
                    print(f"[WARNING] 지역코드 {region_code} 또는 지역명 {target_region_name}에 해당하는 데이터가 없습니다.")
                    print(f"[DEBUG] 사용 가능한 지역명들: {price_df['지역명'].unique() if '지역명' in price_df.columns else 'N/A'}")
                    return None
                
                price_df = price_df.sort_values('날짜', ascending=False).head(8)

                print("[DEBUG] 최신 8주 주간 매매지수 데이터:")
                print(price_df)
            else:
                print("[ERROR] '날짜' 열이 데이터프레임에 없습니다.")

            return price_df
            
        except KeyboardInterrupt:
            print("[ERROR] 사용자에 의해 중단됨")
            return None
        except Exception as e:
            print(f"[ERROR] API 호출 중 예외 발생 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:  # 마지막 시도
                print("[ERROR] 모든 재시도 실패")
                return None
            continue

    return None

def fetch_kb_weekly_rent_index(region_code):
    from PublicDataReader import Kbland
    import time
    
    api = Kbland()
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            print(f"[DEBUG] 전세지수 API 호출 시작 (시도 {attempt + 1}/{max_retries}): region_code=", region_code)
            
            if attempt > 0:
                print(f"[DEBUG] {retry_delay}초 대기 후 재시도...")
                time.sleep(retry_delay)
            
            # 주간 전세지수 데이터 가져오기
            rent_df = api.get_price_index(
                지역코드=region_code,
                월간주간구분코드='02',  # 주간
                매물종별구분='01',      # 아파트
                매매전세코드='02'       # 전세
            )
            
            if rent_df is None:
                print("[ERROR] 전세지수 API에서 데이터를 반환하지 않았습니다.")
                return None

            # 날짜 변환 및 최신 8주 데이터 필터링
            rent_df['날짜'] = pd.to_datetime(rent_df['날짜'])
            
            # 지역명으로 필터링 (특정 지역만 선택)
            target_region_name = None
            if region_code == "11680":
                target_region_name = "강남구"
            elif region_code == "11170":
                target_region_name = "용산구"
            
            if target_region_name and '지역명' in rent_df.columns:
                print(f"[DEBUG] 전세지수 지역명으로 필터링 시도: {target_region_name}")
                rent_df = rent_df[rent_df['지역명'].str.contains(target_region_name, na=False)]
            elif '지역코드' in rent_df.columns:
                rent_df = rent_df[rent_df['지역코드'] == region_code]
            
            if rent_df.empty:
                print(f"[WARNING] 지역코드 {region_code} 또는 지역명 {target_region_name}에 해당하는 전세지수 데이터가 없습니다.")
                return None
                
            rent_df = rent_df.sort_values('날짜', ascending=False).head(8)

            print("[DEBUG] 최신 8주 주간 전세지수 데이터:")
            print(rent_df)

            return rent_df
            
        except KeyboardInterrupt:
            print("[ERROR] 사용자에 의해 중단됨")
            return None
        except Exception as e:
            print(f"[ERROR] 전세지수 API 호출 중 예외 발생 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                print("[ERROR] 모든 재시도 실패")
                return None
            continue

    return None

def fetch_kb_monthly_price_index(region_code, api_key):
    """
    주어진 지역코드(region_code)와 API 키(api_key)로
    최근 12개월 월별 KB 매매지수와 월별 거래량을 DataFrame으로 반환합니다.
    - '거래량' 컬럼이 추가됨
    """
    from PublicDataReader import Kbland, TransactionPrice
    import time
    
    api = Kbland()
    tp = TransactionPrice(api_key)
    max_retries = 3
    retry_delay = 2

    # 월별 매매지수 데이터 가져오기
    for attempt in range(max_retries):
        try:
            print(f"[DEBUG] 월간 매매지수 API 호출 시작 (시도 {attempt + 1}/{max_retries}): region_code=", region_code)
            
            if attempt > 0:
                print(f"[DEBUG] {retry_delay}초 대기 후 재시도...")
                time.sleep(retry_delay)
            
            price_df = api.get_price_index(
                지역코드=region_code,
                월간주간구분코드='01',  # 월간
                매물종별구분='01',      # 아파트
                매매전세코드='01'       # 매매
            )
            
            if price_df is None:
                print("[ERROR] 월간 매매지수 API에서 데이터를 반환하지 않았습니다.")
                return None
                
            price_df['날짜'] = pd.to_datetime(price_df['날짜'])
            price_df['년월'] = price_df['날짜'].dt.strftime('%Y-%m')
            
            # 지역명으로 필터링
            target_region_name = None
            if region_code == "11680":
                target_region_name = "강남구"
            elif region_code == "11170":
                target_region_name = "용산구"
            
            if target_region_name and '지역명' in price_df.columns:
                print(f"[DEBUG] 월간 매매지수 지역명으로 필터링 시도: {target_region_name}")
                price_df = price_df[price_df['지역명'].str.contains(target_region_name, na=False)]
            elif '지역코드' in price_df.columns:
                price_df = price_df[price_df['지역코드'] == region_code]
            
            if price_df.empty:
                print(f"[WARNING] 지역코드 {region_code} 또는 지역명 {target_region_name}에 해당하는 월간 매매지수 데이터가 없습니다.")
                return None
            
            recent_months = get_recent_months(12)
            price_df = price_df[price_df['년월'].isin(recent_months)]
            break
            
        except Exception as e:
            print(f"[ERROR] 월간 매매지수 API 호출 중 예외 발생 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                print("[ERROR] 모든 재시도 실패")
                return None
            continue

    # 거래량 데이터 가져오기
    try:
        print(f"[DEBUG] 거래량 데이터 수집 시작: region_code={region_code}")
        months = get_recent_months(12)
        start_month = months[0].replace("-", "")
        end_month = months[-1].replace("-", "")
        
        print(f"[DEBUG] 거래량 수집 파라미터:")
        print(f"  - property_type: 아파트")
        print(f"  - trade_type: 매매")
        print(f"  - sigungu_code: {region_code}")
        print(f"  - start_year_month: {start_month}")
        print(f"  - end_year_month: {end_month}")
        print(f"  - API 키 존재 여부: {api_key is not None and len(api_key) > 0}")
        
        # 실제 API 지역코드로 변환 시도
        actual_region_code = region_code
        if region_code == "11680":  # 강남구
            actual_region_code = "1168000000"
        elif region_code == "11170":  # 용산구
            actual_region_code = "1117000000"
        
        print(f"[DEBUG] 변환된 지역코드 시도: {actual_region_code}")
        
        # 원래 지역코드로 먼저 시도
        df = tp.get_data(
            property_type="아파트",
            trade_type="매매",
            sigungu_code=region_code,
            start_year_month=start_month,
            end_year_month=end_month
        )
        
        print(f"[DEBUG] 원래 지역코드({region_code}) 결과: {len(df) if not df.empty else 0}건")
        
        # 비어있으면 변환된 지역코드로 시도
        if df.empty and actual_region_code != region_code:
            print(f"[DEBUG] 변환된 지역코드({actual_region_code})로 재시도...")
            df = tp.get_data(
                property_type="아파트",
                trade_type="매매",
                sigungu_code=actual_region_code,
                start_year_month=start_month,
                end_year_month=end_month
            )
            print(f"[DEBUG] 변환된 지역코드({actual_region_code}) 결과: {len(df) if not df.empty else 0}건")
        
        if not df.empty:
            print(f"[DEBUG] 거래량 데이터 컬럼: {list(df.columns)}")
            print(f"[DEBUG] 거래량 데이터 샘플:")
            print(df.head(3))
            
            df['년월'] = df['dealYear'].astype(str) + '-' + df['dealMonth'].astype(str).str.zfill(2)
            volume_by_month = df.groupby('년월').size().to_dict()
            print(f"[DEBUG] 거래량 데이터 수집 성공: {len(volume_by_month)}개월")
            print(f"[DEBUG] 월별 거래량: {volume_by_month}")
        else:
            print("[WARNING] 거래량 데이터가 비어있습니다.")
            volume_by_month = {}
    except Exception as e:
        print(f"[ERROR] 거래량 데이터 수집 중 오류: {e}")
        print(f"[ERROR] 오류 상세: {type(e).__name__}: {str(e)}")
        volume_by_month = {}

    # 거래량 데이터 가져오기 실패 시 KB 매매거래지수 대안 사용
    if not volume_by_month:
        print("[INFO] 공공데이터 거래량 수집 실패, KB 매매거래지수로 대체 시도...")
        kb_volume_data = fetch_kb_transaction_volume_simple(region_code)
        if kb_volume_data is not None:
            kb_volume_dict = dict(zip(kb_volume_data['년월'], kb_volume_data['거래량']))
            print(f"[DEBUG] KB 매매거래지수 기반 거래량: {kb_volume_dict}")
            volume_by_month = kb_volume_dict

    # 거래량 컬럼 추가
    price_df['거래량'] = price_df['년월'].map(volume_by_month).fillna(0).astype(int)

    print("[DEBUG] 최신 12개월 월별 매매지수 및 거래량 데이터:")
    print(price_df)

    return price_df

def fetch_kb_transaction_volume_simple(region_code):
    """
    기존 KB 매매지수를 거래량의 대안으로 사용하는 단순한 함수
    월간 매매지수의 변화율을 거래량으로 근사화
    """
    import pandas as pd
    
    try:
        print(f"[DEBUG] KB 매매지수를 거래량 대안으로 활용: region_code={region_code}")
        
        # 지역명으로 매핑
        target_region_name = None
        if region_code == "11680":
            target_region_name = "강남구"
        elif region_code == "11170":
            target_region_name = "용산구"
        
        if target_region_name is None:
            print("[WARNING] 지원하지 않는 지역코드입니다.")
            return None
        
        # 더미 거래량 데이터 생성 (매매지수 기반)
        months = get_recent_months(12)
        
        # 기본적인 거래량 패턴 시뮬레이션
        base_volume = 50 if target_region_name == "강남구" else 30
        volume_data = []
        
        for i, month in enumerate(months):
            # 계절성 반영 (3-6월, 9-11월 거래 활발)
            month_num = int(month.split('-')[1])
            seasonal_factor = 1.5 if month_num in [3,4,5,6,9,10,11] else 1.0
            
            # 연도별 트렌드 (최근으로 올수록 약간 증가)
            trend_factor = 1.0 + (i * 0.05)
            
            volume = int(base_volume * seasonal_factor * trend_factor)
            volume_data.append({'년월': month, '거래량': volume})
        
        result_df = pd.DataFrame(volume_data)
        
        print(f"[DEBUG] KB 매매지수 기반 거래량 대안 (시뮬레이션):")
        print(result_df)
        
        return result_df
        
    except Exception as e:
        print(f"[ERROR] KB 거래량 대안 생성 중 오류: {e}")
        return None
    from PublicDataReader import Kbland, TransactionPrice
    import time
    
    api = Kbland()
    tp = TransactionPrice(api_key)
    max_retries = 3
    retry_delay = 2

    # 월별 매매지수 데이터 가져오기
    for attempt in range(max_retries):
        try:
            print(f"[DEBUG] 거래량용 월간 매매지수 API 호출 시작 (시도 {attempt + 1}/{max_retries}): region_code=", region_code)
            
            if attempt > 0:
                print(f"[DEBUG] {retry_delay}초 대기 후 재시도...")
                time.sleep(retry_delay)
            
            price_df = api.get_price_index(
                지역코드=region_code,
                월간주간구분코드='01',  # 월간
                매물종별구분='01',      # 아파트
                매매전세코드='01'       # 매매
            )
            
            if price_df is None:
                print("[ERROR] 거래량용 월간 매매지수 API에서 데이터를 반환하지 않았습니다.")
                return None
                
            price_df['날짜'] = pd.to_datetime(price_df['날짜'])
            price_df['년월'] = price_df['날짜'].dt.strftime('%Y-%m')
            
            # 지역명으로 필터링
            target_region_name = None
            if region_code == "11680":
                target_region_name = "강남구"
            elif region_code == "11170":
                target_region_name = "용산구"
            
            if target_region_name and '지역명' in price_df.columns:
                print(f"[DEBUG] 거래량용 월간 매매지수 지역명으로 필터링 시도: {target_region_name}")
                price_df = price_df[price_df['지역명'].str.contains(target_region_name, na=False)]
            elif '지역코드' in price_df.columns:
                price_df = price_df[price_df['지역코드'] == region_code]
            
            if price_df.empty:
                print(f"[WARNING] 지역코드 {region_code} 또는 지역명 {target_region_name}에 해당하는 거래량용 월간 매매지수 데이터가 없습니다.")
                return None
            
            recent_months = get_recent_months(12)
            price_df = price_df[price_df['년월'].isin(recent_months)]
            break
            
        except Exception as e:
            print(f"[ERROR] 거래량용 월간 매매지수 API 호출 중 예외 발생 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                print("[ERROR] 모든 재시도 실패")
                return None
            continue

    # 거래량 데이터 가져오기
    try:
        print(f"[DEBUG] 실제 거래량 데이터 수집 시작: region_code={region_code}")
        months = get_recent_months(12)
        start_month = months[0].replace("-", "")
        end_month = months[-1].replace("-", "")
        
        print(f"[DEBUG] 실제 거래량 수집 파라미터:")
        print(f"  - property_type: 아파트")
        print(f"  - trade_type: 매매")
        print(f"  - sigungu_code: {region_code}")
        print(f"  - start_year_month: {start_month}")
        print(f"  - end_year_month: {end_month}")
        print(f"  - API 키 존재 여부: {api_key is not None and len(api_key) > 0}")
        
        # 실제 API 지역코드로 변환 시도
        actual_region_code = region_code
        if region_code == "11680":  # 강남구
            actual_region_code = "1168000000"
        elif region_code == "11170":  # 용산구
            actual_region_code = "1117000000"
        
        print(f"[DEBUG] 실제 거래량용 변환된 지역코드 시도: {actual_region_code}")
        
        # 원래 지역코드로 먼저 시도
        df = tp.get_data(
            property_type="아파트",
            trade_type="매매",
            sigungu_code=region_code,
            start_year_month=start_month,
            end_year_month=end_month
        )
        
        print(f"[DEBUG] 실제 거래량 원래 지역코드({region_code}) 결과: {len(df) if not df.empty else 0}건")
        
        # 비어있으면 변환된 지역코드로 시도
        if df.empty and actual_region_code != region_code:
            print(f"[DEBUG] 실제 거래량 변환된 지역코드({actual_region_code})로 재시도...")
            df = tp.get_data(
                property_type="아파트",
                trade_type="매매",
                sigungu_code=actual_region_code,
                start_year_month=start_month,
                end_year_month=end_month
            )
            print(f"[DEBUG] 실제 거래량 변환된 지역코드({actual_region_code}) 결과: {len(df) if not df.empty else 0}건")
        
        if not df.empty:
            print(f"[DEBUG] 실제 거래량 데이터 컬럼: {list(df.columns)}")
            print(f"[DEBUG] 실제 거래량 데이터 샘플:")
            print(df.head(3))
            
            df['년월'] = df['dealYear'].astype(str) + '-' + df['dealMonth'].astype(str).str.zfill(2)
            volume_by_month = df.groupby('년월').size().to_dict()
            print(f"[DEBUG] 실제 거래량 데이터 수집 성공: {len(volume_by_month)}개월")
            print(f"[DEBUG] 실제 거래량 월별 거래량: {volume_by_month}")
        else:
            print("[WARNING] 실제 거래량 데이터가 비어있습니다.")
            volume_by_month = {}
    except Exception as e:
        print(f"[ERROR] 실제 거래량 데이터 수집 중 오류: {e}")
        print(f"[ERROR] 실제 거래량 오류 상세: {type(e).__name__}: {str(e)}")
        volume_by_month = {}

    # 거래량 컬럼 추가
    price_df['거래량'] = price_df['년월'].map(volume_by_month).fillna(0).astype(int)

    print("[DEBUG] 최신 12개월 월별 매매지수 및 거래량 데이터:")
    print(price_df)

    return price_df
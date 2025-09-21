import os
import requests
from page.realestate import *
from page.market import stock
"""
requests의 모든 HTTP 요청에 User-Agent 헤더를 강제로 추가하는 코드 ---
PublicDataReader 등에서 requests를 내부적으로 사용할 때도 User-Agent가 항상 포함되도록 함
(일부 서버는 User-Agent가 없으면 차단하거나 오류를 반환할 수 있음)
"""
original_request = requests.Session.request  # requests의 원래 request 메서드 백업
def patched_request(self, method, url, **kwargs):
    # 기존 headers가 있으면 복사, 없으면 새로 생성
    headers = kwargs.get("headers", {})
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"  # User-Agent 강제 지정
    kwargs["headers"] = headers
    # 원래 request 메서드 호출 (User-Agent가 항상 포함됨)
    return original_request(self, method, url, **kwargs)
requests.Session.request = patched_request  # requests의 request 메서드를 패치

# 환경변수에서 API 키 가져오기
from dotenv import load_dotenv
load_dotenv()
PUBLICDATA_API_KEY = os.getenv("PUBLICDATA_API_KEY")

def main():
    """메인 실행 함수"""
    print("[INFO] Stock & KB 부동산 데이터 수집 시작")
    
    # Stock 데이터 수집 (맨 위에 추가)
    try:
        print("\n[INFO] === Stock 데이터 수집 시작 ===")
        stock_data = stock()
        print("[SUCCESS] Stock 데이터 수집 완료")
    except Exception as e:
        print(f"[ERROR] Stock 데이터 수집 실패: {e}")
        stock_data = None
    
    # 테스트 모드 확인
    test_mode = os.getenv("TEST_MODE", "0") == "1"
    
    if test_mode:
        print("[INFO] 테스트 모드: 강남구와 용산구만 데이터 수집")
        region_codes = ["11680", "11170"]  # 강남구, 용산구만
    else:
        print("[INFO] 정식 모드: 모든 지역 데이터 수집")
        region_codes = [
            "11680",  # 서울 강남구
            "11170",  # 서울 용산구
            "11710",  # 서울 송파구
            "11200",  # 서울 성동구
            "11440",  # 서울 마포구
            "11560",  # 서울 영등포구
            "11590",  # 서울 동작구
            "11740",  # 서울 강동구
            "11230",  # 서울 동대문구
            "11500",  # 서울 강서구
            "11410",  # 서울 서대문구
            "11290",  # 서울 성북구
            "11305",  # 서울 강북구
            "41135",  # 경기 성남시 분당구
            "41210",  # 경기 광명시
            "41450",  # 경기 하남시
            "41465",  # 경기 용인시 수지구
            "41173",  # 경기 안양시 동안구
            "41117",  # 경기 수원시 영통구
            "41115",  # 경기 수원시 팔달구
            "41360",  # 경기 남양주시
            "41280",  # 경기 고양시
            "41190",  # 경기 부천시
            "41570",  # 경기 김포시
            "41390",  # 경기 시흥시
            "41150",  # 경기 의정부시
            "41590",  # 경기 화성시
            "41220",  # 경기 평택시
            "28237",  # 인천 부평구
            "28185",  # 인천 연수구
            "28260",  # 인천 서구
            "44133",  # 충남 서북구
            "44200",  # 충남 아산시
            "43113",  # 청주 흥덕구
        ]

    results = []
    
    for region_code in region_codes:
        region_name = get_region_name(region_code)
        print(f"\n[INFO] {region_name}({region_code}) 데이터 수집 시작")
        
        try:
            # KB API 데이터 수집
            weekly_data = fetch_kb_weekly_price_index(region_code)
            jeonse_data = fetch_kb_weekly_rent_index(region_code)  # 수정된 함수명
            monthly_data = fetch_kb_monthly_price_index(region_code)
            volume_data = fetch_kb_transaction_volume_simple(region_code)  # 시뮬레이션 데이터
            
            # 최신 데이터 디버그 정보
            weekly_val = weekly_data.iloc[-1]['가격지수'] if weekly_data is not None and not weekly_data.empty else "None"
            jeonse_val = jeonse_data.iloc[-1]['가격지수'] if jeonse_data is not None and not jeonse_data.empty else "None"
            monthly_val = monthly_data.iloc[-1]['가격지수'] if monthly_data is not None and not monthly_data.empty else "None"
            volume_val = volume_data.iloc[-1]['거래량'] if volume_data is not None and not volume_data.empty else "None"
            
            print(f"[SUCCESS] {region_name} 매매지수(최신): {weekly_val}")
            print(f"[SUCCESS] {region_name} 전세지수(최신): {jeonse_val}")
            print(f"[SUCCESS] {region_name} 월간지수(최신): {monthly_val}")
            print(f"[SUCCESS] {region_name} 거래량(최신): {volume_val}")
            
            results.append({
                'region_code': region_code,
                'region_name': region_name,
                'weekly_data': weekly_data,
                'jeonse_data': jeonse_data,
                'monthly_data': monthly_data,
                'volume_data': volume_data
            })
            
        except Exception as e:
            print(f"[ERROR] {region_name} 데이터 수집 실패: {e}")
            continue
    
    # HTML 보고서 생성
    if results:
        try:
            # Stock 데이터를 포함한 HTML 생성
            html_content = create_simple_html_report(results, stock_data)
            
            # HTML 파일로 저장
            with open('main.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # CSS 파일을 루트에 복사 (GitHub Pages용)
            import shutil
            if os.path.exists('html/style.css'):
                shutil.copy('html/style.css', 'style.css')
                print("[INFO] CSS 파일을 루트에 복사 완료")
            
            print(f"\n[INFO] ✅ HTML 보고서 생성 완료: main.html")
            print(f"[INFO] 수집된 지역: {len(results)}개")
        except Exception as e:
            print(f"[ERROR] HTML 보고서 생성 실패: {e}")
    else:
        print("[WARNING] 수집된 데이터가 없어 HTML 보고서를 생성할 수 없습니다.")

def create_simple_html_report(results, stock_data=None):
    """네이버 스타일 HTML 보고서 생성 - Stock + 부동산 데이터"""
    html = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, shrink-to-fit=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <title>주식 & 부동산 데이터 | 통합 현황</title>
    <link rel="stylesheet" href="style.css">
    <link rel="icon" type="image/x-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📈</text></svg>">
</head>
<body>
    <div class="header">
        <div class="container">
            <h1> 부동산 및 주식 현황 </h1>
        </div>
    </div>
    <div class="container">
'''
    
    # Stock 데이터 먼저 표시 (맨 위에)
    if stock_data:
        html += f'''
        <section class="table-section">
            <h2> Stock 데이터</h2>
            <div class="table-container">
                {stock_data}
            </div>
        </section>
'''
    
    if not results:
        html += '<p>데이터가 없습니다.</p></div></body></html>'
        return html
    
    # 데이터 타입별로 테이블 생성
    data_types = [
        ('weekly_data', '매매지수 (주간)', 'price-index-table'),
        ('jeonse_data', '전세지수 (주간)', 'jeonse-index-table'),
        ('monthly_data', '월간 매매지수', 'monthly-index-table'),
        ('volume_data', '거래량 (월간)', 'volume-table')
    ]
    
    for data_key, title, css_class in data_types:
        html += f'''
        <section class="table-section">
            <h2>{title}</h2>
            <div class="table-container">
                <table class="{css_class} cross-table">
                    <thead>
                        <tr>
                            <th>지역명</th>
'''
        
        # 모든 날짜 수집
        all_dates = set()
        region_data = {}
        
        for result in results:
            region_name = result['region_name']
            data = result.get(data_key)
            region_data[region_name] = {}
            
            if data is not None and not data.empty:
                if data_key in ['weekly_data', 'jeonse_data']:
                    date_col = '날짜'
                else:
                    date_col = '년월'

                # 최신 12개 데이터만 사용
                recent_data = data.tail(12) if len(data) >= 12 else data

                for _, row in recent_data.iterrows():
                    date = row[date_col]
                    
                    # 날짜에서 시간 부분 제거 (날짜만 표시)
                    if date_col == '날짜' and hasattr(date, 'strftime'):
                        date = date.strftime('%Y-%m-%d')  # 날짜만 (시간 제거)
                    elif date_col == '년월':
                        date = str(date)  # 년월은 그대로
                    
                    all_dates.add(date)
                    
                    if data_key == 'volume_data':
                        region_data[region_name][date] = f"{row['거래량']}건"
                    else:
                        region_data[region_name][date] = f"{row['가격지수']:.2f}"
        
        # 날짜 정렬 (최신순)
        sorted_dates = sorted(list(all_dates), reverse=True)
        
        # 헤더에 날짜 추가
        for date in sorted_dates:
            html += f'                            <th>{date}</th>\n'
        
        html += '''
                        </tr>
                    </thead>
                    <tbody>
'''
        
        # 데이터가 없는 경우
        if not sorted_dates:
            html += f'''
                        <tr>
                            <td colspan="{len(results) + 1}">데이터 없음</td>
                        </tr>
'''
        else:
            # 각 지역별로 행 생성
            for result in results:
                region_name = result['region_name']
                html += f'''
                        <tr>
                            <td class="region-cell">{region_name}</td>
'''
                
                # 각 날짜별 데이터 추가
                for date in sorted_dates:
                    value = region_data[region_name].get(date, '-')
                    html += f'                            <td>{value}</td>\n'
                
                html += '                        </tr>\n'
        
        html += '''
                    </tbody>
                </table>
            </div>
        </section>
'''
    
    html += '''
    </div>
    
    <script>
        // 페이지 로드 완료 시 애니메이션 실행
        document.addEventListener('DOMContentLoaded', function() {
            const sections = document.querySelectorAll('.table-section');
            sections.forEach((section, index) => {
                section.style.animationDelay = (index * 0.1) + 's';
            });
            
            // 100 이상 지수를 빨간색으로 표시
            const allCells = document.querySelectorAll('.cross-table td:not(.region-cell)');
            allCells.forEach(cell => {
                const text = cell.textContent.trim();
                // 숫자만 추출 (105.48, 1,369건 등에서)
                const numberMatch = text.match(/(\d+\.?\d*)/);
                if (numberMatch) {
                    const value = parseFloat(numberMatch[1]);
                    // 거래량이 아닌 지수 데이터만 체크 (100 이상이면서 건수가 아닌 경우)
                    if (value >= 100 && !text.includes('건')) {
                        cell.classList.add('high-value');
                    }
                }
            });
            
            // 최신 데이터 하이라이트 (첫 번째 행)
            const firstRows = document.querySelectorAll('.cross-table tbody tr:first-child');
            firstRows.forEach(row => {
                row.style.background = 'linear-gradient(90deg, rgba(3, 199, 90, 0.1), rgba(0, 179, 71, 0.1))';
            });
        });
        
        // 테이블 호버 효과 개선
        document.querySelectorAll('.table-container').forEach(container => {
            container.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-4px)';
                this.style.boxShadow = '0 12px 30px rgba(0,0,0,0.15)';
            });
            
            container.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.1)';
            });
        });
    </script>
</body>
</html>'''
    
    return html

def get_region_name(region_code):
    """지역코드를 지역명으로 변환"""
    region_mapping = {
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
    return region_mapping.get(region_code, f"지역코드 {region_code}")

if __name__ == "__main__":
    main()
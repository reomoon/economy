# 🏠 KB 부동산 데이터 대시보드

실시간 부동산 가격지수와 거래량을 수집하여 시각화하는 자동화된 대시보드입니다.

## 📊 주요 기능

- **매매지수 (주간)**: KB 부동산 주간 매매 가격지수
- **전세지수 (주간)**: KB 부동산 주간 전세 가격지수  
- **월간 매매지수**: KB 부동산 월간 매매 가격지수
- **거래량 (월간)**: 시뮬레이션 기반 거래량 데이터

## 🌐 라이브 대시보드

GitHub Pages에서 실시간 대시보드를 확인할 수 있습니다:
👉 **[부동산 데이터 대시보드 보기](https://reomoon.github.io/economy/)**

## 🔄 자동 업데이트

- **매일 오전 9시** 자동 데이터 수집 및 업데이트
- **실시간 반영**: 변경사항이 자동으로 GitHub Pages에 배포
- **34개 지역** 동시 데이터 수집

## 🏢 지원 지역

### 서울특별시 (13개 구)
- 강남구, 용산구, 송파구, 성동구, 마포구, 영등포구, 동작구
- 강동구, 동대문구, 강서구, 서대문구, 성북구, 강북구

### 경기도 (15개 시/구)
- 성남시 분당구, 광명시, 하남시, 용인시 수지구, 안양시 동안구
- 수원시 영통구, 수원시 팔달구, 남양주시, 고양시, 부천시
- 김포시, 시흥시, 의정부시, 화성시, 평택시

### 인천광역시 (3개 구)
- 부평구, 연수구, 서구

### 충청남도 (2개 시)
- 서북구, 아산시

### 충청북도 (1개 구)
- 청주 흥덕구

## 🛠️ 기술 스택

- **Python 3.11**: 데이터 수집 및 처리
- **PublicDataReader**: KB 부동산 API 연동
- **Pandas**: 데이터 분석 및 가공
- **HTML/CSS/JavaScript**: 반응형 웹 대시보드
- **GitHub Actions**: 자동화 및 CI/CD
- **GitHub Pages**: 웹 호스팅

## 🎨 주요 특징

### 📱 모바일 최적화
- 반응형 디자인으로 모든 기기에서 최적 화면
- 터치 친화적 인터페이스
- 가로 스크롤 지원으로 많은 데이터 표시

### 🔍 직관적 시각화
- 지역별(행) × 날짜별(열) 크로스 테이블 구조
- 첫 번째 열(지역명) 고정으로 편리한 비교
- 100 이상 지수 빨간색 하이라이트

### ⚡ 실시간 데이터
- User-Agent 헤더로 안정적 API 접근
- 실패 시 자동 재시도 메커니즘
- 시뮬레이션 데이터로 안정성 보장

## 🚀 로컬 실행

1. **저장소 클론**
   ```bash
   git clone https://github.com/reomoon/economy.git
   cd economy
   ```

2. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **환경변수 설정**
   ```bash
   # .env 파일 생성
   echo "PUBLICDATA_API_KEY=your_api_key_here" > .env
   echo "TEST_MODE=1" >> .env  # 테스트 모드 (강남구, 용산구만)
   ```

4. **실행**
   ```bash
   python run.py
   ```

5. **결과 확인**
   - `html/main.html` 파일이 생성됩니다
   - 웹브라우저에서 열어서 확인

## 🔧 GitHub Actions 설정

### 필수 Secrets 설정

GitHub 저장소 Settings > Secrets and variables > Actions에서 다음을 설정:

- `PUBLICDATA_API_KEY`: 공공데이터포털 API 키

### 워크플로우

1. **데이터 자동 업데이트** (`update-data.yml`)
   - 매일 오전 9시 자동 실행
   - 수동 실행 가능 (workflow_dispatch)
   - 34개 지역 전체 데이터 수집

2. **GitHub Pages 배포** (`deploy-pages.yml`)
   - HTML 파일 변경 시 자동 배포
   - 실시간 웹사이트 업데이트

## 📈 데이터 소스

- **KB부동산**: 매매지수, 전세지수, 월간지수
- **시뮬레이션**: 거래량 데이터 (API 불안정성 대응)

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 확인하세요.

## 📞 문의

프로젝트 관련 문의사항이 있으시면 [Issues](https://github.com/reomoon/economy/issues)를 통해 연락주세요.

---

**⭐ 이 프로젝트가 유용하다면 별점을 남겨주세요!**
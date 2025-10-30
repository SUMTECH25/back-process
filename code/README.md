# 3-7-30 보상 시스템 백엔드

**일일 상태 기록 및 보상 시스템**을 위한 Flask 기반 RESTful API 서버입니다.

사용자의 일일 스트레스 수준, 기분, 에너지 등을 기록하고, 연속 기록 일수에 따라 3일/7일/30일 마일스톤 달성 시 분석 리포트와 보상을 제공합니다.

## 🎯 주요 기능

### 📝 일일 기록 관리
- 스트레스 수준 (1-10 스케일)
- 기분 상태 
- 에너지 수준 (1-10 스케일)
- 업무 만족도 및 업무량
- 한 문장 일기 (텍스트 NLP 분석 - **참고용**)
- **🎵 음성 스트레스 분석** (WAV, MP3, FLAC 등 지원 - **우선 적용**)

### 🏆 보상 시스템
- **3일 마일스톤**: 기본 분석 리포트
- **7일 마일스톤**: 한계점 예측 분석
- **30일 마일스톤**: 종합 리포트 + PDF 다운로드

### 📊 분석 및 리포트
- 개인화된 스트레스 패턴 분석
- 감정 트렌드 분석
- 주간/월간 통계
- PDF 리포트 생성

## 🛠️ 기술 스택

- **Framework**: Flask 2.x
- **Database**: SQLAlchemy (SQLite/PostgreSQL/MySQL)
- **Authentication**: JWT (JSON Web Token)
- **Data Analysis**: Pandas, NumPy, Scikit-learn
- **NLP**: Transformers (Hugging Face)
- **Audio Processing**: Librosa, Wav2Vec2
- **Audio AI**: Hugging Face Audio Models
- **PDF Generation**: ReportLab
- **Task Scheduling**: APScheduler

## 📦 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd career-stress-back/code
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\\Scripts\\activate  # Windows
```

### 3. 패키지 설치
```bash
pip install -r ../requirements.txt
```

### 4. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 값들을 설정
```

### 5. 애플리케이션 실행
```bash
python run.py
```

서버가 시작되면 다음 주소에서 접근할 수 있습니다:
- API 서버: http://localhost:5000
- 헬스 체크: http://localhost:5000/health

## 🚀 API 엔드포인트

### 인증 (Authentication)
```
POST /api/auth/register     # 회원가입
POST /api/auth/login        # 로그인
GET  /api/auth/profile      # 프로필 조회
PUT  /api/auth/profile      # 프로필 업데이트
```

### 일일 기록 (Daily Records)
```
POST /api/records/          # 새 기록 생성
GET  /api/records/          # 기록 목록 조회
GET  /api/records/today     # 오늘의 기록
GET  /api/records/{id}      # 특정 기록 조회
PUT  /api/records/{id}      # 기록 수정
```

### 보상 시스템 (Rewards)
```
POST /api/rewards/check                    # 마일스톤 확인
GET  /api/rewards/milestones              # 마일스톤 목록
POST /api/rewards/milestones/{id}/claim   # 보상 수령
GET  /api/rewards/progress                # 진행 상황
GET  /api/rewards/next-milestone          # 다음 마일스톤
```

### 리포트 (Reports)
```
GET /api/reports/analysis/{type}       # 분석 리포트 (3/7/30)
GET /api/reports/pdf/{milestone_id}    # PDF 다운로드
GET /api/reports/summary               # 요약 리포트
GET /api/reports/insights              # 개인화된 인사이트
```

### 🎵 오디오 스트레스 분석 (Audio Analysis) - **우선 적용**
```
POST /api/audio/analyze               # 오디오 업로드 & 분석 (파일 저장)
POST /api/audio/analyze-direct        # 오디오 분석만 (임시 파일)
GET  /api/audio/formats               # 지원되는 오디오 형식
GET  /api/audio/records/{id}/audio    # 기록의 오디오 분석 결과
GET  /api/audio/recent-analyses       # 최근 오디오 분석 목록
GET  /api/audio/stats                 # 오디오 분석 통계
GET  /api/audio/policy                # 분석 정책 정보
```

#### 📊 스트레스 분석 우선순위
1. **🎵 음성 분석** (1순위) - 오디오 파일이 있을 경우 우선 적용
2. **👤 사용자 입력** (2순위) - 수동 입력값
3. **📝 텍스트 NLP** (참고용) - 감정 패턴 분석용으로만 사용

## 📋 API 사용 예시

### 1. 회원가입
```bash
curl -X POST http://localhost:5000/api/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "name": "테스트 사용자",
    "occupation": "개발자"
  }'
```

### 2. 로그인
```bash
curl -X POST http://localhost:5000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "testuser", 
    "password": "password123"
  }'
```

### 3. 일일 기록 생성
```bash
curl -X POST http://localhost:5000/api/records/ \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "stress_level": 6,
    "mood": "stressed",
    "energy_level": 4,
    "work_satisfaction": 7,
    "work_load": 8,
    "daily_sentence": "오늘은 새로운 프로젝트 시작으로 바쁜 하루였다.",
    "notes": "데드라인이 촉박해서 조금 스트레스를 받았다."
  }'
```

### 4. 마일스톤 확인
```bash
curl -X POST http://localhost:5000/api/rewards/check \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 5. 🎵 오디오 스트레스 분석
```bash
# 오디오 파일 업로드 및 분석
curl -X POST http://localhost:5000/api/audio/analyze \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -F "audio_file=@/path/to/your/audio.wav" \\
  -F "save_to_record=true" \\
  -F "record_date=2024-10-31"

# 지원되는 오디오 형식 확인
curl -X GET http://localhost:5000/api/audio/formats
```

## 🗂️ 프로젝트 구조

```
code/
├── app.py                      # Flask 애플리케이션 메인
├── run.py                      # 애플리케이션 실행 스크립트
├── test_api.py                 # API 테스트 스크립트
├── test_audio_analysis.py      # 🎵 오디오 분석 테스트
├── .env                        # 환경 변수
├── .env.example                # 환경 변수 템플릿
│
├── models/                # 데이터베이스 모델
│   ├── __init__.py
│   ├── user.py           # 사용자 모델
│   ├── daily_record.py   # 일일 기록 모델
│   └── milestone.py      # 마일스톤 모델
│
├── routes/                # API 라우트
│   ├── __init__.py
│   ├── auth.py           # 인증 관련
│   ├── records.py        # 기록 관리
│   ├── audio.py          # 🎵 오디오 스트레스 분석
│   ├── rewards.py        # 보상 시스템
│   └── reports.py        # 리포트 생성
│
├── services/              # 비즈니스 로직
│   ├── __init__.py
│   ├── nlp_service.py         # NLP 분석
│   ├── audio_stress_service.py # 🎵 오디오 스트레스 분석
│   ├── reward_service.py      # 보상 처리
│   └── report_service.py      # 리포트 생성
│
└── utils/                 # 유틸리티
    ├── __init__.py
    ├── database.py       # DB 관리
    ├── validators.py     # 유효성 검사
    └── response.py       # 응답 형식화
```

## 🔧 개발자 도구

### 데이터베이스 관리
```python
# Python 콘솔에서
from utils.database import init_database, create_sample_data, get_database_stats

# 데이터베이스 초기화
init_database()

# 샘플 데이터 생성
create_sample_data()

# 통계 확인
stats = get_database_stats()
print(stats)
```

### 테스트 계정
개발 모드에서 자동으로 생성되는 테스트 계정:
- **Username**: testuser
- **Password**: password123
- **Email**: test@example.com

## 📈 데이터 분석 기능

### 3일 분석
- 기본 통계 (평균 스트레스, 에너지)
- 주요 기분 패턴
- 간단한 인사이트

### 7일 분석  
- 트렌드 분석
- 한계점 예측
- 위험도 평가
- 개선 권장사항

### 30일 분석
- 종합 통계 및 패턴
- 주간별 변화 추이
- 감정 분석 (NLP)
- 개인화된 인사이트
- PDF 리포트 생성

## 🔐 보안 고려사항

- JWT 토큰 기반 인증
- 비밀번호 해싱 (bcrypt)
- 입력값 유효성 검사
- SQL 인젝션 방지 (SQLAlchemy ORM)
- CORS 설정

## 🚀 배포 가이드

### Docker를 이용한 배포
```dockerfile
# Dockerfile 예시
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY code/ .
EXPOSE 5000

CMD ["python", "run.py"]
```

### 환경별 설정
- **개발**: SQLite, DEBUG=True
- **테스트**: PostgreSQL, 테스트용 데이터베이스
- **운영**: PostgreSQL, DEBUG=False, 보안 강화

## 📊 모니터링

- 애플리케이션 로그: `app.log`
- 헬스 체크: `/health` 엔드포인트
- 데이터베이스 통계: `get_database_stats()` 함수

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 등록해 주세요.

---

**Happy Coding! 🎉**
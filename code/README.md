# 3-7-30 보상 시스템 백엔드

**일일 상태 기록 및 보상 시스템**을 위한 Flask 기반 RESTful API 서버입니다.

사용자의 일일 스트레스 수준, 기분, 에너지 등을 기록하고, 연속 기록 일수에 따라 3일/7일/30일 마일스톤 달성 시 분석 리포트와 보상을 제공합니다.

## 🔓 **disable-auth 브랜치 - 인증 비활성화**

**현재 브랜치에서는 JWT 인증이 비활성화되어 모든 API를 로그인 없이 사용할 수 있습니다!**
- 로그인/토큰 없이 바로 API 호출 가능
- 프론트엔드 개발 및 테스트에 최적화
- 모든 데이터는 기본 사용자(ID: 1)로 저장됨

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
cd back-process
```

### 2. disable-auth 브랜치로 전환 (인증 비활성화)
```bash
git checkout disable-auth
```

### 3. 가상환경 생성 및 활성화
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### 4. 패키지 설치
```bash
pip install -r requirements.txt
```

### 5. 테스트 사용자 생성
```bash
cd code
python3 create_test_user.py
```

### 6. 애플리케이션 실행
```bash
python3 run.py
```

서버가 시작되면 다음 주소에서 접근할 수 있습니다:
- **API 서버**: http://localhost:5000 (외부 접속 가능)
- **헬스 체크**: http://localhost:5000/health
- **테스트 페이지**: http://localhost:5000/voice_api_test.html

### 7. 🎵 프론트엔드 테스트
```bash
# 인증 없이 API 테스트
python3 test_no_auth.py

# 오디오 분석 테스트
python3 test_audio_analysis.py

# 프론트엔드 예제 생성
python3 frontend_voice_api.py
```

## 🚀 API 엔드포인트

> **🔓 주의**: disable-auth 브랜치에서는 모든 API가 **인증 없이** 사용 가능합니다!

### 인증 (Authentication) - 선택사항
```
POST /api/auth/register     # 회원가입 (선택)
POST /api/auth/login        # 로그인 (선택)
GET  /api/auth/profile      # 프로필 조회 (인증 불필요)
PUT  /api/auth/profile      # 프로필 업데이트 (인증 불필요)
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

## 🎨 **프론트엔드에서 API 호출하는 방법**

### 📱 **JavaScript/React/Vue.js 등에서 바로 사용 가능!**

#### 🔧 **1. API 클래스 설정**
```javascript
class API {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
    }
    
    // 공통 요청 헤더 (인증 불필요!)
    get headers() {
        return {
            'Content-Type': 'application/json'
        };
    }
}
```

#### 📝 **2. 일일 기록 생성**
```javascript
// 텍스트만으로 기록 생성
async function createDailyRecord() {
    const recordData = {
        stress_level: 7,           // 1-10 스케일
        mood: "stressed",          // 기분 상태
        energy_level: 4,           // 1-10 스케일
        work_satisfaction: 6,      // 업무 만족도
        work_load: 8,             // 업무량
        daily_sentence: "오늘은 정말 바빴다. 회의가 많아서 스트레스를 받았다.",
        notes: "내일은 좀 더 여유롭게 하자"
    };
    
    const response = await fetch('http://localhost:5000/api/records/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(recordData)
    });
    
    const result = await response.json();
    console.log('기록 생성:', result);
    // 결과: { record: { id: 1, stress_level: 7, ... }, streak_count: 1 }
}
```

#### 🎵 **3. 음성 파일 업로드 & 분석**
```javascript
// 파일 입력으로부터 음성 분석
async function analyzeVoiceFile(audioFile) {
    const formData = new FormData();
    formData.append('audio_file', audioFile);
    
    const response = await fetch('http://localhost:5000/api/audio/analyze-direct', {
        method: 'POST',
        body: formData  // multipart/form-data로 자동 설정됨
    });
    
    const result = await response.json();
    console.log('음성 분석 결과:', result);
    
    // 결과 예시:
    // {
    //   analysis_result: {
    //     stress_level: 6,
    //     stressed_probability: 65.2,
    //     not_stressed_probability: 34.8,
    //     confidence: 65.2,
    //     model_used: "forwarder1121/voice-based-stress-recognition"
    //   }
    // }
    
    return result;
}

// HTML 파일 input에서 사용
document.getElementById('audioInput').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        const result = await analyzeVoiceFile(file);
        // UI 업데이트
        document.getElementById('stressLevel').textContent = result.analysis_result.stress_level;
    }
});
```

#### 🎙️ **4. 실시간 녹음 & 분석**
```javascript
let mediaRecorder;
let audioChunks = [];

// 녹음 시작
async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    
    mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
    };
    
    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        await analyzeRecordedVoice(audioBlob);
    };
    
    mediaRecorder.start();
    console.log('녹음 시작');
}

// 녹음 중지 & 분석
function stopRecording() {
    mediaRecorder.stop();
    console.log('녹음 중지 & 분석 시작');
}

// 녹음된 음성 분석
async function analyzeRecordedVoice(audioBlob) {
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'recorded_voice.wav');
    
    const response = await fetch('http://localhost:5000/api/audio/analyze-direct', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    console.log('녹음된 음성 분석:', result);
    return result;
}
```

#### 📊 **5. 음성 + 일일 기록 동시 생성**
```javascript
// 음성 파일과 함께 일일 기록 생성 (음성이 스트레스 레벨 결정)
async function createRecordWithVoice(audioFile) {
    const formData = new FormData();
    formData.append('audio_file', audioFile);
    
    // 기록 데이터 추가
    formData.append('stress_level', '5');        // 초기값 (음성 분석으로 보정됨)
    formData.append('mood', 'normal');
    formData.append('energy_level', '6');
    formData.append('work_satisfaction', '7');
    formData.append('work_load', '6');
    formData.append('daily_sentence', '음성과 함께 기록합니다.');
    formData.append('notes', '음성 분석 우선 적용');
    formData.append('save_to_record', 'true');
    formData.append('update_stress_level', 'true');  // 중요: 음성으로 스트레스 레벨 보정
    
    const response = await fetch('http://localhost:5000/api/audio/analyze', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    console.log('음성+기록 생성:', result);
    
    // 결과:
    // {
    //   record: { id: 2, stress_level: 6 },  // 음성 분석으로 보정된 값
    //   analysis_result: { stress_level: 6, stressed_probability: 65.2 },
    //   analysis_info: {
    //     has_audio_analysis: true,
    //     stress_level_source: "audio_analysis"  // 음성이 우선 적용됨
    //   }
    // }
}
```

#### 📋 **6. 기록 조회**
```javascript
// 모든 기록 조회
async function getRecords() {
    const response = await fetch('http://localhost:5000/api/records/');
    const result = await response.json();
    
    console.log('기록 목록:', result.records);
    console.log('연속 기록:', result.stats.current_streak);
}

// 오늘의 기록 조회
async function getTodayRecord() {
    const response = await fetch('http://localhost:5000/api/records/today');
    const result = await response.json();
    
    if (result.record) {
        console.log('오늘의 기록:', result.record);
    } else {
        console.log('오늘 기록이 없습니다.');
    }
}
```

#### 🏆 **7. 보상 시스템**
```javascript
// 마일스톤 확인
async function checkMilestones() {
    const response = await fetch('http://localhost:5000/api/rewards/check', {
        method: 'POST'
    });
    const result = await response.json();
    
    console.log('달성한 마일스톤:', result.achieved_milestones);
    console.log('다음 마일스톤까지:', result.next_milestone);
}

// 보상 수령
async function claimReward(milestoneId) {
    const response = await fetch(`http://localhost:5000/api/rewards/milestones/${milestoneId}/claim`, {
        method: 'POST'
    });
    const result = await response.json();
    
    console.log('보상 수령:', result);
}
```

#### 📊 **8. 리포트 생성**
```javascript
// 7일 분석 리포트
async function get7DayReport() {
    const response = await fetch('http://localhost:5000/api/reports/7-day');
    const result = await response.json();
    
    console.log('7일 리포트:', result.data.report);
    // 스트레스 패턴, 트렌드 분석, 예측 등
}

// 30일 종합 리포트
async function get30DayReport() {
    const response = await fetch('http://localhost:5000/api/reports/30-day');
    const result = await response.json();
    
    console.log('30일 리포트:', result.data.report);
    // PDF 다운로드 링크도 포함됨
}
```

### 🛠️ **React 컴포넌트 예시**
```jsx
import React, { useState } from 'react';

function VoiceRecorder() {
    const [isRecording, setIsRecording] = useState(false);
    const [result, setResult] = useState(null);
    const [mediaRecorder, setMediaRecorder] = useState(null);
    
    const startRecording = async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(stream);
        let chunks = [];
        
        recorder.ondataavailable = (e) => chunks.push(e.data);
        recorder.onstop = async () => {
            const audioBlob = new Blob(chunks, { type: 'audio/wav' });
            await analyzeVoice(audioBlob);
        };
        
        recorder.start();
        setMediaRecorder(recorder);
        setIsRecording(true);
    };
    
    const stopRecording = () => {
        mediaRecorder.stop();
        setIsRecording(false);
    };
    
    const analyzeVoice = async (audioBlob) => {
        const formData = new FormData();
        formData.append('audio_file', audioBlob, 'voice.wav');
        
        try {
            const response = await fetch('http://localhost:5000/api/audio/analyze-direct', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            setResult(data.analysis_result);
        } catch (error) {
            console.error('음성 분석 오류:', error);
        }
    };
    
    return (
        <div>
            <button onClick={isRecording ? stopRecording : startRecording}>
                {isRecording ? '녹음 중지' : '녹음 시작'}
            </button>
            
            {result && (
                <div>
                    <h3>분석 결과</h3>
                    <p>스트레스 레벨: {result.stress_level}/10</p>
                    <p>스트레스 확률: {result.stressed_probability}%</p>
                    <p>신뢰도: {result.confidence}%</p>
                </div>
            )}
        </div>
    );
}
```

### 🎯 **핵심 포인트**
1. **인증 불필요**: 모든 API를 토큰 없이 바로 호출 가능
2. **음성 우선**: 음성 분석이 있으면 스트레스 레벨을 자동 보정
3. **multipart/form-data**: 음성 파일은 FormData로 전송
4. **실시간 녹음**: MediaRecorder API로 브라우저에서 바로 녹음
5. **외부 접속**: 0.0.0.0:5000으로 설정되어 외부에서도 접속 가능

### 📱 **지원되는 음성 형식**
- WAV, MP3, FLAC, M4A, OGG
- 최대 파일 크기: 50MB
- 권장: WAV 형식 (최고 정확도)

## 📋 API 사용 예시 (curl)

### 🔓 **인증 없이 바로 사용 가능!**

### 1. 일일 기록 생성 (인증 불필요)
```bash
curl -X POST http://localhost:5000/api/records/ \
  -H "Content-Type: application/json" \
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

### 2. 음성 파일 분석 (인증 불필요)
```bash
curl -X POST http://localhost:5000/api/audio/analyze-direct \
  -F "audio_file=@/path/to/your/audio.wav"
```

### 3. 음성과 함께 기록 생성 (인증 불필요)
```bash
curl -X POST http://localhost:5000/api/audio/analyze \
  -F "audio_file=@/path/to/your/audio.wav" \
  -F "stress_level=5" \
  -F "mood=normal" \
  -F "energy_level=6" \
  -F "daily_sentence=음성과 함께 기록합니다" \
  -F "save_to_record=true" \
  -F "update_stress_level=true"
```

### 4. 기록 조회 (인증 불필요)
```bash
curl http://localhost:5000/api/records/
```

### 5. 7일 리포트 생성 (인증 불필요)
```bash
curl http://localhost:5000/api/reports/7-day
```

## 🗂️ 프로젝트 구조

```
code/
├── app.py                       # Flask 애플리케이션 메인
├── run.py                       # 애플리케이션 실행 스크립트
├── create_test_user.py          # 🔓 테스트 사용자 생성
├── test_no_auth.py              # 🔓 인증 없이 API 테스트
├── test_api.py                  # API 테스트 스크립트
├── test_audio_analysis.py       # 🎵 오디오 분석 테스트
├── frontend_voice_api.py        # 🎨 프론트엔드 예제 생성기
├── frontend_voice_api_example.js # 🎨 JavaScript API 클래스
├── voice_api_test.html          # 🎨 HTML 테스트 페이지
├── .env                         # 환경 변수
├── .env.example                 # 환경 변수 템플릿
│
├── models/                # 데이터베이스 모델
│   ├── __init__.py
│   ├── user.py           # 사용자 모델
│   ├── daily_record.py   # 일일 기록 모델
│   └── milestone.py      # 마일스톤 모델
│
├── routes/                # API 라우트 (🔓 인증 비활성화됨)
│   ├── __init__.py
│   ├── auth.py           # 인증 관련 (프로필만 활성)
│   ├── records.py        # 기록 관리 (인증 불필요)
│   ├── audio.py          # 🎵 오디오 스트레스 분석 (인증 불필요)
│   ├── rewards.py        # 보상 시스템 (인증 불필요)
│   └── reports.py        # 리포트 생성 (인증 불필요)
│
├── services/              # 비즈니스 로직
│   ├── __init__.py
│   ├── nlp_service.py         # NLP 분석 (참고용)
│   ├── audio_stress_service.py # 🎵 오디오 스트레스 분석 (우선 적용)
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

### 🔓 인증 비활성화 모드 테스트
```bash
# 인증 없이 모든 API 테스트
python3 test_no_auth.py

# 오디오 분석 전체 테스트
python3 test_audio_analysis.py

# 프론트엔드 예제 생성 및 테스트
python3 frontend_voice_api.py
```

### HTML 테스트 페이지
브라우저에서 `voice_api_test.html`을 열면:
- 파일 업로드로 음성 분석
- 실시간 녹음 및 분석
- 일일 기록 생성
- 결과 시각화

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

### 🔓 테스트 계정 (인증 비활성화 모드)
- **모든 API**: user_id=1로 고정
- **Username**: testuser (선택사항)
- **Password**: password123 (선택사항)
- **Email**: test@example.com

### 📁 생성되는 프론트엔드 파일들
```bash
python3 frontend_voice_api.py  # 실행하면 생성됨:
├── frontend_voice_api_example.js  # JavaScript API 클래스
└── voice_api_test.html            # HTML 테스트 페이지
```

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

### 🌐 외부 접속 설정 (이미 구성됨)
서버는 `0.0.0.0:5000`으로 실행되어 **외부에서 접속 가능**합니다:
- **로컬**: http://localhost:5000
- **네트워크**: http://YOUR_SERVER_IP:5000
- **클라우드**: http://your-domain.com:5000

### 방화벽 설정 (필요시)
```bash
# Ubuntu/Debian
sudo ufw allow 5000

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### Docker를 이용한 배포
```dockerfile
# Dockerfile 예시
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY code/ .
EXPOSE 5000

# disable-auth 브랜치용
CMD ["python", "run.py"]
```

### 환경별 설정
- **개발 (disable-auth)**: SQLite, 인증 비활성화, DEBUG=True
- **테스트**: PostgreSQL, 인증 활성화
- **운영**: PostgreSQL, JWT 인증, DEBUG=False, 보안 강화

### 🔄 main 브랜치로 전환 (인증 활성화)
```bash
git checkout main  # JWT 인증이 필요한 정상 버전
```

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